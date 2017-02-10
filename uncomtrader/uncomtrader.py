from datetime import datetime as dt
from io import StringIO
from os.path import dirname, exists, join
from time import sleep

import json
import pandas as pd
import re
import requests
import uncomtrader


class ComtradeURL(object):

    def set_valid_args(self):

        data_path = join(dirname(uncomtrader.__file__), '../data/')
        
        with open(data_path + 'reporterAreas.json', 'r') as data_file:
            valid_r = json.load(data_file)

        with open(data_path + 'partnerAreas.json', 'r') as data_file:
            valid_p = json.load(data_file)

        ## valid reporting areas
        valid_r = [obj['id'] for obj in valid_r['results']]
        valid_r = [int(val) for val in valid_r if val != 'all']
        self.valid_r = valid_r + ['all']

        ## set valid partner areas
        valid_p = [obj['id'] for obj in valid_p['results']]
        valid_p = [int(val) for val in valid_p if val != 'all']
        self.valid_p = valid_p + ['all']

    def __init__(self, url=None):
        if url:
            self.base_url = url
        else:
            self.base_url = 'http://comtrade.un.org/api/get?'

        self.set_valid_args()

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
            raise ValueError('''Allowable values for trade type are 'csv' and 'json'!''')

        if hasattr(self, '_fmt'):
            self.base_url = re.sub('fmt=csv', 'fmt={}'.format(val),
                                    self.base_url)
            self.base_url = re.sub('fmt=json', 'fmt={}'.format(val),
                                    self.base_url)
        else:
            self.base_url += '&fmt={}'.format(val)

        self._fmt = val

    @property
    def trade_type(self):
        return self._type

    @trade_type.setter
    def trade_type(self, val):
        try:
            val = val.upper()
        except AttributeError as err:
            raise ValueError('''Allowable values for trade type are 'C' and 'S'!''')

        if val not in ['C', 'S']:
            raise ValueError('''Allowable values for trade type are 'C' and 'S'!''')

        if hasattr(self, '_type'):
            self.base_url = re.sub('type=[A-Z]', 'type={}'.format(val),
                                    self.base_url)
        else:
            self.base_url += '&type={}'.format(val)

        self._type = val

    @property
    def hs(self):
        return self._cc

    @hs.setter
    def hs(self, val):

        if isinstance(val, list):
            val = ','.join(map(str, val))
            if len(val) > 20:
                raise ValueError("Too many HS codes provided; limit is 20.")

        if hasattr(self, '_px'):
            self.base_url = re.sub('cc=(\d+,?)+', 'cc={}'.format(val), 
                                self.base_url)
        else:
            self.base_url += '&px=HS&cc={}'.format(val)

        self._px = 'HS'
        self._cc = val

    @property
    def partner_area(self):
        return self._p

    @partner_area.setter
    def partner_area(self, val):

        if isinstance(self, list):
            for obj in val:
                if obj not in self.valid_p:
                    raise ValueError('Invalid value given!')

            val = ','.join(map(str, val))
        else:
            if val not in self.valid_p:
                raise ValueError('Invalid value given!')

        if hasattr(self, '_p'):
            self.base_url = re.sub('p=(\d+,?)+', 'p={}'.format(val),
                                    self.base_url)
            self.base_url = re.sub('p=all', 'p={}'.format(val),
                                    self.base_url)
        else:
            self.base_url += '&p={}'.format(val)

        self._p = val

    @property
    def time_period(self):
        return self._ps

    @time_period.setter
    def time_period(self, val):

        if isinstance(val, list):
            val = ','.join(map(str, val))
            if len(val) > 5:
                raise ValueError("Too many time periods provided; limit is 5.")

        if hasattr(self, '_ps'):
            self.base_url = re.sub('ps=(\d+,?)+', 'ps={}'.format(val),
                                    self.base_url)
        else:
            self.base_url += '&ps={}'.format(val)

        self._ps = val

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

        if hasattr(self, '_freq'):
            self.base_url = re.sub('freq=[A-Z]', 'freq={}'.format(val), 
                                self.base_url)
        else:
            self.base_url += '&freq={}'.format(val)

        self._freq = val

    @property
    def reporting_area(self):
        return self._r

    @reporting_area.setter
    def reporting_area(self, val):

        if isinstance(self, list):
            for obj in val:
                if obj not in self.valid_r:
                    raise ValueError('Invalid value given!')

            val = ','.join(map(str, val))
        else:
            if val not in self.valid_r:
                raise ValueError('Invalid value given!')
       
        if hasattr(self, '_r'):
            self.base_url = re.sub('r=(\d+,?)+', 'r={}'.format(val),
                                    self.base_url)
            self.base_url = re.sub('r=all', 'r={}'.format(val),
                                    self.base_url)
        else:
            self.base_url += '&r={}'.format(val)

        self._r = val

    def __repr__(self):
        out = 'Current Comtrade Request URL: {}'.format(self._base_url)
        return out


class ComtradeRequest(ComtradeURL):
    '''Creates URL request for UN Comtrade data.

    Inputs:
        partner_area : Partner Area
        reporting_area : Reporting Area
        time_period : Time Period
        hs : Classification Code
        freq : Data Frequency
        trade_type : Trade Type
    '''

    @classmethod
    def from_file(cls, fpath):
        with open(fpath, 'r') as req_path:
            args = json.load(req_path)

        return cls(**args)

    def set_defaults(self):
        '''Sets some convenient default values for testing.'''
        self.partner_area = 36
        self.time_period = 2016
        self.reporting_area = 'all'
        self.hs = 44
        self.freq = 'A'
        self.trade_type = 'C'
        self.fmt = 'csv'

    def pull_data(self, save=False, **kwargs):

        if hasattr(self, 'last_request'):
            now = dt.now()
            time_elapsed = (now - self.last_request).total_seconds()
            if time_elapsed < 1:
               sleep(1)

        if self.n_reqs >= 100:
            raise ValueError("Too many requests have been made! Take a break.")

        self.last_request = dt.now()
        r = requests.get(self._base_url)
        self.n_reqs += 1
        content = r.content.decode('utf-8')
        
        if "No data matches your query" in content:
            raise IOError("No data matches your query or your query is too complex!")

        if self.fmt == 'csv':
            self.data = pd.read_csv(StringIO(content))
        if self.fmt == 'json':
            self.data = pd.read_json(StringIO(content))

        self.data = self.data.dropna(axis=1, how='all')

        if save:
            fname = save
            idx = 1
            while exists(fname):
                fname = fname.replace('.', '_v{}.'.format(idx))
                idx += 1

            if self.fmt == 'csv':
                self.data.to_csv(fname, index=False, **kwargs)
            if self.fmt == 'json':
                self.data.to_json(fname, index=False, **kwargs)

            return None

        return self.data
    
    def __init__(self, partner_area=None, reporting_area=None,
        time_period=None, hs=None, freq=None, trade_type=None):
        self.base_url = 'http://comtrade.un.org/api/get?'
        self.n_reqs = 0
        self.set_valid_args()

        if partner_area:
            self.partner_area = partner_area
        if reporting_area:
            self.reporting_area = reporting_area
        if time_period:
            self.time_period = time_period
        if hs:
            self.hs = hs
        if freq:
            self.freq = freq
        if trade_type:
            self.trade_type = trade_type

        self.fmt = 'csv'

    def __repr__(self):
        out = 'Current Comtrade Request URL: {}'.format(self._base_url)
        return out
