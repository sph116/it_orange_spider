import requests
import random
import json
import time

id_datas = [
    ("16217341143", "147258"),
    ("16534145166", "147258"),
]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    'Content-Type': 'application/json;charset=UTF-8',
    'CURLOPT_FOLLOWLOCATION': 'true',
    'Host': 'www.itjuzi.com',
    'Origin': 'https://www.itjuzi.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.itjuzi.com/login',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}        # post提交json数据 基本请求头

log_in_url = "https://www.itjuzi.com/api/authorizations"
authorization = ""
proxy = {}

go_on_flag = True

# def modify_go_on_flag(flag):
#     global go_on_flag
#     go_on_flag = flag
#
# def get_go_on_flag():
#     global go_on_flag
#     return go_on_flag

def get_authorization():
    global authorization
    return authorization

def get_ip():
    global proxy
    return proxy

def Cookie_Pool():
    global authorization
    global proxy
    global go_on_flag
    print("cookie池启动.....")
    while 1:
    #     while 1:
    #         if go_on_flag == True:
    #             break
    #         else:
    #             print("请求失败 开始半小时休眠")
    #             time.sleep(1800)
        try:
            id_data = random.choice(id_datas)
            ip_list = requests.get(
                url="http://www.xiongmaodaili.com/xiongmao-web/api/glip?secret=8c1fe70d7ceb3a4e77284561df11f0d5&orderNo=GL20190927084055mXHsBkPb&count=1&isTxt=1&proxyType={}".format(1)).text.split("\r\n")
            ip_pool = [{"http": "http://{}".format(ip)} for ip in ip_list if ip != ""]
            proxy = random.choice(ip_pool)

            # proxy = {"http": "http://test926w:test926w@117.41.184.193:888"}
            requests_payload = {"account": id_data[0], "password": id_data[1], "type": "pswd"}
            # log_in_url = 'http://ip.chinaz.com/'
            # print(proxy,
            #       log_in_url,
            #       headers,
            #       requests_payload)

            rep = requests.post(url=log_in_url, headers=headers, data=json.dumps(requests_payload), proxies=proxy, timeout=25)
            # rep = requests.get(url=log_in_url, proxies=proxy)
            # print(rep.text)
            data = json.loads(rep.content)
            code = data['code']
            authorization = data['data']["token"]

            print("authorization更新成功 账号:{} ip{} 登录".format(id_data, proxy))
            print("authorization={}".format(authorization))

        except (Exception, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:

            print("账号:{} ip{} 登录失败 重试 原因:{}".format(id_data, proxy, e))
            time.sleep(5)
            continue

        time.sleep(250)
