"""案例库——标签匹配检索。"""
import json
from pathlib import Path


class Precedent:
    def __init__(self, data: dict):
        self.id: str = data["id"]
        self.court: str = data.get("court", "")
        self.title: str = data["title"]
        self.facts: str = data.get("facts", "")
        self.opinion: str = data.get("opinion", "")
        self.result: str = data.get("result", "")
        self.tags: list[str] = data.get("tags", [])


class CaseStore:
    def __init__(self):
        self.precedents: list[Precedent] = []

    def load(self, data_dir: str):
        index_path = Path(data_dir) / "precedents" / "index.json"
        if not index_path.exists():
            return
        with open(index_path, encoding="utf-8") as f:
            cases_data = json.load(f)
        for item in cases_data:
            self.precedents.append(Precedent(item))

    def search(self, tags: list[str], top_k: int = 5) -> list[Precedent]:
        if not tags:
            return self.precedents[:top_k]
        tag_set = set(t.lower() for t in tags)
        scored = []
        for p in self.precedents:
            score = sum(1 for t in p.tags if t.lower() in tag_set)
            if score > 0:
                scored.append((score, p))
        scored.sort(key=lambda x: -x[0])
        return [p for _, p in scored[:top_k]]


case_store = CaseStore()
