#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import requests
import json
import yaml
from time import time
from time import strftime
from multiprocessing.pool import ThreadPool




class Auth(object):
    def __init__(self):
        self.pwd = "/".join(__file__.split("/")[:-2])+"/"
        self.config_file = 'config.yml'
        self.keys = self.load()
#
    def load(self):
        print(self.pwd)
        try:
            with open(self.pwd + self.config_file, 'r') as file:
                return":".join(yaml.safe_load(file.read()).get("foreman").values())
        except Exception as exc:
            print("Failed read config file", str(exc))


def get_item(item, limit=""):
    url = {"new": 'foreman.at.ivi.ru',
           "stage": 'foreman.staging.ivi.ru'}
    try:
        url = 'http://' + Auth().keys + '@' + url.get("stage")
        print(url)
    except Exception as exc:
        print("Exception:", str(exc))
        return

    # if not limit:
    #     limit = "?per_page=10"

    if limit:
        limit = "?per_page=" + str(limit)
    uris = {
        "hostgroups": "/api/hostgroups" + limit,
        "hosts": "/api/hosts" + limit,
        #"hosts_for_group": "/api/hostgroups/22/hosts",
        #"environments": "/api/environments",
        #"domains": "/api/domains",
        #"locations": "/api/locations",
        #"roles": "/api/roles"
    }

    try:
        if item == "all_items":

            #groups_url =
            #hosts_url = url + uris.get("hosts")
            # Получаем хедеры объектов
            item_definition_urls = [url + uris.get(x) for x in uris]
            print("{get_items} Obj urls:\n", item_definition_urls)
            request = multi_get(item_definition_urls)
            #print(request)
            #groups = []
            #_urls = []
            # Конструируем список урлов
            # urls_for_multi = [list(*url_maker(x)) for x in request]
            urls_for_multi = []
            for headers in request:
                headers = list(headers)
                headers[0] = url + uris.get(headers[0])
                print("Heders", headers)
                urls_for_multi.extend(url_maker(*headers))

            # for ii in request:
            #
            #     if ii[0] == "hostgroups":
            #         _urls.extend(url_maker(groups_url, ii[1], ii[2]))
            #     if ii[0] == "hosts":
            #         _urls.extend(url_maker(hosts_url, ii[1], ii[2]))
            print("Final urls:", urls_for_multi)
            try:
                _request = multi_get(urls_for_multi, )
            except Exception as exc:
                print("{Get_Items} Exception:", str(exc))
            groups = []
            hosts = []
            # [req_batch.append(x) for x in _request]
            for data in _request:
                if data[0] == "hostgroups":
                    for d in data[1]:
                        groups.append(d)
                if data[0] == "hosts":
                    for d in data[1]:
                        hosts.append(d)
            print("{Get_Items} Groups len:", len(groups))
            print("{Get_Items} Hosts len:", len(hosts))
            return [ groups, hosts ]
            #print(request)

        if not uris.get(item, None):
            raise Exception("URI not found")
        start_t = time()
        request = requests.get(url_stg + uri.get(item)).json()
        print(strftime('[ %H:%m:%S ]'), f"{item} pages req duration: {time() - start_t}")
        req_batch = request.get("results")
        #req_batch = []
        pages = round(request.get("total")/request.get("per_page")+0.5)+1
        print(strftime('[ %H:%m:%S ]'), f"{item} pages: {pages}")
        urls = [str((url_stg + uri.get(item) + f"&page={x}")) for x in range(2, pages)]
        for uu in urls:
            print(uu)
        _request = self.multi_get(urls,)
        groups = []
        hosts = []
        #[req_batch.append(x) for x in _request]
        for data in _request:
            if data[0] == "hostgroups":
                for d in data[1]:
                    groups.append(d)
        # for data in _request:
        #     req_batch.extend(data)
        #print(req_batch)
        # for uu in urls:
        #     print(uu)
        #for page in range(2, pages):
            #print(strftime('[ %H:%m:%S ]'), f"{item} page: {page}")
            #start_t = time()
            # try:
            #     req = requests.get(url_stg + uri.get(item) + f"&page={page}").json()
            # except Exception as exc:
            #     print(strftime('[%H:%m:%S]'), str(exc))
            # print(strftime('[ %H:%m:%S ]'), f"{item} {page}/{pages} req duration: {time() - start_t}")
            # req_batch.extend(req.get("results"))
    except Exception as exc:
        print("Exception: "+str(exc))
        return
    #return req.get("results")
    #return req_batch
    return groups

def url_maker(url, per_page, total_pages):
    try:
        pages = round(total_pages / per_page + 0.5) + 1
        print(pages)
        urls = [url + f"?page={x}&per_page={per_page}" for x in range(1, pages)]
        print("{URL Maker} Out:", urls)
    except Exception as exc:
        print("{URL Maker} Exception:", str(exc))
        return
    return urls

def multi_get(urls):
    pool = ThreadPool(len(urls))
    print("Pool:", len(urls))
    procs = []
    for url in urls:
        procs.append(pool.apply_async(req, args=(url,)))
    try:
        pool.close()
        pool.join()
        result = [x.get() for x in procs]
        print(len(result))
        print(len(result[0]))
        #print("Result", result[0])
        return result
    except Exception as exc:
        print("{Processor} Exception:", str(exc))
    #return [r.get() for r in procs]


def req(url):
    try:
        headers = {"Content-Type": "application/json"}
        start_timer = time()
        item = str(*re.findall(r'(hostgroups|hosts)', url))
        #print(url)
        print("{req}: ", item)
        request = requests.get(url) #headers=headers)
        if "page=" not in url:
            # print(request.json())
            return item, request.json().get("per_page"), request.json().get("total")
        print(strftime('[ %H:%m:%S ]'), f"{url}: {time() - start_timer}")
        if request.status_code != 200:
            raise Exception(f"url: {url} response: {request.status_code}")
        return item, request.json().get("results")
    except Exception as exc:
        print(f"Exception in {__name__}", str(exc))
        return

# def write_raw(data):
#     with open("forem_hg.json", "w") as fd:
#         fd.write(json.dumps(data, indent=4))
