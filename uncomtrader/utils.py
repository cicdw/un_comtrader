import json
from os.path import dirname, join

import uncomtrader


data_path = join(dirname(uncomtrader.__file__), '../data/')

def _get_reporting_codes():
    with open(data_path + "reporterAreas.json", "r") as f:
        data = json.load(f)

    country_codes = {d['text'].lower() : int(d['id']) for d in data['results'] if d['id'] != 'all'}
    country_codes.update({"all" : "all"})
    return country_codes


def _get_partner_codes():
    with open(data_path + "partnerAreas.json", "r") as f:
        data = json.load(f)

    country_codes = {d['text'].lower() : int(d['id']) for d in data['results'] if d['id'] != 'all'}
    country_codes.update({"all" : "all"})
    return country_codes
