# -*- coding: utf-8 -*-
import multiprocessing
import multiprocessing.managers
import random, time
import queue
import os
import requests
import lxml
import re
import pymysql
from urllib import parse


class QueueManger(multiprocessing.managers.BaseManager):
    pass
host = '127.0.0.1'
user = 'root'
passwd = '18351962092'
dbname = 'proxies'
tablename = 'proxy'
proxies = []
db = pymysql.connect(host, user, passwd, dbname)
cursor = db.cursor()
sql = f"select * from {tablename}"
cursor.execute(sql)
results = cursor.fetchall()
cursor.close()
for row in results:
    ip = row[0]
    port = row[1]
    fromUrl = f"http://{ip}:{port}"
    proxies.append(fromUrl)
proxy = random.choice(proxies)
proxies = {
      "http": proxy,
      "https": proxy
   }
def getResults(url):
    headers = {
    'Accept':  'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #'Accept-Encoding':  'gzip, deflate',
    'Accept-Language':  'zh-CN,zh;q=0.9',
    'Cache-Control':  'max-age=0',
    'Connection':  'keep-alive',
    'Cookie':  'HJ_UID=2a154a20-1bfa-bb4b-0aa9-2f9b86e896d7; _REF=https://www.baidu.com/link?url=3bNFXFAQ9j0SAEWXW_Dp6zMA5QGS-EU1OMbZMJaP9H-w1VsCsSxTrIsU-Mcfjljy&wd=&eqid=d1ae8cb100015ed9000000065c3fecc6; _REG=www.baidu.com|; _SREG_20=www.baidu.com|; TRACKSITEMAP=20%2C; _SREF_20=https://www.baidu.com/link?url=3bNFXFAQ9j0SAEWXW_Dp6zMA5QGS-EU1OMbZMJaP9H-w1VsCsSxTrIsU-Mcfjljy&wd=&eqid=d1ae8cb100015ed9000000065c3fecc6; Hm_lvt_d4f3d19993ee3fa579a64f42d860c2a7=1548640912,1548640922,1548641117,1550124488; Hm_lpvt_d4f3d19993ee3fa579a64f42d860c2a7=1550124651',
    #'Host':  'www.hjenglish.com',
    #'If-None-Match':  'W/"7cae-tkTpGwNvsgSmOeFrV3/5Hpj3WqI"',
    #'Upgrade-Insecure-Requests':  '1',
    'User-Agent':  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }
    html = requests.get(url, headers=headers,)# proxies=proxies)
    #抓出来的数据不是我们最终的，因为有的是粗体有的不是粗体或者有的会有一些链接，所以有的会有<strong>之类的标签，我们用sub方法去掉这些东西
    preenList = re.findall('<div class="langs_en">(.*?)</div>', html.text)
    precnList = re.findall('<div class="langs_cn">(.*?)</div>', html.text)
    list = [re.sub('<.*?>', '', preenList[i] + '\n' + precnList[i]) for i in range(len(preenList))]
    return list
if __name__=='__main__':
    QueueManger.register("get_task")#注册函数调用服务器
    QueueManger.register("get_result")
    manager = QueueManger(address=("192.168.0.127", 8848), authkey="123456".encode('utf-8'))
    manager.connect()#连接服务器
    task, result = manager.get_task(), manager.get_result()
    for i in range(1000):
        try:
            url = task.get()
            print('client get', url)

            result.put(getResults(url))
        except:
            pass