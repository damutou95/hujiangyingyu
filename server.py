# -*- coding: utf-8 -*-
import multiprocessing
import multiprocessing.managers
import random, time
from requests.exceptions import ProxyError
import queue
import requests
from lxml import etree
import re
import logging
import pymysql
from urllib import parse
def getUrl():
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

    startUrl = 'http://www.hjenglish.com/new/zt/hjdaily/'
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

    # 返回一个代理列表
    def getProxyfromsql():
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
        return proxies

    def getProxy(proxies):
        proxy = random.choice(proxies)
        proxies = {
            "http": proxy,
            "https": proxy
        }
        return proxies

    # 产生一个列表实例
    proxies = getProxyfromsql()

    for i in range(5):
        try:
            html = requests.get(startUrl, headers=headers, )#proxies=getProxy(proxies))
            break
        except ProxyError:
            proxies = getProxyfromsql()
            logging.info('##############刷新代理')
            continue
    urlMorelist = re.findall('href="(http://www.hjenglish.com/new/tag/\w+?/)"', html.text)
    #print(urlMorelist)
    urlNewslist = []

    for url in urlMorelist:
        for i in range(10):
            try:
                html2 = requests.get(url, headers=headers,)# proxies=getProxy(proxies))
                break
            except ProxyError:
                proxies = getProxyfromsql()
                logging.info('##############刷新代理')
                continue

        #抓出第一页所有的地址为相对地址
        preurlNewslist = re.findall('href="(/\w+?/p\d+?/)"', html2.text)
        urlNewslist = urlNewslist + [parse.urljoin(startUrl, x) for x in preurlNewslist]
        #不断抽取下一页的网址
        while 'l-next' in html2.text:
            #先抽出下一页的相对网址
            preurl = re.findall('href="(/\w+?/\w+?/\w+?/page\d+?)" class="l-next"', html2.text)[0]
            url = parse.urljoin(startUrl, preurl)
            print('下一页网址' + url)
            for i in range(10):
                try:
                    html2 = requests.get(url, headers=headers,)# proxies=getProxy(proxies))
                    break
                except ProxyError:
                    proxies = getProxyfromsql()
                    logging.info('##############刷新代理')
                    continue
            preurlNewslist = re.findall('href="(/new/p\d+?/)"', html2.text)
            urlNewslist = urlNewslist + [parse.urljoin(startUrl, x) for x in preurlNewslist]
        #print(urlNewslist)
    return urlNewslist


task_queue = queue.Queue()
result_queue = queue.Queue()


def return_task():
    return task_queue

def return_result():
    return result_queue


class QueueManger(multiprocessing.managers.BaseManager):
    pass


if __name__=='__main__':
    multiprocessing.freeze_support()#开启分布式支持
    QueueManger.register("get_task", callable=return_task)#注册函数给客户端调用
    QueueManger.register("get_result", callable=return_result)
    manager = QueueManger(address=("192.168.0.127", 8848), authkey="123456".encode('utf-8'))#创建一个管理器
    manager.start()
    task, result = manager.get_task(), manager.get_result()
    urls = getUrl()
    for url in urls:
        print("put url ", url)
        task.put(url)
    print('waitint for---------')
    with open('/home/xiyujing/文档/ceshi3.txt', 'a') as f:
        for url in urls:
            res = result.get()
            for i in res:
                f.write(i+'\n')

    manager.shutdown()#关闭服务器


