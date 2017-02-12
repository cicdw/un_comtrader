from datetime import datetime as dt
from io import StringIO
from os.path import dirname, exists, join
from pandas.parser import CParserError
from time import sleep
from .utils import _get_reporting_codes, _get_partner_codes

import json
import pandas as pd
import re
import requests
import uncomtrader


reporting_codes = _get_reporting_codes()
partner_codes = _get_partner_codes()
trade_flow_codes = {"import" : 1, "export" : 2,
                    "re-export" : 3, "re-import" : 4,
                    "all" : "all"}

def _set_attr(obj, pattern, attr, url, dig=True):
    '''Sets class attributes based on searching for 'pattern' in 'url'.

    Inputs:
        obj (class) : Class for which attribute will be set
        pattern (string) : regular expression to search for in `url`
        attr (string) : attribute to be set in `obj`
        url (string) : URL to search

    Output:
        None
    '''

    pat = re.compile(pattern)
    match = pat.search(url)
    if match:
        find = match.group()
        find = find.split('=')[1]

        if len(find.split(',')) > 1:
            try:
                find = list(map(int, find.split(',')))
            except ValueError:
                find = find.split(',')
            setattr(obj, attr, find)
        elif find=='all':
            setattr(obj, attr, 'all')
        else:
            try:
                setattr(obj, attr, int(find))
            except ValueError:
                setattr(obj, attr, find)


class ComtradeURL(object):
    '''Class for manipulating and constructing valid UN Comtrade API URLs.

    Inputs (all optional):
        partner_area : The area(s) receiving the trade
        reporting_area : The area(s) that reported the trade to UNSD
        time_period : Time period(s) for data
        hs : a commodity code (or list of) from the Harmonized System
        freq : data frequency ('A' for annual or 'M' for monthly)
        trade_type : Type of trades to pull ('C' for commodities, 'S' for services)
        trade_flow : Type of trade flow (one of 'Import', 'Export', 're-Import', 're-Export')
        url : URL to construct request from
        fmt : 'csv' or 'json', format to store data in
    '''

    def _parse_url(self, url):
        for pattern, attr in [
            ('p=(\d+,?)+|p=all', 'partner_area'),
            ('r=(\d+,?)+|r=all', 'reporting_area'),
            ('ps=(\d+,?)+', 'time_period'),
            ('cc=(\d+,?)+', 'hs'),
            ('freq=A|freq=M', 'freq'), ('rg=\d+|rg=all', 'rg'),
            ('type=C|type=S', 'trade_type'),
            ('fmt=csv|fmt=json', 'fmt')]:

            _set_attr(self, pattern, attr, url)

    def set_valid_args(self):
        '''Defines what values are valid for various attributes.'''

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

    def from_url(self, url):
        '''Creates ComtradeURL from a given base URL.'''
        self.base_url = url
        self._parse_url(url)
        return self

    def __init__(self, partner_area=None, reporting_area=None,
        time_period=None, hs=None, freq=None, trade_type=None,
        trade_flow=None, url=None, fmt='csv'):

        self.set_valid_args()
        if url:
            self.from_url(url)
        else:
            self.base_url = 'http://comtrade.un.org/api/get?'
            self.fmt = fmt

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
        if trade_flow:
            self.trade_flow = trade_flow

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
    def trade_flow(self):
        return self._rg

    @trade_flow.setter
    def trade_flow(self, val):
        val = val.lower()

        if val not in trade_flow_codes.keys():
            raise ValueError('''Invalid trade flow provided!''')

        code = trade_flow_codes[val]
        if hasattr(self, '_rg'):
            self.base_url = re.sub('rg=\d+|rg=all', 'rg={}'.format(code),
                                    self.base_url)
        else:
            self.base_url += '&rg={}'.format(code)

        self._type = code

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
            if len(val) > 20:
                raise ValueError("Too many HS codes provided; limit is 20.")
            val = ','.join(map(str, val))

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

        if isinstance(val, str):
            val = partner_codes[val.lower()]

        if isinstance(val, list):
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
            if len(val) > 5:
                raise ValueError("Too many time periods provided; limit is 5.")
            val = ','.join(map(str, val))

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

        if isinstance(val, str):
            val = reporting_codes[val.lower()]

        if isinstance(val, list):
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
    '''Class for creating valid UN Comtrade data requests.

    Inputs (all optional):
        partner_area : The area(s) receiving the trade
        reporting_area : The area(s) that reported the trade to UNSD
        time_period : Time period(s) for data
        hs : a commodity code (or list of) from the Harmonized System
        freq : data frequency ('A' for annual or 'M' for monthly)
        trade_type : Type of trades to pull ('C' for commodities, 'S' for services)
        url : URL to construct request from
        fmt : 'csv' or 'json', format to store data in
    '''

    @classmethod
    def from_file(cls, fpath):
        '''Creates ComtradeRequest from a .json file.

        Inputs (required):
            fpath (string): location of .json file; for an example, see data/requests.json
                    in this repository.
        Output:
            ComtradeRequest instance.
        '''

        with open(fpath, 'r') as req_path:
            args = json.load(req_path)

        return cls(**args)

    def pull_data(self, save=False, **kwargs):
        '''
        Actually queries the UN Comtrade Database to gather requested data,
        taking into account usage limits.

        Inputs (optional):
            save (string) : desired location to save data
            **kwargs : keyword arguments passed to pandas save function
        '''

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

        try:
            if self.fmt == 'csv':
                self.data = pd.read_csv(StringIO(content))
            if self.fmt == 'json':
                raw = json.loads(r.text)
                data = json.dumps(raw['dataset'])
                self.data = pd.read_json(data)
        except CParserError as err:
            raise IOError("Data Usage Limit exceeded! Try again in an hour.") from err

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

    def __init__(self, **kwargs):

        super(ComtradeRequest, self).__init__(**kwargs)
        self.n_reqs = 0

    def __repr__(self):
        out = 'Current Comtrade Request URL: {}'.format(self._base_url)
        return out


class MultiRequest(object):
    '''
    Class for creating valid UN Comtrade data requests which exceed
    data field limits.

    Inputs (all optional):
        partner_area : The area(s) receiving the trade
        reporting_area : The area(s) that reported the trade to UNSD
        time_period : Time period(s) for data
        hs : a commodity code (or list of) from the Harmonized System
        freq : data frequency ('A' for annual or 'M' for monthly)
        trade_type : Type of trades to pull ('C' for commodities, 'S' for services)
        url : URL to construct request from
        fmt : 'csv' or 'json', format to store data in
    '''

    @classmethod
    def from_file(cls, fpath):
        '''Creates MultiRequest from a .json file.

        Inputs (required):
            fpath (string): location of .json file; for an example, see data/requests.json
                    in this repository.
        Output:
            MultiRequest instance.
        '''

        with open(fpath, 'r') as req_path:
            args = json.load(req_path)

        return cls(**args)

    def _partition(self, val, max_len):
        res = []

        if not isinstance(val, list):
            return [val]

        if len(val) > max_len:
            while len(val) > max_len:
                res.append(val[:max_len])
                val = val[max_len:]

        if len(val) > 0:
            res.append(val)

        return res

    def pull_data(self, verbose=True, save=False, **kwargs):
        '''
        Actually queries the UN Comtrade Database to gather requested data,
        taking into account usage limits.

        Inputs (optional):
            verbose (boolean) : whether to print current request
            save (string) : desired location to save data
            **kwargs : keyword arguments passed to pandas save function
        '''

        reqs_left = self.reqs
        req = reqs_left.pop()
        base_req = ComtradeRequest(url=req.base_url)

        if verbose:
            print('Pulling request {}'.format(base_req.base_url))
        df = base_req.pull_data()

        while len(reqs_left) > 0:
            new_req = reqs_left.pop()
            # maintains state to prevent too many requests
            req = base_req.from_url(new_req.base_url)

            if verbose:
                print('Pulling request {}'.format(base_req.base_url))

            df = pd.concat([df, base_req.pull_data()])

        self.data = df

        if save:
            df.to_csv(save, index=False)
            return None
        else:
            return df


    def __init__(self, hs=[], time_period=[], **kwargs):
        self.hs = self._partition(hs, 20)
        self.time_period = self._partition(time_period, 5)
        self.reqs = []

        for hs_val in self.hs:
            for ts_val in self.time_period:
                self.reqs.append(ComtradeURL(hs=hs_val, time_period=ts_val, **kwargs))

        self.nrequests = len(self.reqs)
        if self.nrequests > 100:
            raise ValueError("Over 100 requests generated!  Shorten your inputs.")

    def __repr__(self):
        out = 'MultiRequest storing {0} individual Comtrade Requests'.format(self.nrequests)
        return out
