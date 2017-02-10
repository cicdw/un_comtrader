import pandas as pd
import pytest

from uncomtrader import ComtradeRequest, MultiRequest

def test_simple_request():
    '''Test a simple request.'''
    req = ComtradeRequest(trade_type="C", hs=4401,
            partner_area=36, freq='A',
            reporting_area="all", time_period=2016)

    df = req.pull_data()
    assert df.shape == (3, 22)


def test_simple_multirequest():
    '''Test a multi request.'''
    req = MultiRequest(trade_type="C", hs=4401,
            partner_area=36, freq='A',
            reporting_area="all",
            time_period=[2011,2012,2013,2014,2015,2016])

    df = req.pull_data()
    assert df.shape == (264, 22)

def test_simple_multirequest():
    '''Test a simple (unnecessary) multi request.'''
    req = MultiRequest(trade_type="C", hs=4401,
            partner_area=36, freq='A',
            reporting_area="all", time_period=2016)

    df = req.pull_data()
    assert df.shape == (3, 22)
