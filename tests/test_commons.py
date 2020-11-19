from requiam import TimerClass
from requiam.commons import figshare_stem

from datetime import datetime, timedelta

prod_stem = 'arizona.edu:dept:LBRY:figshare'
stage_stem = 'arizona.edu:dept:LBRY:figtest'


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


def test_figshare_stem():

    assert figshare_stem(production=False) == stage_stem
    assert figshare_stem(production=True) == prod_stem

    for stem in ['quota', 'portal']:
        assert figshare_stem(stem, production=True) == \
               f"{prod_stem}:{stem}"
        assert figshare_stem(stem, production=False) == \
               f"{stage_stem}:{stem}"

        assert figshare_stem(stem=stem, production=True) == \
               f"{prod_stem}:{stem}"
        assert figshare_stem(stem=stem, production=False) == \
               f"{stage_stem}:{stem}"
