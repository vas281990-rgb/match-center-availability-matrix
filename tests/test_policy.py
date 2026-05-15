from policy import should_fetch


def test_editor_is_blocked():
    assert should_fetch(
        "statistics",
        "inprogress",
        123,
        True,
    ) is False

def test_editor_blocked_for_all_statuses():
    for status in ["notstarted", "inprogress", "finished"]:
        assert should_fetch("lineups", status, None, True) is False

def test_continuous_endpoint():
    assert should_fetch(
        "statistics",
        "finished",
        None,
        False,
    ) is True

def test_continuous_available_all_statuses():
    for status in ["notstarted", "inprogress", "finished"]:
        assert should_fetch("statistics", status, None, False) is True

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

def test_prematch_blocked_finished():
    assert should_fetch("lineups", "finished", None, False) is False

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

def test_live_only_blocked_notstarted():
    assert should_fetch("graph", "notstarted", None, False) is False

def test_postmatch_allowed():
    assert should_fetch("player-statistics", "finished", 123, False) is True


def test_postmatch_blocked_prematch():
    assert should_fetch(
        "player-statistics",
        "notstarted",
        None,
        False,
    ) is False

def test_player_statistics_available_inprogress():
    assert should_fetch("player-statistics", "inprogress", 123, False) is True

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

def test_momentum_requires_detail_id():
    assert should_fetch("momentum", "inprogress", None, False) is False

def test_momentum_with_detail_id():
    assert should_fetch("momentum", "inprogress", 123, False) is True

def test_player_statistics_requires_detail_id():
    assert should_fetch("player-statistics", "finished", None, False) is False

def test_player_statistics_with_detail_id():
    assert should_fetch("player-statistics", "finished", 456, False) is True