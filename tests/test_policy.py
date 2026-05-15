from policy import should_fetch


def test_editor_is_blocked():
    assert should_fetch(
        "statistics",
        "inprogress",
        123,
        True,
    ) is False


def test_continuous_endpoint():
    assert should_fetch(
        "statistics",
        "finished",
        None,
        False,
    ) is True


def test_prematch_allowed():
    assert should_fetch(
        "lineups",
        "notstarted",
        None,
        False,
    ) is True


def test_prematch_blocked_live():
    assert should_fetch(
        "lineups",
        "inprogress",
        None,
        False,
    ) is False


def test_live_only_allowed():
    assert should_fetch(
        "graph",
        "inprogress",
        None,
        False,
    ) is True


def test_live_only_blocked_finished():
    assert should_fetch(
        "graph",
        "finished",
        None,
        False,
    ) is False


def test_postmatch_allowed():
    assert should_fetch(
        "player-statistics",
        "finished",
        None,
        False,
    ) is True


def test_postmatch_blocked_prematch():
    assert should_fetch(
        "player-statistics",
        "notstarted",
        None,
        False,
    ) is False


def test_unknown_endpoint_allowed():
    assert should_fetch(
        "unknown-endpoint",
        "finished",
        None,
        False,
    ) is True


def test_detail_id_none_not_blocked():
    assert should_fetch(
        "statistics",
        "inprogress",
        None,
        False,
    ) is True