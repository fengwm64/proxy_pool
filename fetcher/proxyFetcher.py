# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
                   2025.02.08: add some freeProxy and delete some useless freeProxy
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import json
from time import sleep
import urllib
from datetime import datetime
import urllib.parse

from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """    
    @staticmethod
    def freeProxy01(page_count=1):
        """ 快代理 https://www.kuaidaili.com """
        categories = ['inha', 'intr', 'fps']
        for category in categories:
            max_page = 1
            page = 1
            while page <= max_page:
                url = f'https://www.kuaidaili.com/free/{category}/{page}'
                sleep(5)
                r = WebRequest().get(url, timeout=10)
                proxies = re.findall(r'\"ip\":\s+\"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\",\s+\"last_check_time\":\s+\"[\d\-\s\:]+\",\s+\"port\"\:\s+\"(\d+)\"', r.text)
                yield from [':'.join(proxy) for proxy in proxies]

                total = re.findall(r'let\s+totalCount\s\=\s+[\'\"](\d+)[\'\"]', r.text)[0]
                max_page = min(int(total)/12, 10)
                page += 1

    @staticmethod
    def freeProxy02():
        """ 云代理 """
        stypes = ('1', '2')
        for stype in stypes:
            url = f'http://www.ip3366.net/free/?stype={stype}'
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

            pages = re.findall(r'<a\s+href=\"\?stype=[12]&page=(\d+)\">\d+</a>', r.text)
            for page in pages:
                url = f'http://www.ip3366.net/free/?stype={stype}&page={page}'
                sleep(1)
                r = WebRequest().get(url, timeout=10)
                proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
                yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy03():
        """ 小幻代理 """
        now = datetime.now()
        url = f'https://ip.ihuan.me/today/{now.year}/{now.month:02}/{now.day:02}/{now.hour:02}.html'
        r = WebRequest().get(url, timeout=10)
        proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', r.text)
        yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy04():
        """ 89免费代理 """
        urls = ['https://www.89ip.cn/']
        while True:
            try:
                url = urls.pop()
            except IndexError:
                break

            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            if not proxies:
                # 没了
                break

            yield from [':'.join(proxy) for proxy in proxies]

            # 下一页
            r = re.findall(r'<a\s+href=\"(index_\d+.html)\"\s+class=\"layui-laypage-next\"\s+data-page=\"\d+\">下一页</a>', r.text)
            if r:
                next_url = urllib.parse.urljoin(url, r[0])
                urls.append(next_url)
                sleep(1)

    @staticmethod
    def freeProxy05():
        """ 稻壳代理 https://www.docip.net/ """
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)
    
    @staticmethod
    def freeProxy06():
        """
        https://proxy-list.org/english/index.php
        :return:
        """
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        request = WebRequest()
        import base64
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                yield base64.b64decode(proxy).decode()

    @staticmethod
    def freeProxy07():
        url = 'https://gh-proxy.com/https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json'
        r = WebRequest().get(url, timeout=10)
        proxies = [f'{proxy["ip"]}:{proxy["port"]}' for proxy in  r.json]
        yield from proxies

    @staticmethod
    def freeProxy08():
        url = 'https://gh-proxy.com/https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt'
        r = WebRequest().get(url, timeout=10)
        proxies = [proxy for proxy in r.text.split('\n') if proxy]
        yield from proxies

    @staticmethod
    def freeProxy09():
        url = 'https://sunny9577.github.io/proxy-scraper/proxies.json'
        r = WebRequest().get(url, timeout=10)
        proxies = [f'{proxy["ip"]}:{proxy["port"]}' for proxy in  r.json]
        yield from proxies

    @staticmethod
    def freeProxy10():
        url = 'https://iproyal.com/free-proxy-list/?page=1&entries=100'

        while True:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</div><div class=\"flex items-center astro-lmapxigl\">(\d+)</div>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]

            next = r.tree.xpath('//a[text()="Next"]/@href')
            if next:
                url = urllib.parse.urljoin(url, next[0])
                sleep(5)
            else:
                break

    @staticmethod
    def freeProxy11():
        urls = ['http://pubproxy.com/api/proxy?limit=5&https=true', 'http://pubproxy.com/api/proxy?limit=5&https=false']
        proxies = set()
        for url in urls:
            for _ in range(10):
                sleep(1)
                r = WebRequest().get(url, timeout=10)
                for proxy in [proxy['ipPort'] for proxy in r.json['data']]:
                    if proxy in proxies:
                        continue
                    yield proxy
                    proxies.add(proxy)

    @staticmethod
    def freeProxy12():
        urls = ['https://freeproxylist.cc/servers/']
        while True:
            try:
                url = urls.pop()
            except IndexError:
                break

            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]

            r = re.findall(r'''<a\s+href='(https://freeproxylist\.cc/servers/\d+\.html)'>&raquo;</a></li>''', r.text)
            if r:
                urls.append(r[0])
                sleep(1)

    @staticmethod
    def freeProxy13():
        url = 'https://hasdata.com/free-proxy-list'
        r = WebRequest().get(url, timeout=10)
        proxies = re.findall(r'<tr><td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d+)</td><td>HTTP', r.text)
        yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy14():
        urls = ['https://www.freeproxy.world/?type=https&anonymity=&country=&speed=&port=&page=1', 'https://www.freeproxy.world/?type=http&anonymity=&country=&speed=&port=&page=1']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>\s*<td>\s*<a href=\"/\?port=\d+\">(\d+)</a>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy01():
        print(_)

# http://nntime.com/proxy-list-01.htm
