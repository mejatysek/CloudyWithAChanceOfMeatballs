#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from pathlib import Path

import requests
import json

from store import Store

__author__ = 'mejty'


class WeatherApi(object):

    WMO_TO_ACCUWEATHER_ICON = {
    0: 1,   # Clear sky -> Sunny
    1: 2,   # Mainly clear -> Mostly Sunny
    2: 4,   # Partly cloudy -> Intermittent Clouds
    3: 7,   # Overcast -> Cloudy
    45: 11, # Fog -> Fog
    48: 11, # Depositing rime fog -> Fog
    51: 12, # Drizzle, light -> Showers
    53: 12, # Drizzle, moderate -> Showers
    55: 12, # Drizzle, dense -> Showers
    56: 25, # Freezing Drizzle, light -> Sleet
    57: 25, # Freezing Drizzle, dense -> Sleet
    61: 18, # Rain, slight -> Rain
    63: 18, # Rain, moderate -> Rain
    65: 18, # Rain, heavy -> Rain
    66: 26, # Freezing Rain, light -> Freezing Rain
    67: 26, # Freezing Rain, heavy -> Freezing Rain
    71: 22, # Snow fall, slight -> Snow
    73: 22, # Snow fall, moderate -> Snow
    75: 22, # Snow fall, heavy -> Snow
    77: 19, # Snow grains -> Flurries
    80: 12, # Rain showers, slight -> Showers
    81: 12, # Rain showers, moderate -> Showers
    82: 12, # Rain showers, violent -> Showers
    85: 23, # Snow showers, slight -> Mostly Cloudy w/ Snow
    86: 23, # Snow showers, heavy -> Mostly Cloudy w/ Snow
    95: 15, # Thunderstorm -> T-Storms
    96: 15, # Thunderstorm with hail, slight -> T-Storms
    99: 15, # Thunderstorm with hail, heavy -> T-Storms
    }

    def __init__(self, store):
        self._store = store
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.geocoding_get_url = "https://geocoding-api.open-meteo.com/v1/get"
        self.logger = logging.getLogger(__name__)

    def _make_request(self, url, ex, **kwargs):
        argumnets = json.dumps(kwargs, sort_keys=True)
        cached = self._store.get_cached_request(url, argumnets)
        if cached:
            self.logger.debug("cached")
            return cached
        result = requests.get(url, params=kwargs)
        result.raise_for_status()
        result = result.json()
        self._store.cache_request(url, argumnets, result, ex)
        return result

    def search_city(self, query, language_code="cs"):
        return self._make_request(self.geocoding_url, None, name=query, language=language_code)

    def get_city_by_id(self, city_id, language_code="cs"):
        return self._make_request(self.geocoding_get_url, None, id=city_id, language=language_code)

    def get_day_forecast(self, latitude, longitude):
        result = self._make_request(self.url, ex=60 * 60 * 4, latitude=latitude, longitude=longitude, daily="weathercode,temperature_2m_max,temperature_2m_min", forecast_days="1", timezone="auto")
        result['daily']['weathercode'] = [self.WMO_TO_ACCUWEATHER_ICON.get(code, 1) for code in result['daily']['weathercode']] 
        return result


if __name__=="__main__":
    api = WeatherApi(Store())
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    data = api.search_city("Chomutov")
    print(data)
    forecast = api.get_5_day_forecast(data["results"][0]["latitude"], data["results"][0]["longitude"])
    print(forecast)
