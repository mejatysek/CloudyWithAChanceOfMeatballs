#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from sortedcontainers import SortedDict

import requests
import json

from store import Store

__author__ = 'mejty'


class WeatherApi(object):

    def __init__(self, store, credentials):
        self._store = store
        self._api_key = credentials.api_key
        self.url = "http://dataservice.accuweather.com/{method}"
        self.logger = logging.getLogger(__name__)

    def _stringify_chars(self, **kwargs):
        dictionary = SortedDict(kwargs)
        result = []
        for k, v in dictionary.items():
            result.append("{k}={v}".format(k=k, v=v))
        return "&".join(result)

    def _make_request(self, method, ex, **kwargs):
        url = self.url.format(method=method)
        argumnets = self._stringify_chars(**kwargs)
        cached = self._store.get_cached_acu(method, argumnets)
        if cached:
            self.logger.debug("cached")
            return cached
        kwargs['apikey'] = self._api_key
        result = requests.get(url, kwargs)
        result.raise_for_status()
        result = result.json()
        self._store.cache_acu(method, argumnets, result, ex)
        return result

    def search_city(self, query, language_code="cs"):
        method = "locations/v1/cities/autocomplete"
        return self._make_request(method, None, q=query, language=language_code)

    def get_city(self, location_key, language_code="cs"):
        method = "locations/v1/{location_key}".format(location_key=location_key)
        return self._make_request(method, None, language=language_code)

    def get_5_day_forecast(self, location_key, metric=True, language_code="cs"):
        method = "forecasts/v1/daily/5day/{location_key}".format(location_key=location_key)
        return self._make_request(method, ex=60 * 60 * 4, metric=metric, language=language_code)


if __name__=="__main__":
    api = WeatherApi(Store())
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    data = api.search_city("Chomu")
    print(data)
    city = api.get_city(data[0]["Key"])
    print(city)
    forecast = api.get_5_day_forecast(data[0]["Key"])
    print(forecast)
    a = {"b":"a", "a":"b", "c":"c"}
    a = SortedDict(a)
    print(a)
    print(dict(**a))
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
