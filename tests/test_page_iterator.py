from ishtaran.pagination.page_iterator import paginate


def test_iterates_across_multiple_pages_never_fetching_all_at_once() -> None:
    all_items = list(range(25))
    fetch_calls: list[int] = []

    def fetch_page(skip: int, take: int) -> list[int]:
        fetch_calls.append(skip)
        return all_items[skip : skip + take]

    collected = list(paginate(10, fetch_page))
    assert collected == all_items
    assert fetch_calls == [0, 10, 20]


def test_empty_result_never_fetches_more_than_one_page() -> None:
    fetch_calls: list[int] = []

    def fetch_page(skip: int, take: int) -> list[int]:
        fetch_calls.append(skip)
        return []

    assert list(paginate(10, fetch_page)) == []
    assert len(fetch_calls) == 1


def test_exact_page_size_boundary_fetches_one_extra_empty_page_then_stops() -> None:
    all_items = list(range(10))
    fetch_calls: list[int] = []

    def fetch_page(skip: int, take: int) -> list[int]:
        fetch_calls.append(skip)
        return all_items[skip : skip + take]

    assert list(paginate(10, fetch_page)) == all_items
    assert fetch_calls == [0, 10]
