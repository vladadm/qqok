#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

URL = 'http://localhost:10701'
#URL = 'http://rt-srv01b.infra.racktables.amosrv.ru:10701'
HEADER = {'content-type': 'application/json'}

def get_free_external_ip(*args):

    #body = requests.get(URL+'ip_free_pub').json()
    if args:
        print(args)
        print()
        arg = str(*args)
        print(json.dumps(requests.get(URL + f'/ip_free_pub?dc={arg}').json(), indent=4))
    else:
        print(json.dumps(requests.get(URL + "/ip_free_pub").json(), indent=4))

def get_free_ip(*args):
    arg = str(*args)
    req = requests.get(URL + f'/ip_free?dc={arg}').json()
    #req = json.dumps(requests.get(URL + f'/ip_free?dc={arg}').json(), indent=4)
    # for net in req:
    #     print(json.dumps(req[net], indent=4))
    return req

def create_lxd_container(*args):
    print(*args)
    #data = {'command' : 'create'}
    #data.update(dict([tuple(x.split(":")) for x in str(*args).split()]))
    #print(json.dumps())
    post = requests.post(URL + '/hosts', headers=HEADER, data=json.dumps(*args)).json()
    print('RT:', post)

def delete(*args):
    #data = {'command' : 'delete'}
    #print(*args)
    #data.update(dict([tuple(x.split(":")) for x in str(*args).split()]))
    #print(data)
    delete = requests.delete(URL + '/hosts', headers=HEADER, data=json.dumps(*args))
    if delete.status_code != 204:
        print('RT:', delete.json())
        return delete.status_code
        #return delete.status_code

    print('RT:', {'code': 204, 'text': f'Hostname {dict(*args).get("name")} not found'})

def search(*args):
    arg = str(*args)
    req = requests.get(URL + f'/hosts?search={arg}').json()
    for host in req.get('hosts'):
        print(host.get('name'), host.get('ip'))

def rename_lxd_container(*args):
    pass

def hyper_for_host(*args):
    arg = str(*args)
    req = requests.get(URL + f'/hyperv?name={arg}').json()
    return req
