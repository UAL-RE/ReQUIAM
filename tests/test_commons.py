from requiam import TimerClass
from datetime import datetime, timedelta


def test_TimerClass():

    tc = TimerClass()

    assert tc.start == 0
    assert tc.stop == 0
    assert tc.delta == 0
    assert tc.format == ""

    # Test each methods
    tc._start()
    tc._stop()

    assert isinstance(tc.start, datetime)
    assert isinstance(tc.stop, datetime)
    assert isinstance(tc.delta, timedelta)
    assert isinstance(tc.format, str)
