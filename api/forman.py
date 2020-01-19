# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для работы с foreman api
"""

import re
from time import time, strftime
from multiprocessing.pool import ThreadPool
import yaml
import requests


class Form(object):
    def __init__(self):
        settings = self.load()
        url = {"new": 'foreman.at.ivi.ru',
               "stage": 'foreman.staging.ivi.ru'}
        self.user = settings['user']
        self.pw = settings['password']
        self.env = settings['environment']
        self.url = "http://{}:{}@{}".format(
            self.user,
            self.pw,
            url.get(self.env),
        )

    @staticmethod
    def load():
        config_file = 'config.yaml'
        config_path = "/".join(__file__.split("/")[:-2]) + "/"
        try:
            with open(config_path + config_file, 'r') as file:
                return yaml.safe_load(file.read()).get("foreman")
        except Exception as exc:
            print("Exc in read config file", exc)
            return


def get_item(item, limit=""):
    """

    """
    # Проверка URL
    try:
        url = Form().url
        print('[ {} {} ] Form URL: {}'.format(strftime('%H:%m:%S'), strftime('%s')[0:3], url))
        req(url)
    except Exception as exc:
        print(__name__, "Exc:", str(exc))
        return
    # if not limit:
    #     limit = "?per_page=10"
    if limit:
        limit = "?per_page=" + str(limit)
    uris = {
        "hostgroups": "/api/hostgroups" + limit,
        "hosts": "/api/hosts" + limit,
        # "hosts_for_group": "/api/hostgroups/22/hosts",
        # "environments": "/api/environments",
        # "domains": "/api/domains",
        # "locations": "/api/locations",
        # "roles": "/api/roles"
    }
    start_timer = time()
    try:
        if item == "all_items":
            # Получаем хедеры объектов
            item_definition_urls = [url + uris.get(x) for x in uris]
            print(
                # "[ {} {} ] HEADERS FOR: {}".format(
                "[ {} {} ] URI: {} \nURLS:{}".format(
                    strftime('%H:%m:%S'),
                    strftime('%s')[0:3],
                    # "\n".join(item_definition_urls)
                    [uris.get(x)for x in uris],
                    item_definition_urls
                )
            )
            # Получаем кол-во объектов, и кол-во на страницу
            request = multi_get(item_definition_urls)
            urls_for_multi = []
            for headers in request:
                headers = list(headers)
                headers[0] = url + uris.get(headers[0])
                # print("Heders", headers)
                urls_for_multi.extend(url_maker(*headers))
            print(
                "[ {} {} ] FINAL URLS: {}".format(
                    strftime('%H:%m:%S'),
                    strftime('%s')[0:3],
                    urls_for_multi,
                )
            )
            try:
                _request = multi_get(urls_for_multi, )
            except Exception as exc:
                print("{Get_Items} Exception:", str(exc))
            # groups = [ x[1] for x in _request if x[0] == "hostgroups"]
            groups = []
            hosts = []
            for data in _request:
                if data[0] == "hostgroups":
                    for d in data[1]:
                        groups.append(d)
                if data[0] == "hosts":
                    for d in data[1]:
                        hosts.append(d)
            print("Execute time: ", str(time() - start_timer))
            print("Groups len:", len(groups))
            print("Hosts len:", len(hosts))
            return [groups, hosts]

        if not uris.get(item, None):
            raise Exception("URI not found")

        print("item:", item)
        item_definition_urls = [url + uris.get(item)]
        print(
            # "[ {} {} ] HEADERS FOR: {}".format(
            "[ {} {} ] URI: {} \n".format(
                strftime('%H:%m:%S'),
                strftime('%s')[0:3],
                # "\n".join(item_definition_urls)
                item_definition_urls
                #[uris.get(x) for x in uris],

            )
        )
        request = multi_get(item_definition_urls)
        urls_for_multi = []
        for headers in request:
            headers = list(headers)
            headers[0] = url + uris.get(headers[0])
            # print("Heders", headers)
            urls_for_multi.extend(url_maker(*headers))
        print(
            "[ {} {} ] FINAL URLS: {}".format(
                strftime('%H:%m:%S'),
                strftime('%s')[0:3],
                urls_for_multi,
            )
        )
        try:
            _request = multi_get(urls_for_multi, )
        except Exception as exc:
            print("{Get_Items} Exception:", str(exc))
        # groups = [ x[1] for x in _request if x[0] == "hostgroups"]
        print("II:", item)
        #print(_request)
        groups = []
        for data in _request:
            if data[0] == item:
                for d in data[1]:
                    groups.append(d)
        print("Execute time: ", str(time() - start_timer))
        print("{} len: {}".format(item, len(groups)))
        return [groups]
    except Exception as exc:
        print("ERROR: GetException: "+str(exc))
        return


def url_maker(url, per_page, total_pages):
    """
    Функция примает:
    :url:
    Функция возвращает:
    список урлов
    """
    try:
        pages = round(total_pages / per_page + 0.5) + 1
        #print(pages)
        urls = [url + f"?page={x}&per_page={per_page}" for x in range(1, pages)]
        print(
            "[ {} {} ] URL MK: {}".format(
                strftime('%H:%m:%S'),
                strftime('%s')[0:3],
                urls,
            )
        )
    except Exception as exc:
        print("{URL Maker} Exception:", str(exc))
        return
    return urls

def multi_get(urls):
    pool = ThreadPool(len(urls))
    print(
        #"[ {} {} ] POOL: {}\n{}".format(
        "[ {} {} ] POOL: {}".format(
            strftime('%H:%m:%S'),
            strftime('%s')[0:3],
            #len(urls),
            urls,
        )
    )
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


def req(url):
    """
    Функция request
    :url
    """
    # headers = {"Content-Type": "application/json"}
    # start_timer = time()
    item = str(*re.findall(r'(hostgroups|hosts)', url))
    print(
        "[ {} {} ] REQ: {}".format(
            strftime('%H:%m:%S'),
            strftime('%s')[0:3],
            url,
        )
    )
    start_timer = time()
    try:
        request = requests.get(url)
        if not item:
            return
    except Exception as exc:
        raise Exception("ERROR: URL {} not available".format(url))
    if request.status_code != 200:
        raise Exception(f"url: {url} response: {request.status_code}")

    if "page=" not in url:
        # print(request.json())
        resp = request.json()
        print(
            "[ {} {} ] {}: {}".format(
                strftime('%H:%m:%S'),
                strftime('%s')[0:3],
                str(time() - start_timer)[0:4],
                url,
            )
        )
        keys = ["per_page", "total"]

        return item, resp.get("per_page"), resp.get("total")
    print(
        "[ {} {} ] {}: {}".format(
            strftime('%H:%m:%S'),
            strftime('%s')[0:3],
            str(time() - start_timer)[0:4],
            url,
        )
    )
    return item, request.json().get("results")

# def write_raw(data):
#     with open("forem_hg.json", "w") as fd:
#         fd.write(json.dumps(data, indent=4))
