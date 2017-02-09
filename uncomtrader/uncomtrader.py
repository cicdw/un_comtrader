from datetime import datetime as dt
from io import StringIO
from os.path import exists

import pandas as pd
import requests


class ComtradeRequest(object):

    def set_defaults(self):
        '''Sets some convenient default values for testing.'''
        self.partner_area = 36
        self.time_period = 2016
        self.reporting_area = 'all'
        self.hs = 44
        self.freq = 'A'
        self.trade_type = 'C'
        self.fmt = 'csv'

    def pull_data(self, save=False):
        self.last_request = dt.now()
        r = requests.get(self._base_url)
        content = r.content.decode('utf-8')
        self.data = pd.read_csv(StringIO(content))

        if save:
            fname = 'australia_comtrade.{}'.format(self.fmt)
            idx = 1
            while exists(fname):
                fname = fname.replace('.', '_v{}.'.format(idx))
                idx += 1

            self.data.to_csv(fname)
            return None

        return self.data
    
    def __init__(self):
        self.base_url = 'http://comtrade.un.org/api/get?'

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, url):
        if url == 'http://comtrade.un.org/api/get?':
            self._base_url = url
        elif '?&' in url:
            self._base_url = url.replace('?&', '?')
        else:
            self._base_url = url

    @property
    def fmt(self):
        return self._fmt

    @fmt.setter
    def fmt(self, val):
        if val not in ['csv', 'json']:
            raise ValueError('Allowable values for trade type are csv and json!')

        self.base_url += '&fmt={}'.format(val)
        self._fmt = val

    @property
    def trade_type(self):
        return self._type

    @trade_type.setter
    def trade_type(self, val):
        try:
            val = val.upper()
        except AttributeError:
            raise ValueError('Allowable values for trade type are C and S!')

        if val not in ['C', 'S']:
            raise ValueError('Allowable values for trade type are C and S!')

        self.base_url += '&type={}'.format(val)
        self._type = val

    @property
    def hs(self):
        return self._cc

    @hs.setter
    def hs(self, val):
        if val != 44:
            raise ValueError("Only allowable value is 44!")

        self._px = 'HS'
        self._cc = val

        self.base_url += '&px=HS&cc={}'.format(val)

    @property
    def partner_area(self):
        return self._p

    @partner_area.setter
    def partner_area(self, val):
        if val != 36:
            raise ValueError("Only allowable value is 36!")

        self._p = val
        self.base_url += '&p={}'.format(val)

    @property
    def time_period(self):
        return self._ps

    @time_period.setter
    def time_period(self, val):
        self._ps = val
        self.base_url += '&ps={}'.format(val)

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, val):
        try:
            val = val.upper()
        except AttributeError:
            raise ValueError('''Allowable frequency values are 'A' and 'M'!''')
        if val not in ['A', 'M']:
            raise ValueError('''Allowable frequency values are 'A' and 'M'!''')

        self._freq = val
        self.base_url += '&freq={}'.format(val)

    @property
    def reporting_area(self):
        return self._r

    @reporting_area.setter
    def reporting_area(self, val):
        self._r = val
        self.base_url += '&r={}'.format(val)

    def __repr__(self):
        out = 'Current Comtrade Request URL: {}'.format(self._base_url)
        return out
