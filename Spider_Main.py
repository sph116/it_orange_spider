import requests
import json
import re
import math
import random
import time
import pymysql
from DBUtils.PooledDB import PooledDB
import threading
from cookie_pool import Cookie_Pool, get_authorization, get_ip

class Spider_main():
    def __init__(self):

        # self.users = users          # 用于登陆的所有账号信息
        self.log_in_url = "https://www.itjuzi.com/api/authorizations"   # 登录地址
        self.list_page_url = "https://www.itjuzi.com/api/investments"   # 列表页请求地址
        self.heads = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
            'Content-Type': 'application/json;charset=UTF-8',
        }        # post提交json数据 基本请求头
        self.host = 'localhost'
        self.user = 'root'
        self.password = '123456'
        self.port = 3306
        self.db = 'half_a_year_data'
        # self._db = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port, db=self.db)
        # self._db.ping(reconnect=True)
        # self._cur = self._db.cursor()

        self.POOL = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=1,
            maxcached=5,
            ping=0,

            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.db,
            charset='utf8'
        )

    def log_in(self, user):
        """
        登录 返回 authorization 用于后续抓取 拼接新的登录cookie
        :param user:
        :return:
        """
        requests_payload = {"account": user[0], "password": user[1], "type": "pswd"}
        rep = requests.post(url=self.log_in_url, headers=self.heads, data=json.dumps(requests_payload))
        data = json.loads(rep.content)
        code = data['code']
        authorization = data['data']["token"]
        return authorization

    def get_list_detail_page(self, requests_payload):

        i = 1
        save_dates = []
        while i <= 2:
            try:
                authorization = get_authorization()
                headers = self.heads
                headers['Authorization'] = '"{}"'.format(authorization)
                headers['Cookie'] = "_ga=GA1.2.1946721150.1569380973; _gid=GA1.2.2142960013.1569380973; gr_user_id=cf51a490-f1af" \
                                "-41b3-81fa-2b008f0c5bec; MEIQIA_TRACK_ID=1PU4ePP7W0OJIchz5YhwFhTYmkB; MEIQIA_VISIT_ID=1RJNT" \
                                "q1YJSaJDNf2PUbvZbxnQTx; Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1569380974,1569381371,15693" \
                                "83156,1569459288; juzi_user={}; juzi_token={}; _gat_gtag_UA_59006131_1=1; Hm_lpvt_1c58" \
                                "7ad486cdb6b962e94fc2002edf89=1569472543".format(771133, authorization)
                proxy = get_ip()
                rep = requests.post(url=self.list_page_url, headers=headers, data=json.dumps(requests_payload), timeout=15, proxies=proxy)
                time.sleep(round(random.uniform(10, 50), 3))
                if rep.status_code == 200:
                    # print(str(json.loads(rep.content)))
                    str_rep_data = str(json.loads(rep.content))
                    investments_id = re.findall("'id':(.*?),", str_rep_data)
                    investments_name = re.findall("'name': '(.*?)',", str_rep_data)
                    invst_character = [",".join(re.findall("'invst_character_name': '(.*?)'", i)) for i in re.findall("'invst_character': (.*?)]", str_rep_data)]
                    state = [",".join([i for i in re.findall("'state_name': '(.*?)'", i) if i == "种子天使轮" or i == "Pre-A轮"]) for i in re.findall("'state': (.*?)]", str_rep_data)]
                    break

            except (Exception, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
                print("条件{}链接失败，重试".format(requests_payload))
                # modify_go_on_flag(False)
                time.sleep(175)
                # modify_go_on_flag(True)
                i += 1

        for i, j, h, z in zip(investments_name, investments_id, invst_character, state):
            url = "https://www.itjuzi.com/api/invst_left_info/{}".format(j.replace(' ', ''))
            while 1:
                try:
                    authorization = get_authorization()
                    headers = self.heads
                    headers['Authorization'] = '"{}"'.format(authorization)
                    headers[
                        'Cookie'] = "_ga=GA1.2.1946721150.1569380973; _gid=GA1.2.2142960013.1569380973; gr_user_id=cf51a490-f1af" \
                                    "-41b3-81fa-2b008f0c5bec; MEIQIA_TRACK_ID=1PU4ePP7W0OJIchz5YhwFhTYmkB; MEIQIA_VISIT_ID=1RJNT" \
                                    "q1YJSaJDNf2PUbvZbxnQTx; Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1569380974,1569381371,15693" \
                                    "83156,1569459288; juzi_user={}; juzi_token={}; _gat_gtag_UA_59006131_1=1; Hm_lpvt_1c58" \
                                    "7ad486cdb6b962e94fc2002edf89=1569472543".format(771133, authorization)
                    proxy = get_ip()
                    rep = requests.get(url=url, headers=headers, timeout=15, proxies=proxy)
                    time.sleep(round(random.uniform(10, 50), 3))
                    if rep.status_code == 200:
                        detail_data = json.loads(rep.content)
                        wechat = detail_data['data']['wechat']
                        tel = detail_data['data']['tel']
                        save_data = {
                            "investment_name": i,
                            "investment_character": h,
                            "location": requests_payload["location"],
                            "state": z,
                            "wechat": wechat,
                            "tel": tel,
                        }
                        # save_dates.append(save_data)
                        self.Save_data(save_data, url, proxy)
                        break
                except (Exception, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
                    print("url:{} 请求失败 重试 原因:{}".format(url, e))
                    # modify_go_on_flag(False)
                    time.sleep(175)
                    # modify_go_on_flag(True)

    def Save_data(self, item, url, proxy):
        """
        存储详情页url
        :param url_list:
        :param table:
        :return:
        """
        conn = self.POOL.connection()
        cursor = conn.cursor()

        keys = ', '.join(item.keys())
        values = ', '.join(['%s'] * len(item))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table="it_juzi_data", keys=keys,
                                                                     values=values)
        try:
            if cursor.execute(sql, tuple(item.values())):
                conn.commit()

        except Exception as a:
            print(':插入数据失败, 原因', a)
        conn.close()
        print("网址{}数据存储成功 ip:{}".format(url, proxy))


    def Spider_action(self):

        Conditions = [            # 筛选条件
            {"location": "海外", "round": ["种子天使轮", "Pre-A轮"], "pagetotal": 75},
            {"location": "国内", "round": ["种子天使轮", "Pre-A轮"], "pagetotal": 391},

        ]

        requests_payload = {
            'city': [],
            'end_time': "",
            'equity_ratio': "",
            'hot_city': "",
            'ipo_platform': "",
            'keyword': "",
            'location': "国内",
            'page': 1,
            'pagetotal': 14146,
            'per_page': 20,
            'prov': "",
            'round': ["天使轮"],
            'scope': ["游戏"],
            'selected': "",
            'sort': "year_count",
            'start_time': "",
            'status': "",
            'sub_scope': [],
            'time': [],
            'total': 0,
            'type': [],
            'valuation': ""
        }

        for Condition in Conditions:

            for page_num in range(1, math.ceil(Condition['pagetotal']/20) + 1):   # 计算列表页数量
                # 将筛选条件 提取替换到post数据上
                requests_payload["location"] = Condition['location']
                requests_payload["round"] = Condition['round']
                requests_payload["pagetotal"] = Condition['pagetotal']
                requests_payload["page"] = page_num
                # 详情页列表页整合采集方法
                self.get_list_detail_page(requests_payload)
            print("条件{}抓取结束".format(requests_payload))


if __name__ == "__main__":

    t = threading.Thread(target=Cookie_Pool, args=())
    t.start()
    time.sleep(15)
    Spider_main().Spider_action()