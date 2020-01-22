#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from qqok.api.forman import get_item as get_forman_items
from qqok.api.zabbix import zabbix_api
from collections import ChainMap
from multiprocessing.pool import ThreadPool
from time import time
import yaml
from time import strftime


class Cache:
    """
    Local Cache
    """
    def __init__(self):
        self.local_cache = '/tmp/.qqok.cache.json'
        self.hosts = []
        self.zabbix_hosts = []
        self.groups = []
        self.grp = []
        self.env = []
        self.dc = []
        self.read_local_cache()
        # self.groups_hierarchy = []

    def read_local_cache(self):
        if not os.path.exists(self.local_cache):
            print("Local cache not found, run <reload>")
            return
        try:
            with open(self.local_cache, 'r') as fd:
                buf = json.loads(fd.read())
        except Exception as exc:
            print('Read cache file error:', str(exc))
            return
        if not buf:
            print('Cache file empty...')
            self.update_items()
            return

        print(
            'local cache:\n'
            'Groups: {}\n'
            'Hosts: {}'.format(
                            len(buf.get('groups')),
                            len(buf.get('hosts')),
            )
        )
        setattr(self, 'groups', [])
        setattr(self, 'hosts', [])
        setattr(self, 'env', [])
        setattr(self, 'dc', [])
        setattr(self, 'location', [])
        # setattr(self, 'dc_literals', [])

        self.hosts.extend(buf.get('hosts'))
        self.groups.extend(buf.get('groups'))
    #
    def write_cache(self, items):   # save_cache
        try:
            with open(self.local_cache, 'w') as fd:
                fd.write(json.dumps(items, indent=4))
            print('Cache file update.')
        except:
            print('Fail file update. {}')
    #
    def update_zabbix_items(self, *args, data_source=""):
        """
        Получает из форемана словари с объектами
        парсит и складывает в кэш.
        """
        try:
            timer_start = time()
            setattr(self, 'zabbix_hosts', [x for x in zabbix_api.hosts()])
            print(
                "[ {} {} ] ZABBIX: {} \n".format(strftime('%H:%m:%S'), strftime('%s')[0:3], str(time() - timer_start)[0:4])
            )
        except Exception as exc:
            raise Exception(str(exc))
        return
    #
    def update_items(self, *args, data_source=""):
        """
        Получает из форемана словари с объектами
        парсит и складывает в кэш.
        """
        arg = str(*args)
        # self.hosts= []
        # self.groups = []
        start = time()
        item = {
            "all": "all_items",
            "groups": "hostgroups",
            "hosts": "hosts",
                }.get(arg, None)
        print("Arg:", arg)
        print(item)
        try:
            if not arg:
                raise Exception("Incorrect item {}".format(arg))
            print("Arg:", arg)
            result = get_forman_items(item)
        except Exception as exc:
            print("Failed request items: {}".format(str(exc)))
            return

        if arg == "all":

            setattr(self, 'groups', [])
            for group in result[0]:
                self.groups.append(
                    {"id": group.get("id"),
                     "name": group.get('name'),
                     "env": group.get("environment_name"),
                     "title": group.get("title"),
                     "domain_name": group.get("domain_name"),
                     "parent": group.get("parent_name")}
                )

            setattr(self, 'hosts', [])
            for host in result[1]:
                self.hosts.append(
                    {
                        "host": host.get("name"),
                        "ip": host.get("ip"),
                        "group": host.get("hostgroup_name"),
                        "group_title": host.get("hostgroup_title"),
                        "model_name": host.get("model_name"),
                        "location_name": host.get("location_name"),
                        "compute_resource_name": host.get("compute_resource_name"),
                        "id": host.get("id"),
                        "uuid": host.get("uuid"),
                        "domain_name": host.get("domain_name"),
                        "last_report": host.get("last_report"),
                     }
                )

            cache_items = {'groups': self.groups, 'hosts': self.hosts, }

        if arg == "groups":

            setattr(self, 'groups', [])
            for group in result[0]:
                self.groups.append(
                    {"id": group.get("id"),
                     "name": group.get('name'),
                     "env": group.get("environment_name"),
                     "title": group.get("title"),
                     "domain_name": group.get("domain_name"),
                     "parent": group.get("parent_name")}
                )
            cache_items = {'groups': self.groups, 'hosts': self.hosts, }

        self.write_cache(cache_items)


cache = Cache()


def executor(data=""):
    items = ['hostgroups', 'hosts']
    if data == 'all':
        items = items
    elif not data or data not in items:
        raise ValueError(f" func{__name__}: Incorrect item,\nCorrect:  {items}")
    else:
        items = [data]
    pool = ThreadPool(len(items))
    results = []
    # print(func)
    for item in items:
        results.append(pool.apply_async(get_forman_items, args=(item, )))
    pool.close()
    pool.join()
    return [r.get() for r in results]
