#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

__author__ = 'mejty'


class Credentials(object):

    def __init__(self):
        with Path("credentials.json").open() as credential:
            data = json.loads(credential.read())
            self.maps_key = data['maps']
