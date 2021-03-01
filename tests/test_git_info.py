from requiam.git_info import GitInfo


def test_GitInfo():
    gi = GitInfo()

    assert isinstance(gi.branch, str)

    assert isinstance(gi.commit, str)
    assert isinstance(gi.short_commit, str)
    if not gi.short_commit:  # Empty string
        assert len(gi.short_commit) == 0
    else:
        assert len(gi.short_commit) == 7
