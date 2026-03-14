from bot.classes import FetchError, WebData


def test_fetch_error_stores_info():
    err = FetchError("connection timeout")
    assert err.info == "connection timeout"


def test_fetch_error_is_exception():
    assert isinstance(FetchError("x"), Exception)


def test_web_data_stores_fields():
    wd = WebData(joraa="j", alra="a", base="b", portal="p", alra_ids="ids")
    assert wd.joraa == "j"
    assert wd.alra == "a"
    assert wd.base == "b"
    assert wd.portal == "p"
    assert wd.alra_ids == "ids"
