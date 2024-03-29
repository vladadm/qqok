import requests
import json
import yaml
from qqok.api.forman import req


URL = 'https://zabbix.vcp.ivi.ru/api_jsonrpc.php'
HEADERS = {"Content-Type": "application/json-rpc"}


class Auth:
    def __init__(self):
        self.user = self.load().get("user")
        self.pw = self.load().get("password")
        self.get_key()

    @staticmethod
    def load():
        config_file = 'config.yaml'
        config_path = "/".join(__file__.split("/")[:-2]) + "/"
        try:
            with open(config_path + config_file, 'r') as file:
                return yaml.safe_load(file.read()).get("zabbix")
        except Exception as exc:
            print("Exc in read config file", exc)
            return

    def get_key(self):
        data = {
            "params": {
                "password": self.pw,
                "user": self.user
            },
            "jsonrpc": "2.0",
            "method": "user.login",
            "id": "1"
        }
        try:
            post = requests.post(URL, headers=HEADERS, data=json.dumps(data)).json()
            if post.get("error"):
                # print(post.get("error"))
                raise ConnectionError("[{}] {}".format(URL, post["error"]["data"]))
                return
            setattr(self, "api_key", post.get('result'))
        except Exception as exx:
            print('Except: ', exx)
            return


cred = Auth()


class API(object):
    def __init__(self):
        self.key = cred.api_key
        self.dc = ["dtln", "linx", "m9"]

    def post(self, data):
        '''
        Метод POST
        :param data: данные для передачи запросом (dict)
        :return:
        '''
        try:
            post = requests.post(URL, headers=HEADERS, data=json.dumps(data)).json()
            return post.get("result")
        except Exception as exx:
            print("Except: ", exx)
            return

    def host_groups(self, group_id="", limit=""):
        """
        Возвращает группы хостов
        Может принимать параметры
        :param group_id: идентификатор группы (int)
        :param limit: лимит на выборку (int)
        :return: возвращает список словарей [ {}, {} ]
        """
        data = {
            "params": {
            },
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "auth": self.key,
            "id": "1"
        }
        if limit:
            data["params"].update({"limit": int(limit)})
        if group_id:
            data["params"].update({"groupids": int(group_id)})
        try:
            post = requests.post(URL, headers=HEADERS, data=json.dumps(data)).json()
            return post.get("result")
        except Exception as exx:
            print("Except: ", exx)
            return

    def host_for_groups(self, group_id=""):
        data = {
            "params": {
                "output": [
                    "host",
                    "status",
                ],
            },
            "jsonrpc": "2.0",
            "method": "host.get",
            "auth": self.key,
            "id": "1"
        }

        if not group_id:
            # print("Host group not found")
            group_name = "unsorted"
            # return
        else:
            group = self.host_groups(group_id)
            data["params"].update({"groupids": group_id})
            group_name = dict(*group).get("name")

        try:
            post = requests.post(URL, headers=HEADERS, data=json.dumps(data)).json()
            #return post.get("result")
        except Exception as exx:
            print("Except: ", exx)
            return
        print({
            "group_id": group_id,
            "group_name": group_name,
            "hosts": post.get("result")
        })
        ###################################################################
        # for host in dev_h:
        #     ss.update({host.get("hostid"): {"name": host.get("host")}})
        return {
            "group_id": group_id,
            "group_name": group_name,
            "hosts": post.get("result")
        }

    def interfaces_for_host(self, host_id):
        '''

        :param host_id:
            Параметром можно передать число 195 либо список чисел [ 195, 208, ... ]
        :return:
        '''
        data  = {
            "params": {
                "hostids": host_id
            }, "jsonrpc": "2.0",
            "method": "hostinterface.get",
            "auth": self.key,
            "id": "1"
        }
        try:
            post = requests.post(URL, headers=HEADERS, data=json.dumps(data)).json()
            #return post.get("result")
        except Exception as exx:
            print("Except: ", exx)
            return
        return post.get("result")


    def hosts(self, search=""):
        '''

        :return:
        {
            "hostid": "12804",
            "proxy_hostid": "12753",
            "host": "gitlab-runner-dtln-4",
            "status": "0",
            "disable_until": "0",
            "error": "",
            "available": "1",
            "errors_from": "0",
            "lastaccess": "0",
            "ipmi_authtype": "-1",
            "ipmi_privilege": "2",
            "ipmi_username": "",
            "ipmi_password": "",
            "ipmi_disable_until": "0",
            "ipmi_available": "0",
            "snmp_disable_until": "0",
            "snmp_available": "0",
            "maintenanceid": "0",
            "maintenance_status": "0",
            "maintenance_type": "0",
            "maintenance_from": "0",
            "ipmi_errors_from": "0",
            "snmp_errors_from": "0",
            "ipmi_error": "",
            "snmp_error": "",
            "jmx_disable_until": "0",
            "jmx_available": "0",
            "jmx_errors_from": "0",
            "jmx_error": "",
            "name": "gitlab-runner-dtln-4",
            "flags": "0",
            "templateid": "0",
            "description": "",
            "tls_connect": "1",
            "tls_accept": "1",
            "tls_issuer": "",
            "tls_subject": "",
            "tls_psk_identity": "",
            "tls_psk": "",
            "proxy_address": "",
            "auto_compress": "1"
        }
        '''
        data = {
            "params": {
                "output": ["host"]
            },
            "jsonrpc": "2.0",
            "method": "host.get",
            "auth": self.key,
            "id": "1"
        }
        if search:
            data["params"].update({"search": {"name": [search]}})
        try:
            post = requests.post(URL, headers=HEADERS, data=json.dumps(data)).json()
            post_ids = [ x.get("hostid") for x in post.get("result")]
            post_iface = self.interfaces_for_host(post_ids)
            # ss = {}
            ss = []
            for host in post.get("result"):
                ss.append({"id": host.get("hostid"), "host": host.get("host")})

            for host in ss:
                host_id = host.get("id")
                for iface in post_iface:
                    iface_id = iface.get("hostid")

                    if host_id == iface_id and iface['type'] == "1":
                        host.update({"ip": iface.get("ip", "empty"), "fqdn": iface.get("dns", "empty")})
            with_fqdn = [x for x in ss if x.get("fqdn")]
                    #ss[iface.get("hostid")].update({"ip": iface.get("ip", "empty"), "fqdn": iface.get("dns", "empty")})
            #for iface in post_iface:
             #   ss[iface.get("hostid")].update({"ip": iface.get("ip", "empty"), "fqdn": iface.get("dns", "empty")})
            #print(ss)
            with_fqdn = [{"id": x.get("id"), "host": x.get("fqdn"), "ip": x.get("fqdn")} for x in ss if x.get("fqdn")]
            return with_fqdn
            #return post.get("result")
        except Exception as exx:
            print("Except: ", exx)
            return
        # count = 0
        # hosts = []
        # for host in post.get("result"):
        #     count += 1
        #     hosts.append({"id": host.get('hostid'), "name": host.get('host')})
        # return hosts


zabbix_api = API()


