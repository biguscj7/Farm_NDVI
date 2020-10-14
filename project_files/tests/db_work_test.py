import pytest

def test_filename_to_dt():
    assert filename_to_dt('Messy_20200531.csv') == '20200531'

