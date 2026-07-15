from app.legal_engine.law_store import LawStore


def test_law_store_load_and_search():
    store = LawStore()
    store.load("app/legal_engine/data")
    assert len(store.articles) > 0

    results = store.search(["拖欠工资", "克扣"])
    assert len(results) > 0
    # 劳动法第50条应该在结果中
    ids = [r.id for r in results]
    assert "labor_law_50" in ids


def test_law_store_search_no_keyword():
    store = LawStore()
    store.load("app/legal_engine/data")
    results = store.search([])
    assert len(results) <= 10
