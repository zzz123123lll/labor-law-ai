"""法律条文内存搜索引擎。启动时加载所有 YAML 文件，建立倒排索引。"""
from pathlib import Path

import yaml


class LawArticle:
    def __init__(self, data: dict):
        self.id: str = data["id"]
        self.law: str = data["law"]
        self.article: str = data["article"]
        self.content: str = data["content"]
        self.tags: list[str] = data.get("tags", [])
        self.applicable_scenarios: list[str] = data.get("applicable_scenarios", [])


class LawStore:
    """法律库单例。"""

    def __init__(self):
        self.articles: list[LawArticle] = []
        self._keyword_index: dict[str, list[int]] = {}  # 关键词 → 文章索引列表

    def load(self, data_dir: str):
        """加载 data_dir 下所有 .yaml 文件。"""
        yaml_files = list(Path(data_dir).rglob("*.yaml"))
        for yf in yaml_files:
            with open(yf, encoding="utf-8") as f:
                articles_data = yaml.safe_load(f) or []
            for item in articles_data:
                article = LawArticle(item)
                idx = len(self.articles)
                self.articles.append(article)
                # 建立关键词索引
                for tag in article.tags:
                    tag_lower = tag.lower()
                    self._keyword_index.setdefault(tag_lower, []).append(idx)
                # 内容分词索引（简单版：按中文分词）
                for word in self._tokenize(article.content + article.article):
                    self._keyword_index.setdefault(word, []).append(idx)

    def search(self, keywords: list[str], top_k: int = 10) -> list[LawArticle]:
        """根据关键词搜索相关法条，按匹配度排序。"""
        if not keywords:
            return self.articles[:top_k]

        scores: dict[int, int] = {}
        for kw in keywords:
            kw_lower = kw.lower()
            for word in self._tokenize(kw):
                for idx in self._keyword_index.get(word, []):
                    scores[idx] = scores.get(idx, 0) + 1
            # 精确 tag 匹配加分
            for idx in self._keyword_index.get(kw_lower, []):
                scores[idx] = scores.get(idx, 0) + 3

        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return [self.articles[i] for i, _ in ranked[:top_k]]

    def _tokenize(self, text: str) -> list[str]:
        """简单中文分词：按 2-gram 切分。"""
        cleaned = text.replace("\n", "").replace(" ", "")
        if not cleaned:
            return []
        # 2-gram
        grams = [cleaned[i:i+2] for i in range(len(cleaned)-1)]
        # 完整短语
        grams.append(cleaned[:10])
        return list(set(grams))


# 全局单例
law_store = LawStore()
