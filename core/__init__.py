#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CORE



import sys
import os
from qqok.cache import cache
from qqok.cache import executor
import qqok.ssh as ssh
import cmd2
import qqok.racktables as rt
#from xgun.garage import portal
import re
import json
from termcolor import colored


import gnureadline
gnureadline.parse_and_bind('tab:complete')

class Cli(cmd2.Cmd):
    def __init__(self):
        shortcuts = dict(self.DEFAULT_SHORTCUTS)
        shortcuts.update({
            'r': 'reload',
            'u': 'update',
            'gg': 'groups',
            'q': 'quit',
            'fe': 'free_ip',
            '.': 'ssh1'
        })
        super().__init__(shortcuts=shortcuts)
        #super().__init__(shortcuts=shortcuts, allow_cli_args = False, allow_redirection = False )
        #self.allow_redirection = False
        self.prompt = "=> "
        self.intro = "Hello \n I know 'help'"
        self.doc_header = "'help _command_')"
        self.histfile = os.path.expanduser('~/.xgun_history')
        self.cmd_history_file = '/tmp/.xgun/cmd_history'
        self.histfile_size = 1000
        self.update_exec_completions()

    def cmdloop(self, *args, **kwargs):
        try:
            super().cmdloop(*args, **kwargs)
        except KeyboardInterrupt:
            kwargs.update({'intro': False})
            print()
            self.cmdloop(*args, **kwargs)

    def preloop(self):
        if gnureadline and os.path.exists(self.histfile):
            gnureadline.read_history_file(self.histfile)

    def postloop(self):
        if gnureadline:
            gnureadline.set_history_length(self.histfile_size)
            gnureadline.write_history_file(self.histfile)


########## Complition ####### Также нужно вынести в cache

    def update_exec_completions(self, *args, item=""):
        hosts = [x['host'] for x in cache.hosts]
        if item == "hosts":
            setattr(self, 'exec_completions', hosts)
            return
        #groups = ['%%%s' % x.get("name") for x in cache.groups]
        groups = []
        for group in cache.groups:
            if not group.get("parent"):
                groups.append("%" + group.get("name"))
            else:
                groups.append("%{}/{}".format(group.get("parent"), group.get("name")))
        setattr(self, 'exec_completions', hosts + groups)

    def get_exec_completions(self, ignore=[]):
        exec_completions = getattr(self, 'exec_completions')
        return [x for x in exec_completions if x not in ignore]

    def complete_exec(self, text, line, begidx, endidx):
        line = reversed(line[begidx:endidx])
        buf = []
        for b in line:
            if b == ' ':
                break
            buf.append(b)
        return self.find_similar_host_or_group(''.join(reversed(buf)))

    def complete_exec_right(self, text, line, begidx, endidx):
        """
        Функуия разбиениея строки на блоки и определение какой блок коплитить по табу
        example: ssh1 mapi * ivi.ru
        """
        #print("\n", line)
        #line = reversed(line[begidx:endidx])
        line = line[begidx:endidx]
        #print("\n", line)
        buf = []
        for b in line:
            if b == ' ':
                break
            buf.append(b)
        #print(buf)
        receive = ''.join(buf)
        print(receive)
        if '*' in receive:
            obj_items = receive.split('*')
            print('Obj_Items:', obj_items)
            right_item = obj_items[0]
            left_items = [x.get("host") for x in cache.hosts if x.startswith(right_item)]
            print(left_items)
            left_item = obj_items[1]
            len_left = len(left_item)+1
            return left_items

            #print("RItem", right_item)
            line = 'LItem ' + left_item
            #print("Line", line)
            #return self.find_items_for_line()
        return self.find_similar_host_or_group(''.join(buf))

    def find_items_for_line(self, item):
        buf = []
        for item in self.get_exec_completions():
            if item.startswith(item):
                buf.append(item)
        return buf

    def find_similar_host_or_group(self, name):
        buf = []
        for item in self.get_exec_completions():
            if item.startswith(name):
                buf.append(item)
        return buf

    def find_dc(self, name):
        dc = ['selectel', 'serversru', 'serverscom']
        buf = []
        for item in dc:
            if item.startswith(name):
                buf.append(item)
        return buf
    def auto_complete(self, text, line, begidx, endidx):
        line = reversed(line[begidx:endidx])
        buf = []
        for b in line:
            if b == ' ':
                break
            buf.append(b)
        return self.find_dc(''.join(reversed(buf)))

    complete_p_exec = complete_exec
    complete_ssh = complete_exec
    # complete_ssh1 = complete_exec_right
    complete_ssh1 = complete_exec
    complete_puppet_agent_test = complete_exec
    complete_p_puppet_agent_test = complete_exec
    complete_delete = complete_exec
    complete_p_puppet = complete_exec
    complete_free_ip_ext = auto_complete
    complete_free_ip = auto_complete

######### Commands
    def do_hosts(self, *args):
        """show loaded hosts"""
        for item in cache.hosts:
            print(item)

    def do_groups(self, *args):
        """show loaded groups"""
        for item in cache.groups:
            print(item)

    def do_grp(self, *args):
        print(cache.groups)

    def do_reload(self, *args):
        """
        # Должно обновлять полностью кэш
        # метод
        """
        print(*args)
        arg = str(*args)
        try:
            if arg == "zbx":
                cache.update_zabbix_items()
                self.update_exec_completions()
                return
            if not arg:
                cache.update_items('all')
            else:
                cache.update_items(arg)
            #print(f'Cache size: {sys.getsizeof(cache)}b')
        except Exception as exc:
            print("ERROR: {} {}".format(__name__, str(exc)))
            return
            #print("Error in {}:".format(__name__), str(exc))
        self.update_exec_completions()
    do_update = update_exec_completions

    def do_save_cache(self, *args):
        cache.write_cache()

    def do_ssh(self, *args):
        """Test autocomplit"""
        ssh.ssh(*args)

    def do_ssh1(self, *args):
        """Test autocomplit"""
        ssh.ssh1(*args)
        #cache.update_items('hosts')

    def do_p_exec(self, *args, **kwargs):
        """Parallel execution command or commands on hosts\nExample: p_exec %group_name -- hostname"""
        ssh.p_exec(*args, pool_size_limit=50)

    def do_exec(self, *args):
        """run <command> on hosts in a non-parallel mode"""
        ssh.p_exec(*args, pool_size_limit=1)

    def do_p_puppet(self, *args):
        ssh.p_puppet(*args, pool_size_limit=50)


    def default(self, line):
        print("Command not found")


    def default_unpuck(self):
        print('unpuck')

    def do_describe(self, *args):
        """Show info about hosts, hostgroups"""
        #for i in args:
        #    print(i)
        #dd = dict(str(args)[11:-3])
        #print(dd)
        spl = args[0]
        if not spl:
            print("usage: %s host [ %hostgroup ...]") # % args.command)
            return
        print(colored("=== Describe ===", 'yellow'))
        print('SPL:', spl)
        if spl.startswith('%'):
            print("Group:", spl.startswith('%'))
            #dc_filter = spl[1] if len(spl) > 1 else False
            group_name = spl.split('@')[0][1:]
            # DataCenter delimetr
            if '@' in spl:
                group_name = spl.split('@')[0][1:]
                dc = spl.split('@')[1]
                print(group_name, dc)
                for group in cache.groups:
                    # print(group)
                    if group_name in str(*group.keys()) and len(list(*group.values())) > 0:
                        for gg in list(*group.values()):
                            print(f'== {gg}:')
                            for host in cache.hosts:
                                if host['group'] == gg and host['dc'] == dc:
                                    print(host)
                                    # print(f'- {host["host"]}\n-- {host["group"]}\n-- {host["env"]}\n-- {host["dc"]}')
                    elif group_name == str(*group.keys()) and len(list(*group.values())) == 0:
                        print(str(*group.keys()), list(*group.values()))
                        for host in cache.hosts:
                            if host['group'] != group_name:
                                continue
                            elif host['group'] == group_name and host["dc"] == dc:
                                # print(f'- {host["host"]}\n-- {host["group"]}\n-- {host["env"]}\n-- {host["dc"]}')
                                print(host)
                return
            print(colored('Group name: {}'.format(group_name), 'yellow'))
            print("==", set([x.get("name") for x in cache.groups if x.get("name") == group_name]))
            for host in cache.hosts:
                if group_name.endswith("*") and not "/" in group_name:
                    if host.get("group_title") and host.get("group_title").startswith(group_name[:-1]):
                        print(f'+ {host.get("host")}')
                else:
                    if host.get("group_title") == group_name:
                        print(f'+ {host.get("host")}')
            #print("-", *[x.get("host") for x in cache.hosts if x.get("group") == group_name])
            # for group in cache.groups:
            #     if group.get("name") == group_name:
            #         print(f'== {group.get("name")}:')
                # print(group)
                # if group_name == str(*group.keys()) and len(list(*group.values())) > 0:
                #     for gg in list(*group.values()):
                #         print(f'== {gg}:')
                #         for host in cache.hosts:
                #             if host['group'] == gg:
                #                 print(host)
                #                 # print(f'- {host["host"]}\n-- {host["group"]}\n-- {host["env"]}\n-- {host["dc"]}')
                # elif group_name == str(*group.keys()) and len(list(*group.values())) == 0:
                #     print(str(*group.keys()), list(*group.values()))
                #     for host in cache.hosts:
                #         if host['group'] != group_name:
                #             continue
                #         elif host['group'] == group_name:
                #             #print(f'- {host["host"]}\n-- {host["group"]}\n-- {host["env"]}\n-- {host["dc"]}')
                #             print(host)

            # return

                # else:
                #     #group_name in str(*group.keys()) == 0
                #     for host in cache.hosts:
                #         if host['group'] != group_name:
                #             continue
                #         else: #host['group'] == group_name:
                #             #print(f'- {host["host"]}\n-- {host["group"]}\n-- {host["env"]}\n-- {host["dc"]}')
                #             print(host)

                    #print(str(*group.keys()), list(*group.values()))
                    #if str(*group.keys())
                    # for host in cache.hosts:
                    #     if host['group'] == group_name:
                    #         print(host)
                    #print(group)
        for item in cache.hosts:
            if item['host'] in spl:
                print(item)
    complete_describe = complete_exec

    def do_quit(self, *args):
        """exit from xgun"""
        return True

    def do_save(self, *args):
        cache.save_cache()

    def emptyline(self):
        pass

    def do_free_ip_ext(self, *args):
        rt.get_free_external_ip(*args)
    def do_free_ip(self, *args):
        print(json.dumps(rt.get_free_ip(*args), indent=4))
    def do_create_lxd_container(self, *args):
        ''' format name:hostname ip:ip'''
        rt.create_lxd_container(*args)
    #
    #
#     def do_lxd(self, *args):
#         ''' format name: hostname'''
#
#         args = str(*args)
#         dic = { 'delete' : lambda x ,y: x + y }
#         if args.startswith('delet'):
#             print('command:'+ args)
#             rt.delete_lxd_container('command:'+ args)
#         elif args.startswith('create'):
#             print('command:' + args)
#             rt.create_lxd_container('command:'+ args)
#         else:
#             print('help')
#     #
#     #
#     #============================== Create command =========================================================
#     def do_create(self, *args):
#         items = ['name:', 'eth0:', 'eth1:']
#         type = ['lxd', 'container', 'server']
#         _types = ['host', 'group', 'network']
#         args = str(*args)
#         if args.startswith('%'):
#             '''Create group in Garage'''
#             group_name = args.split('%')[1]
#             print('GRP_name', group_name)
#             data = {"name":group_name, "description": "", "dialog": "", "_embedded":{"groups":[]}}
#             portal.create_group(**data)
#             cache.update_items('hosts')
#             return
#         #if args.startswith('host'):
#         ''' Create host'''
#         #args = *args
#         dns = 'amosrv.ru'
#         ####################
#         print("parce")
#         payload = {}
#         dc_id = ''.join(re.findall(r'-.*\d\d(\w)', args))
#         system = ''.join(re.findall(r'^\w+', args))
#         env = ''.join(re.findall(r'\W.*\W(.*$)', args))
#         app = ''.join(re.findall(r'[-](\D*)', args))
#         #dc = cache.dc_literals.get(dc_id)
#         dc = str(*[list(x.values())[0] for x in cache.dc if x.get('literal') == dc_id])
#         print(dc)
#
#         group = input('input group: ')
#         #if group None:
#
#         print({'name': f'{args}.{system}.{dns}',
#                'dc': dc_id,
#                'sys': system,
#                'env': env,
#                'app': app,})
#     # ===== Garage Information Sysytem =====
#         #
#         # Exemple json data:
#         #
#         # {
#         #     "name": "mail-sphinx-shard9-srv01a.prod.mail.amosrv.ru",
#         #     "datacenter": "selectel",
#         #     "environment": "production",
#         #     "group": "mail-production-sphinx",
#         #     "description": "xgun create datetime, user"
#         # }
#         #
#         print({'name': f'{args}.{system}.{dns}'})
#         payload.update({'name': f'{args}.{system}.{dns}'})
#         if dc:
#             print({'datacenter': dc})
#             payload.update({'datacenter': dc})
#         else:
#             print('incorected dc')
#             return
#         if env == 'prod':
#             env = 'production'
#         #print({'environment': env})
#         payload.update({'environment': env})
#         #pp = {y: x for x, y in cache.groups_dic.items()}
#         if [ x for x in cache.groups if group in x.keys()]:
#             print({'group': group.strip()})
#             payload.update({'group': group.strip()})
#         else:
#             print('incorected group')
#             return
#         payload.update({'description': "create from xgun"})
#         payload = {'name': f'{args}.{system}.{dns}',
#                    'description': "create from xgun",
#                    'datacenter_uuid': str(*[ list(x.keys())[0] for x in cache.dc if list(x.values())[0] == dc ]),
#                    'environment_uuid': str(*[str(*x.keys()) for x in cache.env if str(*x.values()) == env]),
#                    'group_uuid': str(*[str(*x.keys()) for x in cache.grp if str(*x.values()) == group])}
#
#         print('====== OUTPUT ====>\n',json.dumps(payload, indent=4))
#         #portal.add_host(**payload)
#         if input('[n/y] ') == 'y':
#             portal.add_host(**payload)
#     # ===== Racktables Information System =====
#         #
#         # Exemple json data
#         # ( minimal )
#         #{
#         #  "name" : "mail-sphinx-shard9-srv01a.prod.mail.amosrv.ru",
#         #  "eth0" : "10.13.2.247",
#         # }
#         # (container)
#         # {
#         #  "name" : "mail-sphinx-shard9-srv01a.prod.mail.amosrv.ru",
#         #  "type" : "lxd-container",
#         #  "hypervisor"  : "lxd-host0036a.infra.lxd.amosrv.ru",
#         #  "eth0" : "10.13.2.247",
#         #  "eth1" : "89.122.77.101"
#         #  }
#         # (hypervisor)
#         #  {
#         #   "name" : "lxd-host0077.infra.lxd.amosrv.ru",
#         #   "type" : "lxd-hypervisor",
#         #   "eth0" : "10.13.2.247",
#         #   "eth1" : "89.122.77.101"
#         #   }
#         # (server)
#         #  {
#         #   "name" : "lxd-host0077.infra.lxd.amosrv.ru",
#         #   "type" : "server",
#         #   "eth0" : "10.13.2.247",
#         #   "eth1" : "89.122.77.101"
#         #   }
#         #
#         payload = {}
#         payload.update({'name': f'{args}.{system}.{dns}'})
#         hyper = input('Hyper ?: ')
#         if hyper and hyper.startswith('0'):
#             # ПРоверка существует-ли хост
#             payload.update({'hypervisor': f'lxd-host{hyper}.infra.lxd.amosrv.ru'})
#
#
#         #payload.update({'datacenter': dc})
#         #eth0_ip = {'eth0': rt.get_free_ip(dc)['internal'][f'{dc} internal']['free'][-1]}
#         ### ETH 0
#         # if input('pub_ip [n/y]:') == 'y':
#         #     pub_ip =
#         external_ips = rt.get_free_ip(dc)['external']
#         for key in external_ips.keys():
#             eth0_ip = external_ips[key]['free'][-1]
#         print('eth0:', eth0_ip)
#         payload.update({'eth0': eth0_ip})
#         #eth1_ip = {'eth1': rt.get_free_ip(dc)[''][f'inet-{dc}-mow1']['free'][-1]}
#         ####   ETH 1
#         internal_ips = rt.get_free_ip(dc)['internal']
#         for key in internal_ips.keys():
#             eth1_ip = internal_ips[key]['free'][-1]
#         print('eth1:', eth1_ip)
#         payload.update({'eth1': eth1_ip})
#         #payload.update({'eth0': rt.get_free_ip(dc)['internal'][f'{dc} internal']['free'][-1]})
#         # if dc == 'selectel':
#         #     dc_network = input('Input spb3/spb5 ')
#         #     payload.update({'eth1': rt.get_free_ip(dc)['external'][f'inet-selectel-{dc_network}']['free'][-1]})
#         # else:
#         #     payload.update({'eth1': cache.dc_literals.get(dc_id)})
#         #print(rt.get_free_ip(payload.get('datacenter')))
#         print('====== OUTPUT ====>\n', json.dumps(payload, indent=4))
#         if input('[n/y] ') == 'y':
#             rt.create_lxd_container(payload)
#
#         # Возвращать конфигурацию neplan для хоста
#         return
#
#         if 'group':
#             pass
#
#         if 'network':
#             pass
#
#     def create(self, name):
#         cmd = ['host', 'group', 'network']
#         buf = []
#         for item in cmd:
#             if item.startswith(name):
#                 buf.append(item)
#         return buf
#     def auto_complete_create(self, text, line, begidx, endidx):
#         #print(line)
#         #print(len(line.split()))
#         if len(line.split()) >= 2 and line.endswith('host'):
#             return
#         line = reversed(line[begidx:endidx])
#         buf = []
#         for b in line:
#             if b == ' ':
#                 break
#             buf.append(b)
#         return self.create(''.join(reversed(buf)))
#
#     complete_create = auto_complete_create
#
# # ===============================================================================
#     #
#     def do_delete(self, *args):
#         '''
#         Удаление объекстов из GArage и RT
#         формат:
#             delete mail-sphinx-shard9-srv01a.prod
#             delete %group_name
#         '''
#         #
#         args = str(*args)
#         #
#         if args.startswith('%'):
#             '''Create group in Garage'''
#             group_name = args.split('%')[1]
#             print('GRP_name', group_name)
#             data = {"name": group_name}
#             portal.delete_group(**data)
#             return
#         #args = str(*args)
#         dns = 'amosrv.ru'
#         system = ''.join(re.findall(r'^\w+', args))
#         print(system)
#         payload = ({'name': f'{args}.{system}.{dns}'})
#         #
#         # ======= Garage ======
#         # Exemple json data
#         # ( minimal )
#         # {
#         #  "name" : "mail-sphinx-shard9-srv01a.prod.mail.amosrv.ru",
#         # }
#         # =======================
#         # _types = ['host', 'group', 'network']
#         # if args.startswith('host'):
#         #     portal.delete_host(args.split()[1])
#         # ======== RT =======
#         # Exemple json data
#         # ( minimal )
#         # {
#         #  "name" : "mail-sphinx-shard9-srv01a.prod.mail.amosrv.ru",
#         # }
#         #
#         print('====== OUTPUT DELETE ====>\n', json.dumps(payload, indent=4))
#         # acync
#         #try:
#         #if  rt.delete(payload) == 202:
#         #    print('Garage: delete' )
#         #except:
#         #    print('failed')
#         rt.delete(payload)
#         portal.delete_host(**payload)


        #print({'group': })
        #print(cache.envs)
        # if args.startswith('container'):
        #     hostname = input('hostname:')
        #     print({'hostname' : hostname})
        #     eth0 = '10.13.2.240'
        #     eth1 = '89.56.77.1'
        #     if input(f"hostname: {hostname}\neth0: {eth0}\neth1: {eth1}\n\n Correct [y/n]") == 'y':
        #         print('OK')
        #     # else:
        #     #     print('Aborted')
        #     print('type:'+ args)

            #
        #elif args.startswith('create'):
        #    print('command:' + args)
            #rt.create_lxd_container('command:'+ args)
        #else:
        #    print('help')



    def lxd_(self, name):
        cmd = ['create', 'delete']
        buf = []
        for item in cmd:
            if item.startswith(name):
                buf.append(item)
        return buf
    def auto_complete_lxd(self, text, line, begidx, endidx):
        # print('\nL', line)
        # print('T', text)
        line = reversed(line[begidx:endidx])
        #print(line)
        buf = []
        for b in line:
            if b == ' ':
                break
            buf.append(b)
        return self.lxd_(''.join(reversed(buf)))
    #
    complete_lxd = auto_complete_lxd

    # def do_check(self, *args):
    #
    #     #portal = executor('all')
    #     print('groups', {'portal': len(portal[3]), 'xgun': len(cache.groups)})
    #     print('hosts', {'portal': len(portal[2]), 'xgun': len(cache.hosts)})
    #     print('datacenters',{'portal': len(portal[0]), 'xgun': len(cache.dc)})
    #     print('environments', {'portal': len(portal[1]), 'xgun': len(cache.env)})

    # def do_search(self, *args):
    #     #rt.search(*args)
    #     if '@' in str(*args):
    #         name, dc = str(*args).split("@")
    #         print(dc)
    #     name = str(*args)
    #     for i in portal.search(name):
    #         print(i)
    #     #result = portal.search(*args)
    def do_search(self, *args):
        arg = str(*args)
        if '@' in str(*args):
            name, dc = str(*args).split("@")
            print(dc)
        for host in cache.hosts:
            if arg in host.get("host"):
                print(host.get("host"))
#####################################
    def do_dom(self, *args):
        hyper = rt.hyper_for_host(*args)
        print(hyper)
        ssh.ssh(hyper.get('hyper'))


    complete_dom = complete_exec

