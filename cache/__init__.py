#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
#from foreman import
from qqok.api.forman import get_item as get_forman_items
from collections import ChainMap
from multiprocessing.pool import ThreadPool
from time import time
import yaml


class Cache:
    """
    Local Cache
    """
    def __init__(self):
        self.local_cache = '/tmp/.qqok.cache.json'
        self.hosts = []
        self.groups = []
        self.grp = []
        self.env = []
        self.dc = []
        self.read_local_cache()
        #self.groups_hierarchy = []

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
        #setattr(self, 'groups', [])
        setattr(self, 'hosts', [])
        setattr(self, 'env', [])
        setattr(self, 'dc', [])
        setattr(self, 'location', [])
        #setattr(self, 'dc_literals', [])

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
    def update_items(self, *args):
        # self.hosts= []
        # self.groups = []
        start = time()
        print(args)

        #result = executor('all')
        #result = executor('hostgroups')
        try:
            result = get_forman_items("all_items")
        except Exception as exc:
            print("Failed request items: {}".format(str(exc)))
            return

        setattr(self, 'groups', [])

        #
        # groups = form.get_item("hostgroups")
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
        #hosts = form.get_item("hosts")
        #     host = {
        #         'host': host.get('name'),
        #         'env': str(*[x.get(host.get('environment_uuid')) for x in self.env if x.get(host.get('environment_uuid'))]), #(self.env.get(name.get("environment_uuid")),
        #         'group': str(*[x.get(host.get("group_uuid")) for x in self.grp if x.get(host.get("group_uuid"))]),
        #         'dc': str(*[x.get(host.get("datacenter_uuid")) for x in self.dc if x.get(host.get("datacenter_uuid"))]),
        #         }

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
        self.write_cache(cache_items)

        # for group in result[3]:
        #     self.grp.append(
        #         {group.get('uuid'): group.get('name')}
        #     )


        # setattr(self, 'groups', [])
        # for group in self.hierarchy_groups(result[3]):
        #     self.groups.append(group)
        #
        # setattr(self, 'env', [])
        # #print(self.env)
        # for envi in result[1]:
        #     self.env.append({envi.get('uuid'): envi.get('name')})
        # #print(self.env)
        #
        # setattr(self, 'dc', [])
        # for dc in result[0]:
        #     self.dc.append({dc.get('uuid'): dc.get('name'), 'literal': dc.get('description').split(":")[0]})
        #
        # # setattr(self, 'dc_literals', [])
        # # for dc_liter in portal.get_dc('literals'):
        # #     self.dc_literals.append(dc_liter)
        #
        # setattr(self, 'hosts', [])
        # for host in result[2]:
        #     host = {
        #         'host': host.get('name'),
        #         'env': str(*[x.get(host.get('environment_uuid')) for x in self.env if x.get(host.get('environment_uuid'))]), #(self.env.get(name.get("environment_uuid")),
        #         'group': str(*[x.get(host.get("group_uuid")) for x in self.grp if x.get(host.get("group_uuid"))]),
        #         'dc': str(*[x.get(host.get("datacenter_uuid")) for x in self.dc if x.get(host.get("datacenter_uuid"))]),
        #         }
        #     self.hosts.append(host)
        #
        # attr_list = ['grp', 'groups', 'hosts', 'env', 'dc', 'dc_literals']
        # print('Update execute time:', time() - start)
        # cache_items = {'groups': self.groups, 'hosts': self.hosts, }
        # self.write_cache(cache_items)

    def resive_hosts(self):
        print(os.getcwd())

    def hierarchy_groups(self, groups):
        # Groups withiout parent
        new_groups = [x for x in groups if not x.get("parent")]
        [gg.remove(x) for x in [x for x in gg if not x.get("parent")]]
        for g in gg:
            g_n = "{}/{}".format(g.get("parent"), g.get("name"))
            print("== " + g_n)
            for host in hh:
                if host.get("group_title") and host.get("group_title") == g_n:
                    print(host.get("host"))
        ###############
        groups = 0
        hosts = 0
        _hosts = []
        for g in gg:
            if g.get("parent"):
                g_n = "{}/{}".format(g.get("parent"), g.get("name"))
            else:
                g_n = g.get("name")
            print("== " + g_n)
            for host in hh:
                if host.get("group_title") and host.get("group_title") == g_n:
                    print(host.get("host"))
                    hosts += 1
                    _hosts.append(host.get("id"))
            groups += 1
        print(groups)
        print(hosts)
        ### Ungroup hosts
        for hhh in hh:
            if hhh.get("id") not in _hosts: print(hhh)


    # def resive_groups(self):
    #     for group in portal.get_groups_new():
    #         yield group

    # def hierarchy_groups(self, groups):
    #
    #     new_grp = {}
    #     for grp in groups:
    #     # # count += 1
    #     #     # yield {grp.get('name'): [x.get('name') for x in grp['_embedded']['groups']]}
    #         new_grp.update({grp.get('name'): [x.get('name') for x in grp['_embedded']['groups']]})
    #     # Get groups from portal
    #     #new_grp = {}
    #     #new_grp = groups
    #     grp = []
    #     #for p in portal.get_groups_new():
    #     #for p in groups:
    #         #grp.append(p)
    #     #print('Incon groups:', len(grp))
    #     # for i in grp:
    #     #     new_grp.update(**i)
    #     c0 = 0
    #
    #
    #     # make dict with empty groups
    #     for group in new_grp:
    #         c0 += 1
    #         group_len = len(new_grp.get(group))
    #         if group_len == 0:
    #             new_grp.update({group: [[], 0, 0]})
    #     lvl0 = {x: y for x, y in new_grp.items() if isinstance(y[0], list) and y[2] == 0}
    #
    #     # make copy main dict
    #     c_new_grp = new_grp.copy()
    #
    #     # remove empty group
    #     for pp in lvl0:  # Сюда функцию чистки
    #         c_new_grp.pop(pp)  #
    #
    #     for group in c_new_grp:
    #         incl = new_grp.get(group)
    #         mask = []
    #         ll = len(incl)
    #         for gg in incl:
    #             if gg in lvl0:
    #                 mask.append(0)
    #             else:
    #                 mask.append(1)
    #         if mask.count(1) <= 0:
    #             new_grp.update({group: [incl, mask, 1]})
    #         elif mask.count(1) == ll:
    #             new_grp.update({group: [incl, mask, 3]})
    #         else:
    #             new_grp.update({group: [incl, mask, 2]})
    #             # Не забыть перобразовать mask в кортеж
    #     # От этого нужно избавляться, передалаю когда буду делать дерево
    #     lvl1 = {x: y for x, y in new_grp.items() if y[2] == 1}  # first
    #     lvl2 = {x: y for x, y in new_grp.items() if y[2] == 2}  # middle
    #     lvl3 = {x: y for x, y in new_grp.items() if y[2] == 3}  # point
    #
    #     for name, proper in lvl2.items():
    #         groups = proper[0]
    #         mask = proper[1]
    #         for pos in [i for i, e in enumerate(proper[1].copy()) if e == 1]:
    #             if lvl1.get(proper[0][pos]):
    #                 #print(1)
    #                 groups.extend(lvl1.get(proper[0][pos])[0])
    #                 mask[pos] = 0
    #                 new_grp.update({name: [ groups, mask, 2] })
    #             elif lvl2.get(proper[0][pos]):
    #                 groups.extend(lvl2.get(proper[0][pos])[0])
    #                 mask[pos] = 0
    #                 new_grp.update({name: [groups, mask, 2]})
    #                 #print(0)
    #
    #     for name, proper in lvl3.items():
    #         groups = proper[0]
    #         mask = proper[1]
    #         grps = groups.copy()
    #         mm = mask.copy()
    #         for pos in [i for i, e in enumerate(mask) if e == 1]:
    #             ng = new_grp.get(grps[pos])[0]
    #             grps.extend(ng)
    #             mm[pos] = 0
    #         new_grp.update({name: [ grps, mask, 3 ]})
    #     print('Groups in hierarchy:', len(new_grp))
    #
    #     # Cleaning
    #     #del(lvl1)
    #     #del(lvl2)
    #     #del(lvl3)
    #     for i in new_grp.items():
    #         yield {i[0]: i[1][0]}
    #     #return new_grp
    #

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

#
# #=====
# # def add_host(self, item, *args):
# #     try:
# #         hosts = getattr(self, 'hosts')
# #     except AttributeError:
# #         #self.init_hosts()
# #         hosts = getattr(self, 'hosts')
# #     hosts.append(item)
# #
# # def add_group(self, item):
# #     try:
# #         groups = getattr(self, 'groups')
# #     except AttributeError:
# #         #self.init_hosts()
# #         groups = getattr(self, 'groups')
# #     groups.append(item)
# #
# # def get_host(self, name):
# #     for item in self.get_hosts():
# #         if item['name'] == name:
# #             return item
# #
# # def do_get_hosts(self):
# #     return getattr(self, 'hosts')
# # get_hosts = do_get_hosts
# #
# # def do_get_groups(self):
# #     return getattr(self, 'groups')
# # get_groups = do_get_groups
# #======
#
#
# # Подумать, как объеденить две эти функции в одну
# # def read_cache_file():
# #     if not os.path.exists('/tmp/.xgun.t_cache.json'): # Не забыть поменять на нормальное название
# #         return
# #     with open("/tmp/.xgun.t_cache.json", 'r') as fd:
# #         try:
# #             buf = json.loads(fd.read())
# #         except:
# #             print('Hosts cache is dirty or empty. Run <reload>')
# #             return
#
# # def reload():
# #     """Load data from garage"""
# #     #self.init_hosts()
# #     #self.init_groups()
# #     # for item in Garage().get_hosts():
# #     #     self.add_host(item)
# #     reload_hosts()
# #     # for group in Garage().get_groups_new():
# #     #     self.add_group(group)
# #     reload_groups()
# #     #self.save_hosts_cache()
# #     #self.save_groups_cache()
# #
# #     #self.update_exec_completions()
# #
#     # Иерархия групп
#     # 1) Составлять бинарное дерево
#     # 2) Проходить по всем группам
#     # 3) считать глубину для каждой группы
#
# # ============  Group hierarchy ====
# # Алгоритм
# # Получаем из гаража список со словорями [ { }, { } ]
# # Формируем единый словарь { имя группы : подгруппы,  }
# # Итерируем словарь и извлекаем пустые группы в множество lvl 0,
# #  группы включающие в себя только пустые (lvl0) извлекаем в lvl 1
# #  группы
#
# #
# # Итерируем список групп с подгруппами
# # и запрашиваем у каждой спик подгрупп
# # опять итерируем список
# # и смотрим присутствует группа в списке пустых групп
#
#
# # dic = {'greoup_name':
# #          {
# #            'members': "list groups",
# #            'len': 12,
# #            'deep': 4,
# #             'lvl': 1
# #             }
# #         }
# #
# # grp = 'garage'
# # grp_sum = len(grp)
# #
# # empty_grp = set()
# # grp_inc_grp = set()
# #
# # new_g_dic = {}
# #
# # for grpp in new_grp:
# #     new_g_dic.update({'len': len(grpp)})
# #
# # empty_grp = set()
# # grp_inc_grp = set()
# # set_for_groups_member = set()
# # new_g_dic = {}
# # fin_grp = set()
#
#
# #=====
# def hierarchy():
#     #Get groups from Garage
#     new_grp = {}
#     grp = []
#     for p in portal().get_groups_new():
#         grp.append(p)
#     print('Incon groups:', len(grp))
#     for i in grp:
#         new_grp.update(**i)
#     c0 = 0
#
#     # make dict with empty groups
#     for group in new_grp:
#         c0 +=1
#         group_len = len(new_grp.get(group))
#         if group_len == 0:
#             new_grp.update({group: [[], 0, 0]})
#     lvl0 = {x: y for x, y in new_grp.items() if isinstance(y[0], list) and y[2] == 0}
#
#     # make copy main dict
#     c_new_grp = new_grp.copy()
#
#     # remove empty group
#     for pp in lvl0:        # Сюда функцию чистки
#         c_new_grp.pop(pp)    #
#
#     for group in c_new_grp:
#         incl = new_grp.get(group)
#         mask = []
#         ll = len(incl)
#         for gg in incl:
#             if gg in lvl0:
#                 mask.append(0)
#             else:
#                 mask.append(1)
#         if mask.count(1) <= 0:
#             new_grp.update({group: [incl, mask, 1]})
#         elif mask.count(1) == ll:
#             new_grp.update({group: [incl, mask, 3]})
#         else:
#             new_grp.update({group: [incl, mask, 2]})
#             # Не забыть перобразовать mask в кортеж
#     lvl1 = {x: y for x, y in new_grp.items() if y[2] == 1} # first
#     lvl2 = {x: y for x, y in new_grp.items() if y[2] == 2} # middle
#     lvl3 = {x: y for x, y in new_grp.items() if y[2] == 3} # point
#
#     for name, proper in lvl2.items():
#         groups = proper[0]
#         mask = proper[1]
#         for pos in [i for i, e in enumerate(proper[1].copy()) if e == 1]:
#             groups.extend(lvl1.get(proper[0][pos])[0])
#             mask[pos] = 0
#             new_grp.update({name: [ groups, mask, 2] })
#
#     for name, proper in lvl3.items():
#         groups = proper[0]
#         mask = proper[1]
#         grps = groups.copy()
#         mm = mask.copy()
#         for pos in [i for i, e in enumerate(mask) if e == 1]:
#             ng = new_grp.get(grps[pos])[0]
#             grps.extend(ng)
#             mm[pos] = 0
#         new_grp.update({name: [ grps, mask, 3]})
#     print('After processing:', len(new_grp))
#     for i in new_grp.items():
#         yield {i[0]: i[1]}
#     #return new_grp
#
#
#
# #=====================
# # мерж 2 группы с вложеностью 2
# # for name, proper in lvl2.items():
# #     print(name, proper)
# #     groups = proper[0]
# #     mask = proper[1]
# #     print(groups)
# #     for pos in [i for i, e in enumerate(proper[1].copy()) if e == 1]:
# #         print(len(groups), groups)
# #         print(proper[0][pos])
# #         print(lvl1.get(proper[0][pos])[0])
# #         groups.extend(lvl1.get(proper[0][pos])[0])
# #         mask[pos] = 0
# #         print(len(groups), groups)
# #         new_grp.update({name : groups})
# #
# #
# #
# # for name, proper in lvl3.items():
# #     print('in lvl3:', list(lvl3.keys()))
# #     print(name, proper)
# #     groups = proper[0]
# #     mask = proper[1]
# #     print(groups,mask)
# #     grps = groups.copy()
# #     mm = mask.copy()
# #     #we = set()
# #     #posit = [i for i, e in enumerate(mask) if e == 1]
# #     print(name, '|---')
# #     for pos in [i for i, e in enumerate(mask) if e == 1]:
# #         print('|====')
# #         print(len(grps), grps)
# #         print('Grp name:', grps[pos])
# #         ng = new_grp.get(grps[pos])[0]
# #         msk = new_grp.get(grps[pos])[1]
# #         lv = new_grp.get(grps[pos])[2]
# #         print(len(ng), ng, lv)
# #         grps.extend(ng)
# #         #mask[pos] = 0
# #         #mask.extend(new_grp.get(proper[0][pos])[1])
# #         print(len(grps), grps )
# #         mm[pos] = 0
# #         print(mm)
# #         print('==|')
# #         print(grps[pos], ng)
# #         #try:
# #         #new_grp.update({grps[pos]: ng})
# #         #ggg.extend(grps)
# #         # except:
# #         #     print('Dict update failed')
# #         # Final
# #         #nn_grp.update({name : groups})
# #         #we.add(grps)
# #     print(name, grps)
# #     new_grp.update({name: grps})
# #     print('--|')
# #
# # def extract(name):
# #     #for ii in new_grp.get(name):
# #     sub_grp, mask, lvl = new_grp.get(name)
# #     return [sub_grp, mask, lvl]
# # # Return new dict
# #
# #
# # #def build_grp():
# # #for i in lvl2:
# # for i in lvl2:
# #     print('Processing lvl2')
# #     grg, mask, lvl = new_grp.get(i)
# #     #grg = new_grp.get(i)[0]
# #     #mask = new_grp.get(i)[1]
# #     posit = [i for i, e in enumerate(mask) if e == 1]
# #     for pos in posit:
# #     #if new_grp.get(grg[mask.index(1)])[2] != 0:
# #         sub_grp, mask, lvl = new_grp.get(grg[pos])
# #         print(i, grg, '\n',grg[pos] + ":", sub_grp, mask)
# #         #print(grg.get(sub_grp))
# #
# # for g in lvl3:
# #     print('Processing lvl3')
# #     grg, mask, lvl = new_grp.get(g)
# #     #grg = new_grp.get(i)[0]
# #     #mask = new_grp.get(i)[1]
# #     print(g+":", grp)
# #     posit = [i for i, e in enumerate(mask) if e == 1]
# #     for pos in posit:
# #     #if new_grp.get(grg[mask.index(1)])[2] != 0:
# #         sub_grp, mask, lvl = new_grp.get(grg[pos])
# #         print(g+":" ,grp,'\n', grg[pos] + ":", sub_grp, mask)
# #         #print(grg.get(sub_grp))
# #         if 1 in mask:
# #             sub_grp, mask, lvl = new_grp.get(grg[pos])
# #             posit = [i for i, e in enumerate(mask) if e == 1]
# #             print('Found', posit, 'group:', grg[pos])
# #             for pos in posit:
# #             #     # if new_grp.get(grg[mask.index(1)])[2] != 0:
# #                 sub_grp, mask, lvl = new_grp.get(sub_grp[pos])
# #                 print(sub_grp[pos], mask)
# #                 #rint(g + ":", grp, '\n', grg[pos] + ":", sub_grp, mask)
# #
# # for g in lvl3:
# #     print('Processing lvl3')
# #     name = g
# #     sub_grp, mask, lvl = new_grp.get(g)
# #     print('orig_mask:', mask)
# #     if 1 in mask:
# #         for i in [i for i, e in enumerate(mask) if e == 1]:
# #             g, m, l = extract(sub_grp[i])
# #             #print(m)
# #             mask[i] = m
# #     print(mask)
# #
# #
# #
# # def extract(name):
# #     #for ii in new_grp.get(name):
# #     sub_grp, mask, lvl = new_grp.get(name)
# #     return [sub_grp, mask, lvl]
# #
# #
# #
# # # =======
# # rr = [[0, 0, 1], [0,1,0], [0,0,0]]
# # while True:
# #     for ii in rr:
# #         if 1 in ii:
# #             print('pos:', ii.index(1))
# #         else:
# #             print('0')
# #     break
# # # ========
# #
# #
# #
# #
# #
# #
# # def get_grp(name):
# #     mask = []
# #     for i in new_grp.get(name):
# #         print(inc)
# #         inc = i[0]
# #         lvl = i[1]
# #         if i[0] not in empty_grp:
# #             mask.append(1)
# #         mask.append(0)
# #     return new_grp.get(name), mask
# # # new_grp.update({'core-production-memcache-session': [[], 0]})
# # # new_grp.update({'core-production-memcache-session': {'include':[], "lvl": 0}})
# #
# # #def mapping_grp()
# # def main():
# #     separation_grp()
# #     for group in lvl1
# #     # for group in unsorted.copy():
# #     #     grps = get_grp(group)
# #     #     if 1 not in grps[1]:
# #     #
# #     #         lvl1.add(group)
# #     #         #new_grp.update({group: [grps, 1]})
# #     #         print(group, "lvl1")
# #     #         unsorted.remove(group)
# #     #         new_grp.update({group: [grps[0], 1]})
# #     #     else:
# #     #         lvl2.add(group)
# #     #         print(group, "lvl2")
# #     #if len(unsorted)
# #
# #             #unsorted.add(group)
# # main()
# #
# #
# #
# #         we = set()
# #         print("G name:", group, "Set len:", len(we))
# #         group_include = new_grp.get(group)
# #         print("G name:", group, "Adding groups", group_include)
# #         [we.add(x) for x in group_include]
# #         print("G name:", group, 'Set len:', len(we))
# #         group_len = len(group)
# #         group_mask = []
# #         # print("From Garage:", group, group_include, group_len)
# #         ######## Первый уровень
# #         for gg in group_include:
# #             # Ппроверка на принодлежность к списку empty_grp
# #             if gg not in empty_grp:
# #                 print("G:", gg, "is empty")
# #                 group_mask.append(0)
# #             else:
# #                 # Если не принадлежит то идём глубже и смотрим какие и сколько пустых групп в группе
# #                 # Или создавать маску и на этом заканчивать ?
# #                 print("IN", group, "found not empty group", gg)
# #                 group_mask.append(1)
# #         if 1 not in group_mask:
# #             print("All G in G empty", group)
# #         else:
# #             print("G include not empty G", group)
# #             # знаем сколько каких рупп в группе
# #         ######## Второй уровень
# #         #         for i in new_grp.get(gg):
# #         #             print(i)
# #         #             if i in empty_grp:
# #         #                 print("G:", i, "in epmpty")
# #         #             #we.add(i)
# #         #             #print('3 Len we:', len(we) )
# #         #             else: # i not in empty_grp:
# #         #                 we.add(*new_grp.get(i))
# #         #                 print(new_grp.get(i))
# #         #                 print('3 Len we:', len(we))
# #         #                 print("I", i)
# #         #         # if len(pp) < 0:
# #         #         #    print(pp)
# #         # # if 1 in group_mask:
# #         # # [i for i, e in group_mask if e == 1]
# #         # new_d.update({group : tuple(we)})
# #         print("== \ngroup: {}\ninclude: {}\n==\n".format(group, sorted(we)))
# #
# #
# # for group in grp_inc_grp:
# #     group_include = new_grp.get(group)
# #     group_len = len(group)
# #     group_mask = []
# #     print(group, group_include, group_len)
# #     # Good cycle ==
# #     # c = 0
# #     # while c <= ll:
# #     #     print("Eter:", c, ll)
# #     #     c += 1
# #     #
# #     # else:
# #     #     print('stop')
# #     # ===
# #
# #     for gg in group_include:
# #         # group_mask.append(gg)
# #         # count +=1
# #         # while count < ll :
# #         # Ппроверка на принодлежность к списку empty_grp
# #         if gg in empty_grp:
# #             group_mask.append(0)
# #         else:
# #             group_mask.append(1)
# #             # members = new_grp.get()
# #             pp = new_grp.get(gg)
# #             print(pp)
# #     # if 1 in
# #     print("group: {}\ninclude: {}\nmask: {}".format(group, group_include, group_mask))
# #     #
# #     # print(new_grp.get(group))
# #
# #
# #
# #
# # # v 0.0.1
# # # def separation_grp():
# # #     lvl0 = set()
# # #     lvl1 = set()
# # #     lvl2 = set()
# # #     lvl3 = set()
# # #     unsorted = set()
# # #     new_grp = {}
# # #
# # #     # group_lvl0 = {}
# # #     # group_lvl1 = {}
# # #     # group_lvl2 = {}
# # #     # group_lvl3 = {}
# # #
# # #     # Формируем новый словарь { group_name : [], group_name  }
# # #     grp = []
# # #     for p in Garage().get_groups_new():
# # #         grp.append(p)
# # #
# # #     for i in grp:
# # #         new_grp.update(**i)
# # #     c0 = 0
# # #     # make empty groups
# # #
# # #     for group in new_grp:
# # #         c0 +=1
# # #         group_len = len(new_grp.get(group))
# # #
# # #         if group_len == 0:
# # #             #print("G: {} empty 0".format(group_name))  #
# # #             #lvl0.add(group)
# # #             new_grp.update({group: [[], 0, 0]})
# # #             #group_lvl0.update({group: [[], 0, 0]})
# # #         else:
# # #             incl = new_grp.get(group)
# # #             #print("G: {} not empty".format(group_name))
# # #             # Make mask for group
# # #             mask = []
# # #             for gg in incl:
# # #                 ll = len(incl)
# # #                 if gg in empty_grp:
# # #                     mask.append(0)
# # #                 else:
# # #                     inc = new_grp.get(gg)
# # #                     mask.append(1)
# # #                     # if inc[2] == 1:
# # #                     #     new_grp.update({group_name: [incl, mask, 1]})
# # #             #print(group, mask)
# # #             if mask.count(1) <= 0:
# # #                 new_grp.update({group: [incl, mask, 1]})
# # #                 #lvl1.add(group)
# # #                 #group_lvl1.update({group: [incl, mask, 1]})
# # #                 print('G:', group, "M:", mask, "lvl1")
# # #                 #print(extract(group))
# # #
# # #             elif mask.count(1) == ll:
# # #                 new_grp.update({group: [incl, mask, 3]})
# # #                 #group_lvl3.update({group: [incl, mask, 3]})
# # #                 #lvl3.add(group)
# # #                 print('G:', group, "M:", mask, "lvl3")
# # #                 #print(extract(group))
# # #             else:
# # #                 new_grp.update({group: [incl, mask, 2]})
# # #                 #group_lvl2.update({group: [incl, mask, 2]})
# # #                 #lvl2.add(group)
# # #                 print('G:', group, "M:", mask, "lvl2")
# # #                 #print(extract(group))
# # #                 # Не забыть перобразовать mask в кортеж
# # #     lvl0 = {x: y for x, y in new_grp.items() if y[2] == 0} # Dno
# # #     lvl1 = {x: y for x, y in new_grp.items() if y[2] == 1} # first
# # #     lvl2 = {x: y for x, y in new_grp.items() if y[2] == 2} # middle
# # #     lvl3 = {x: y for x, y in new_grp.items() if y[2] == 3} # point
# # #     print("G Summ:", c0)
# # #     return new_grp
# #
# #
# #
# # # ====== v0.0.2
# def separation_grp():
#     lvl0 = set()
#     lvl1 = set()
#     lvl2 = set()
#     lvl3 = set()
#     unsorted = set()
#
#     #lvl0 = {}
#     new_grp = {}
#     # group_lvl0 = {}
#     # group_lvl1 = {}
#     # group_lvl2 = {}
#     # group_lvl3 = {}
#
#     # Формируем новый словарь { group_name : [], group_name  }
#     grp = []
#     for p in portal.get_groups_new():
#         grp.append(p)
#
#     for i in grp:
#         new_grp.update(**i)
#     c0 = 0
#
#     # make empty groups
#     for group in new_grp:
#         c0 +=1
#         group_len = len(new_grp.get(group))
#         if group_len == 0:
#             #print("G: {} empty 0".format(group_name))  #
#             #lvl0.add(group)
#             new_grp.update({group: [[], 0, 0]})
#             #group_lvl0.update({group: [[], 0, 0]})
#         lvl0 = {x: y for x, y in new_grp.items() if isinstance(y[0], list) and y[2] == 0}
#
#     # copy
#     c_new_grp = new_grp.copy()
#
#     for pp in lvl0:        # Сюда функцию чистки
#         c_new_grp.pop(pp)    #
#
#     for group in c_new_grp:
#         incl = new_grp.get(group)
#         #print("G: {} not empty".format(group_name))
#         # Make mask for group
#         mask = []
#         for gg in incl:
#             ll = len(incl)
#             if gg in lvl0:
#                 mask.append(0)
#             else:
#                 inc = new_grp.get(gg)
#                 mask.append(1)
#                 # if inc[2] == 1:
#                 #     new_grp.update({group_name: [incl, mask, 1]})
#         print(group, mask)
#         if mask.count(1) <= 0:
#             new_grp.update({group: [incl, mask, 1]})
#             #lvl1.add(group)
#             #group_lvl1.update({group: [incl, mask, 1]})
#             print('G:', group, "M:", mask, "lvl1")
#             #print(extract(group))
#
#         elif mask.count(1) == ll:
#             new_grp.update({group: [incl, mask, 3]})
#             #group_lvl3.update({group: [incl, mask, 3]})
#             #lvl3.add(group)
#             print('G:', group, "M:", mask, "lvl3")
#             #print(extract(group))
#         else:
#             new_grp.update({group: [incl, mask, 2]})
#             #group_lvl2.update({group: [incl, mask, 2]})
#             #lvl2.add(group)
#             print('G:', group, "M:", mask, "lvl2")
#             #print(extract(group))
#             # Не забыть перобразовать mask в кортеж
#     lvl1 = {x: y for x, y in new_grp.items() if y[2] == 1} # first
#     lvl2 = {x: y for x, y in new_grp.items() if y[2] == 2} # middle
#     lvl3 = {x: y for x, y in new_grp.items() if y[2] == 3} # point
#     print("G Summ:", c0)
#
#     for name, proper in lvl2.items():
#         print(name, proper)
#         groups = proper[0]
#         mask = proper[1]
#         print(groups)
#         for pos in [i for i, e in enumerate(proper[1].copy()) if e == 1]:
#             print(len(groups), groups)
#             print(proper[0][pos])
#             print(lvl1.get(proper[0][pos])[0])
#             groups.extend(lvl1.get(proper[0][pos])[0])
#             mask[pos] = 0
#             print(len(groups), groups)
#             print('New M:', mask)
#             new_grp.update({name: [ groups, mask, 2 ] })
#
#     for name, proper in lvl3.items():
#         print('in lvl3:', list(lvl3.keys()))
#         print(name, proper)
#         groups = proper[0]
#         mask = proper[1]
#         print(groups, mask)
#         grps = groups.copy()
#         mm = mask.copy()
#         # we = set()
#         # posit = [i for i, e in enumerate(mask) if e == 1]
#         print(name, '|---')
#         for pos in [i for i, e in enumerate(mask) if e == 1]:
#             print('|====')
#             print(len(grps), grps)
#             print('Grp name:', grps[pos])
#             ng = new_grp.get(grps[pos])[0]
#             msk = new_grp.get(grps[pos])[1]
#             lv = new_grp.get(grps[pos])[2]
#             print(len(ng), lv, msk, ng,)
#             grps.extend(ng)
#             # mask[pos] = 0
#             # mask.extend(new_grp.get(proper[0][pos])[1])
#             print(len(grps), grps)
#             mm[pos] = 0
#             print(mm)
#             print('==|')
#             print(grps[pos], ng)
#             # try:
#             # new_grp.update({grps[pos]: ng})
#             # ggg.extend(grps)
#             # except:
#             #     print('Dict update failed')
#             # Final
#             # nn_grp.update({name : groups})
#             # we.add(grps)
#         print(name, grps)
#         #new_grp.update({name: grps})
#         print('--|')
#
#     return new_grp
