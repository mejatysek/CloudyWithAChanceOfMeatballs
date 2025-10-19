#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import redis
import pickle
from hashids import Hashids

__author__ = 'mejty'


class Store(object):

    def __init__(self, db=4):
        self._redis = redis.StrictRedis(db=db)

    def _prepare_key(self, prefix, key):
        return "cloudy:{prefix}:{key}".format(prefix=prefix, key=key)

    def _add_user_id(self, user_id):
        self._redis.set(self._prepare_key(user_id, "exists"), 1)

    def _add_user_id_message(self, user_id):
        self._redis.set(self._prepare_key(user_id, "message"), 1)

    def show_user_message(self, user_id):
        result = self._redis.exists(self._prepare_key(user_id, "message"))
        if result:
            self._redis.delete(self._prepare_key(user_id, "message"))
        return result

    def get_new_id(self):
        int_id = self._redis.incr(self._prepare_key("app", "id"))
        hashids = Hashids(salt="BMb658SWMXmEqxpOXFwVFpHajuhwpqu7w3+BFfnK", alphabet="0123456789abcdefghijklmnopqrstuvwxyz")
        user_id = hashids.encode(int_id)
        self._add_user_id(user_id)
        self._add_user_id_message(user_id)
        return user_id

    def id_exists(self, user_id):
        return self._redis.exists(self._prepare_key(user_id, "exists"))

    def add_user_city(self, user_id, city):
        self._redis.hset(self._prepare_key(user_id, "cities"), city['id'], pickle.dumps(city, protocol=4))

    def del_user_city(self, user_id, location_key):
        self._redis.hdel(self._prepare_key(user_id, "cities"), location_key)

    def get_user_cities(self, user_id):
        data = self._redis.hgetall(self._prepare_key(user_id, "cities"))
        if data:
            result = {k.decode("utf-8"): pickle.loads(v) for k, v in data.items()}
            return result
        else:
            return {}

    def cache_request(self, method, arguments, data, ex=None):
        key = "{method}:{arguments}".format(method=method, arguments=arguments)
        self._redis.set(self._prepare_key("apirequest", key), pickle.dumps(data, protocol=4), ex=ex)

    def get_cached_request(self, method, arguments):
        key = "{method}:{arguments}".format(method=method, arguments=arguments)
        data = self._redis.get(self._prepare_key("apirequest", key))
        return pickle.loads(data) if data else data

