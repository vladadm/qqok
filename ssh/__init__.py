#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import multiprocessing
import multiprocessing.queues
import setproctitle
import subprocess
from termcolor import colored
import sys
from qqok.cache import cache



FORBIDDEN_CMD = ["shutdown ",
                 "reboot ",
                 "init ",
                 "rm "]


def expand(name):
    """Returns [host] host [host1,host2,...] list"""
    buf = []
    if name.startswith('%'):
        name = name.lstrip('%')
        if ' ' in name:
            name = name.split(' ')
        spl = name.split('@', 1)
        hostgroup = spl[0]
        dc_filter = spl[1] if len(spl) > 1 else False
        for _group in cache.groups:
            if _group.get("name") != hostgroup:
                continue
            else:
                # for group in _group.get(hostgroup):
                #     print(group)
                for item in cache.hosts:
                    if item.get("group", None) != hostgroup:
                        continue
                    elif dc_filter and item['dc'] != dc_filter:
                        continue
                    else:
                        print(item)
                        buf.append(item)
                        if len(buf) == 0:
                            print('Error')

        # for item in cache.hosts:
        #     if item['group'] != hostgroup:
        #         continue
        #     elif dc_filter and item['dc'] != dc_filter:
        #         continue
        #     else:
        #         buf.append(item)
    else:
        buf.append({'host': name})
    print("Expand buf: {}".format(buf))
    return buf


def expand_hosts(hosts):
    hosts_buf = []
    ignore = []
    for item in hosts.split(' '):
        print('Ex h:', hosts)
        if item.startswith('-'):
            ignore += expand(item[1:])
        else:
            hosts_buf += expand(item)
    hosts = [x['host'] for x in hosts_buf if x not in ignore]
    print("Expand Host: {}".format(len(hosts)))
    return hosts

def expand_groups(groups):
    groups_buf = []
    ignore = []
    for item in groups.split():
        if item.startswith('-'):
            ignore += expand(item[1:])
        else:
            groups_buf += expand(item)
    hosts = [x['host'] for x in groups_buf if x not in ignore]
    return hosts

def name_validator(name):
    if '@' in name:
        name = name.split('@')[0]

    if name.startswith('%') and ' ' in name:
        names = name.replace('%', '').split(' ')
        mask = []
        for name in names:
            for _group in cache.groups:
                if _group.get("name") == name.lstrip('%'):
                    mask.append(0)
        #print(mask)
        if len(names) == len(mask):
            return 0
    if name.startswith('%'):
        #print(1)
        for _group in cache.groups:
            if _group.get("name") == name.lstrip('%'):
                return 0
    else:
        for _host in cache.hosts:
            #print(_host)
            if _host['host'] == name:
                return 0


def cmd_validator(cmd):
    if len([x for x in FORBIDDEN_CMD if x in cmd]) > 0 and '/tmp' not in cmd:
        return 1

##########

def ssh(*args):
    """ Interactive ssh client (ssh %core-stage-front)"""
    if not args[0]:
        print("usage: ssh host [ %hostgroup ...]")
        return
    # if name_validator(args[0]) != 0:
    #     print('Incorrected host or group name')
    #     return
    hosts = expand_hosts(args[0])
    for host in hosts:
        p = subprocess.Popen('ssh -A %s' % host, shell=True, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        p.communicate()

def do_exec(*args):
    """run <command> on hosts in a non-parallel mode"""
    p_exec(*args, pool_size_limit=1)

def p_exec(*args, pool_size_limit=50):
    """run <command>
    Execute this command on all hosts in the list in parallel mode"""
    err = '"usage: p_exec host [ %hostgroup ...] -- <command>'
    if not args[0]:
        print(err)
        return
    spl = args[0].split(' -- ', 1)
    # hosts, cmd = spl
    print('p_exec Spl:', spl)
    try:
        hosts, cmd = spl
    except:
        print(err)
        return
    if name_validator(hosts) != 0:
        print('Incorrected host or group name')
        return
    if cmd_validator(cmd) == 1:
        print('Forbidden command')
        return
    print('Host:', hosts, 'cmd', cmd)
    if not spl or len(spl) < 1:
        print("usage: %s host [ %hostgroup ...] -- <command>")
        return
    hosts = expand_hosts(hosts)
    map_args = []
    for host in hosts:
        map_args.append((host, spl[1]))
    pool_size = min(pool_size_limit, len(map_args))
    with multiprocessing.Pool(pool_size) as pool:
        pool.starmap(ssh_exec, map_args)
        pool.close()

def ssh_exec(host, command):
    setproctitle.setproctitle('xgun exec on ' + host)
    try:
        process = subprocess.Popen(['ssh', '-A', host, command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline, ""):
            if not line:
                break
            print('%s %s' % (colored('%s: ' % host, 'green'), line.decode('utf8').rstrip()))
    except Exception as e:
        sys.stderr.write('%s: %s\n' % (host, e))


def p_puppet(*args, pool_size_limit=50):
    """run <command>
    Execute puppet agent --test on all hosts in the list in parallel mode"""
    hosts = args[0]
    hosts = expand_hosts(hosts)
    map_args = []
    for host in hosts:
        map_args.append((host, 'sudo puppet agent --test'))
    pool_size = min(pool_size_limit, len(map_args))
    with multiprocessing.Pool(pool_size) as pool:
        pool.starmap(ssh_exec, map_args)
        pool.close()


def ssh1(*args):
    """ Interactive ssh client (ssh %core-stage-front)"""
    spl = args[0].raw.split(None, 1)[1:]
    print("SPL:", spl)
    if not spl or len(spl) < 1:
        print("usage: ssh1 host/(host*) [cmd]")
        return
    items = spl[0].split(' ')
    print("Items", items)
    if len(items) > 1:
        name = items[0]
        cmd = ' '.join(items[1:])
        print("CMD", cmd)
    else:
        name = items[0]
        cmd = ''
        print("Not found CMD:", cmd)
    if '*' in name:
        obj_items = name.split('*')
        print('Obj_Items:', obj_items)
        right_item = obj_items[0]
        left_item = obj_items[1]
        print("RItem", right_item)
        line = 'LItem ' + left_item
        print("Line", line)
        hosts = [x.get("host") for x in cache.hosts
                 if x.get("host").startswith(right_item)
                 and x.get("host").endswith(left_item)]
        print("Hosts:", hosts)
        multiproc_ssh_connect(hosts, cmd)
        return
    elif name.startswith('%'):  # также добавить условие для исключения
        group = name.split('%')[1].rstrip()
        print('Select group:', group)
        group_buf = []
        for i in cache.groups:
            if list(*i.items())[0] == group:
                group_buf.extend(list(*i.items())[1])
        print('Groups:', group_buf)
        host_buf = [x['host'] for x in cache.hosts if x['group'] in group_buf]
        host_buf.sort()
        print(host_buf)
        multiproc_ssh_connect(host_buf, cmd,)
        return
    elif ',' in name:
        items = spl[0].split(',')
        hosts_buf = []
        ignore = []
        for item in items:
            print(item)
            hosts_buf.append(item)

        hosts = [x for x in hosts_buf if x not in ignore]
        cmd = '' if len(spl) == 1 else '"%s"' % spl[1]
        print('Hosts:',hosts, 'cmd:', cmd)
        for host in hosts:
            p = subprocess.Popen('ssh -A %s %s' % (host, cmd), shell=True, stdin=sys.stdin, stdout=sys.stdout,
                                 stderr=sys.stderr)
            p.communicate()
        return

    if not cmd:
        print('Connect to single host')
        ssh_connect(name, cmd, )
    else:
        multiproc_ssh_connect(name, cmd, pool_size_limit=1)


def ssh_connect(host, cmd=''):
    if not cmd:
        p = subprocess.Popen('ssh -A %s \'%s\'' % (host, cmd), shell=True, stdin=sys.stdin, stdout=sys.stdout,
                             stderr=sys.stderr)
        p.communicate()
    else:
         p = subprocess.Popen('ssh -A %s %s' % (host, cmd), shell=True, stdin=sys.stdin, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
         out, err = p.communicate()
         print('%s return empty output' % colored(host, 'cyan'))
         if out:
             for i in out.strip().decode("utf-8").split("\n"):
                 print('%s: %s' % (colored(host, 'green'), i))
         if err:
             print('%s: %s' % (colored(host, 'green'), colored(str(err.strip().decode("utf-8")), 'red')))
    return

def multiproc_ssh_connect(hosts, cmd='', pool_size_limit=50):
    print('Pool_size_limit', pool_size_limit)
    map_args = []
    print('Hosts:', hosts, 'Type:', type(hosts))
    if isinstance(hosts, (list,)):
        for host in hosts:
            map_args.append((host, cmd))
    else:
        map_args.append((hosts, cmd))
    print('Map', map_args)
    pool_size = min(pool_size_limit, len(map_args))
    with multiprocessing.Pool(pool_size) as pool:
        pool.starmap(ssh_exec, map_args)
        pool.close()

