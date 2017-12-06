#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from pathlib import Path
__author__ = 'mejty'

for i in range(1, 43):
    url = url = "https://vortex.accuweather.com/adc2010/images/slate/icons/{num:0>2}.svg".format(num=i)
    image_data = requests.get(url)
    if (image_data.ok):
        name = url.split("/")[-1]
        with open(Path("icons/", name), "wb") as iconfile:
            iconfile.write(image_data.content)
