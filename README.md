
ProxyPool 爬虫代理IP池
=======


    ______                        ______             _
    | ___ \_                      | ___ \           | |
    | |_/ / \__ __   __  _ __   _ | |_/ /___   ___  | |
    |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | |
    | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___
    \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____\
                           __ / /
                          /___ /

### ProxyPool

[![](https://img.shields.io/badge/Python-2.7-green.svg)](https://docs.python.org/2.7/)
[![](https://img.shields.io/badge/Python-3.5-blue.svg)](https://docs.python.org/3.5/)
[![](https://img.shields.io/badge/Python-3.6-blue.svg)](https://docs.python.org/3.6/)
[![](https://img.shields.io/badge/Python-3.7-blue.svg)](https://docs.python.org/3.7/)
[![](https://img.shields.io/badge/Python-3.8-blue.svg)](https://docs.python.org/3.8/)
[![](https://img.shields.io/badge/Python-3.9-blue.svg)](https://docs.python.org/3.9/)
[![](https://img.shields.io/badge/Python-3.10-blue.svg)](https://docs.python.org/3.10/)
[![](https://img.shields.io/badge/Python-3.11-blue.svg)](https://docs.python.org/3.11/)

爬虫代理IP池项目,主要功能为定时采集网上发布的免费代理验证入库，定时验证入库的代理保证代理的可用性，提供API和CLI两种使用方式。同时你也可以扩展代理源以增加代理池IP的质量和数量。

本项目 fork 自大佬 [@jhao104](https://github.com/jhao104) 的项目 [proxy_pool](https://github.com/jhao104/proxy_pool)，但是原项目已经许久没有更新，我在原项目的issu和pull request收集了一些更新，更新了一下新的免费代理获取方式、修复了匿名度获取、地区获取功能。


### 运行项目

### Docker Image

```bash
docker pull oixel64/proxy_pool:master

docker run --env DB_CONN=redis://:password@ip:port/0 -p 5010:5010 docker.xuanyuan.me/oixel64/proxy_pool
```
### docker-compose

项目目录下运行: 
``` bash
docker-compose up -d
```

### 使用

* Api

启动web服务后, 默认配置下会开启 http://127.0.0.1:5010 的api接口服务:

| api | method | Description | params|
| ----| ---- | ---- | ----|
| / | GET | api介绍 | None |
| /get | GET | 随机获取一个代理| 可选参数: `?type=https` 过滤支持https的代理|
| /pop | GET | 获取并删除一个代理| 可选参数: `?type=https` 过滤支持https的代理|
| /all | GET | 获取所有代理 |可选参数: `?type=https` 过滤支持https的代理|
| /count | GET | 查看代理数量 |None|
| /delete | GET | 删除代理  |`?proxy=host:ip`|


* 爬虫使用

　　如果要在爬虫代码中使用的话， 可以将此api封装成函数直接使用，例如：

```python
# proxy.py
import requests
from pprint import pprint

class ProxyPool:
    def __init__(self, host='127.0.0.1', port=5010):
        """
        初始化代理池
        :param host: 代理池服务地址
        :param port: 代理池服务端口
        """
        self.base_url = f"http://{host}:{port}"
    
    def _make_request(self, endpoint, params=None):
        """
        内部请求方法
        :param endpoint: API端点
        :param params: 请求参数
        :return: 响应数据或None
        """
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=5
            )
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            print(f"请求代理池API失败: {str(e)}")
            return None
    
    def get_api_info(self):
        """
        获取API介绍信息
        :return: API介绍信息
        """
        return self._make_request("/")
    
    def test_proxy(cls, proxy, test_url='https://www.baidu.com', max_retries=5):
        """
        测试代理是否可用，最多重试 max_retries 次
        :param proxy: 代理字符串（host:port）
        :param test_url: 测试的 URL（默认为 https://www.baidu.com）
        :param max_retries: 最大重试次数（默认 5）
        :return: True（可用） / False（不可用）
        """
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        
        failure_count = 0  # 记录连续失败的次数
        
        while failure_count < max_retries:
            try:
                response = requests.get(test_url, proxies=proxies, timeout=10)
                
                # 如果状态码是 2xx，则认为代理可用
                if response.status_code // 100 == 2:
                    return True
                else:
                    failure_count += 1  # 状态码不是 2xx，增加失败次数
            
            except requests.exceptions.RequestException as e:
                failure_count += 1  # 网络请求异常，增加失败次数
        
        # 如果重试超过最大次数，认为代理不可用
        return False

    def get_proxy(self, proxy_type=None, need_test=True):
        """
        随机获取一个代理并测试其可用性
        :param proxy_type: 代理类型（可选，如'https'）
        :param need_test: 是否需要测试代理的可用性，默认为 True
        :return: 可用的代理字符串（host:port），如果没有找到可用代理，则返回 None
        """
        # 从代理源获取一个代理
        params = {'type': proxy_type} if proxy_type else None
        result = self._make_request("/get/", params)
        proxy = result.get("proxy") if result else None

        if proxy:
            if need_test:
                # 测试获取到的代理是否可用
                if self.test_proxy(proxy):
                    return proxy
                else:
                    self.delete_proxy(proxy)  # 删除不可用代理
                    return self.get_proxy(proxy_type, need_test)  # 递归获取新代理
            else:
                return proxy
        return None
    
    def pop_proxy(self, proxy_type=None):
        """
        获取并删除一个代理
        :param proxy_type: 代理类型（可选，如'https'）
        :return: 代理字符串（host:port）或None
        """
        params = {'type': proxy_type} if proxy_type else None
        result = self._make_request("/pop/", params)
        return result.get("proxy") if result else None
    
    def get_all_proxies(self, proxy_type=None):
        """
        获取所有代理
        :param proxy_type: 代理类型（可选，如'https'）
        :return: 代理列表或None
        """
        params = {'type': proxy_type} if proxy_type else None
        result = self._make_request("/all/", params)

        if isinstance(result, list):
            return result  # 直接返回列表
        else:
            print("返回数据格式错误，预期为列表:", result)
            return None
    
    def get_proxy_count(self):
        """
        获取代理数量
        :return: 代理数量（整数）
        """
        result = self._make_request("/count/")
        return result.get("count", 0) if result else 0
    
    def delete_proxy(self, proxy):
        """
        删除指定代理
        :param proxy: 要删除的代理（host:port格式）
        :return: True（删除成功） / False（删除失败）
        """
        result = self._make_request("/delete/", {'proxy': proxy})
        return result.get("src") == 1 if isinstance(result, dict) else False

# 示例代码
# 初始化代理池
# proxy_pool = ProxyPool(host='192.168.123.2', port=5010)

# 1. 获取API介绍
# print("API介绍:", proxy_pool.get_api_info())

# 2. 获取随机代理
# random_proxy = proxy_pool.get_proxy('https')
# print("随机代理:", random_proxy)

# 3. 获取并删除一个HTTPS代理
# https_proxy = proxy_pool.pop_proxy('https')
# print("获取并删除的HTTPS代理:", https_proxy)

# 4. 获取所有HTTP代理
# http_proxies = proxy_pool.get_all_proxies('https')
# if http_proxies:
#     print("所有HTTP代理:")
#     pprint(http_proxies, sort_dicts=False)  # `sort_dicts=False` 保持原顺序
# else:
#     print("未获取到代理")

# 5. 获取代理数量
# proxy_count = proxy_pool.get_proxy_count()
# print("当前代理数量:", proxy_count)

# 6. 删除指定代理
# if random_proxy:
#     delete_result = proxy_pool.delete_proxy(random_proxy)
#     print(f"删除代理 {random_proxy} 结果:", "成功" if delete_result else "失败")
```

### 扩展代理

　　项目默认包含几个免费的代理获取源，但是免费的毕竟质量有限，所以如果直接运行可能拿到的代理质量不理想。所以，提供了代理获取的扩展方法。

　　添加一个新的代理源方法如下:

* 1、首先在[ProxyFetcher](https://github.com/jhao104/proxy_pool/blob/1a3666283806a22ef287fba1a8efab7b94e94bac/fetcher/proxyFetcher.py#L21)类中添加自定义的获取代理的静态方法，
该方法需要以生成器(yield)形式返回`host:ip`格式的代理，例如:

```python

class ProxyFetcher(object):
    # ....

    # 自定义代理源获取方法
    @staticmethod
    def freeProxyCustom1():  # 命名不和已有重复即可

        # 通过某网站或者某接口或某数据库获取代理
        # 假设你已经拿到了一个代理列表
        proxies = ["x.x.x.x:3128", "x.x.x.x:80"]
        for proxy in proxies:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
```

* 2、添加好方法后，修改[setting.py](https://github.com/jhao104/proxy_pool/blob/1a3666283806a22ef287fba1a8efab7b94e94bac/setting.py#L47)文件中的`PROXY_FETCHER`项：

　　在`PROXY_FETCHER`下添加自定义方法的名字:

```python
PROXY_FETCHER = [
    "freeProxy01",    
    "freeProxy02",
    # ....
    "freeProxyCustom1"  #  # 确保名字和你添加方法名字一致
]
```


　　`schedule` 进程会每隔一段时间抓取一次代理，下次抓取时会自动识别调用你定义的方法。

### 免费代理源

   目前实现的采集免费代理网站有(排名不分先后, 下面仅是对其发布的免费代理情况, 付费代理测评可以参考[这里](https://zhuanlan.zhihu.com/p/33576641)): 
   
  | 代理名称          |  状态  |  更新速度 |  可用率  |  地址 | 代码                                             |
  |---------------|  ---- | --------  | ------  | ----- |------------------------------------------------|
  | 站大爷           |  ✔    |     ★     |   **     | [地址](https://www.zdaye.com/)    | [`freeProxy01`](/fetcher/proxyFetcher.py#L28)  |
  | 66代理          |  ✔    |     ★     |   *     | [地址](http://www.66ip.cn/)         | [`freeProxy02`](/fetcher/proxyFetcher.py#L50)  |
  | 开心代理          |   ✔   |     ★     |   *     | [地址](http://www.kxdaili.com/)     | [`freeProxy03`](/fetcher/proxyFetcher.py#L63)  |
  | FreeProxyList |   ✔  |    ★     |   *    | [地址](https://www.freeproxylists.net/zh/) | [`freeProxy04`](/fetcher/proxyFetcher.py#L74)  |
  | 快代理           |  ✔    |     ★     |   *     | [地址](https://www.kuaidaili.com/)  | [`freeProxy05`](/fetcher/proxyFetcher.py#L92)  |
  | 冰凌代理          |  ✔    |    ★★★    |   *     | [地址](https://www.binglx.cn/) | [`freeProxy06`](/fetcher/proxyFetcher.py#L111) |
  | 云代理           |  ✔    |    ★     |   *     | [地址](http://www.ip3366.net/)      | [`freeProxy07`](/fetcher/proxyFetcher.py#L123) |
  | 小幻代理          |  ✔    |    ★★    |    *    | [地址](https://ip.ihuan.me/)        | [`freeProxy08`](/fetcher/proxyFetcher.py#L133) |
  | 免费代理库         |  ✔    |     ☆     |    *    | [地址](http://ip.jiangxianli.com/)   | [`freeProxy09`](/fetcher/proxyFetcher.py#L143) |
  | 89代理          |  ✔    |     ☆     |   *     | [地址](https://www.89ip.cn/)         | [`freeProxy10`](/fetcher/proxyFetcher.py#L154) |
  | 稻壳代理          |  ✔    |     ★★    |   ***   | [地址](https://www.docip.ne)         | [`freeProxy11`](/fetcher/proxyFetcher.py#L164) |

  
  如果还有其他好的免费代理网站, 可以在提交在[issues](https://github.com/jhao104/proxy_pool/issues/71), 下次更新时会考虑在项目中支持。

### 问题反馈

　　任何问题欢迎在[Issues](https://github.com/fengwm64/proxy_pool/issues) 中反馈，但是本人能力有限，只能尽力尝试解决。

### 贡献代码

　　本项目依然不够完善，如果发现bug或有新的功能添加，请在[Issues](https://github.com/fengwm64/proxy_pool/issues)中提交bug(或新功能)描述，我会尽力改进，使她更加完美。

　　这里感谢以下contributor的无私奉献：

　　[@jhao104](https://github.com/jhao104) | [@kangnwh](https://github.com/kangnwh) | [@bobobo80](https://github.com/bobobo80) | [@halleywj](https://github.com/halleywj) | [@newlyedward](https://github.com/newlyedward) | [@wang-ye](https://github.com/wang-ye) | [@gladmo](https://github.com/gladmo) | [@bernieyangmh](https://github.com/bernieyangmh) | [@PythonYXY](https://github.com/PythonYXY) | [@zuijiawoniu](https://github.com/zuijiawoniu) | [@netAir](https://github.com/netAir) | [@scil](https://github.com/scil) | [@tangrela](https://github.com/tangrela) | [@highroom](https://github.com/highroom) | [@luocaodan](https://github.com/luocaodan) | [@vc5](https://github.com/vc5) | [@1again](https://github.com/1again) | [@obaiyan](https://github.com/obaiyan) | [@zsbh](https://github.com/zsbh) | [@jiannanya](https://github.com/jiannanya) | [@Jerry12228](https://github.com/Jerry12228)


### Release Notes

   [changelog](https://github.com/fengwm64/proxy_pool/blob/master/docs/changelog.rst)
