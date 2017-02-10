import pandas as pd
import pytest

from uncomtrader import ComtradeRequest, MultiRequest

# whether to skip actual request calls
skip = True

@pytest.mark.parametrize("attr,val", [
    ("partner_area",36),
    ("reporting_area","all"),
    ("time_period",2016),
    ("freq","A"),
    ("fmt","csv"),
    ("hs","44,4401"),
    ("trade_type","C")
])
def test_url_parser(attr, val,
    url="http://comtrade.un.org/api/get?p=36&r=all&ps=2016&px=HS&cc=44,4401&freq=A&type=C&fmt=csv"):
    req = ComtradeRequest(url=url)
    assert getattr(req, attr)==val


@pytest.mark.skipif(skip,
    reason="Prevent using up unecessary requests accidentally.")
def test_simple_request():
    '''Test a simple request.'''
    req = ComtradeRequest(trade_type="C", hs=4401,
            partner_area=36, freq='A',
            reporting_area="all", time_period=2016)

    df = req.pull_data()
    assert df.shape == (3, 22)


@pytest.mark.skipif(skip,
    reason="Prevent using up unecessary requests accidentally.")
def test_simple_multirequest():
    '''Test a multi request.'''
    req = MultiRequest(trade_type="C", hs=4401,
            partner_area=36, freq='A',
            reporting_area="all",
            time_period=[2011,2012,2013,2014,2015,2016])

    df = req.pull_data()
    assert df.shape == (264, 22)


@pytest.mark.skipif(skip,
    reason="Prevent using up unecessary requests accidentally.")
def test_simple_multirequest():
    '''Test a simple (unnecessary) multi request.'''
    req = MultiRequest(trade_type="C", hs=4401,
            partner_area=36, freq='A',
            reporting_area="all", time_period=2016)

    df = req.pull_data()
    assert df.shape == (3, 22)
