import pytest

from scripts.test_panelite.utils import MaxRetriesExceeded, Retrier


def test_retrier_no_exception():
    retrier = Retrier(retries=3)
    while not retrier.accomplished:
        with retrier:
            pass

    assert retrier.retries==0

def test_retrier_exception():
    retrier = Retrier(retries=2, delay=0)
    with pytest.raises(MaxRetriesExceeded):
        while not retrier.accomplished:
            with retrier:
                raise ValueError

    assert retrier.retries==2
