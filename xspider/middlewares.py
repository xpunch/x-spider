# encoding: utf-8
import random
import pymongo
from xspider.settings import MONGO_HOST, MONGO_PORT, MONGO_DATABASE, MONGO_USERNAME, MONGO_PASSWORD


class CookieMiddleware(object):
    def __init__(self):
        db = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)[MONGO_DATABASE]
        db.authenticate(MONGO_USERNAME, MONGO_PASSWORD)
        self.collection = db["weibo.cookies"]

    def process_request(self, request, spider):
        count = self.collection.find({'status': 'success'}).count()
        if count == 0:
            raise Exception('当前账号池为空')
        random_index = random.randint(0, count - 1)
        random_cookie = self.collection.find(
            {'status': 'success'})[random_index]
        request.headers.setdefault('Cookie', random_cookie['cookie'])
        request.meta['account'] = random_cookie


class RedirectMiddleware(object):
    """
    检测账号是否正常
    302 / 403,说明账号cookie失效/账号被封，状态标记为error
    418,偶尔产生,需要再次请求
    """

    def __init__(self):
        db = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)[MONGO_DATABASE]
        db.authenticate(MONGO_USERNAME, MONGO_PASSWORD)
        self.collection = db["weibo.cookies"]

    def process_response(self, request, response, spider):
        http_code = response.status
        if http_code == 302 or http_code == 403:
            self.collection.find_one_and_update({'_id': request.meta['account']['_id']},
                                                {'$set': {'status': 'error'}}, )
            return request
        elif http_code == 418:
            spider.logger.error('ip 被封了!!!请更换ip,或者停止程序...')
            return request
        else:
            return response


class IPProxyMiddleware(object):

    def fetch_proxy(self):
        # 如果需要加入代理IP，请重写这个函数
        # 这个函数返回一个代理ip，'ip:port'的格式，如'12.34.1.4:9090'
        return None

    def process_request(self, request, spider):
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = f'http://{proxy_data}'
            spider.logger.debug(f"当前代理IP:{current_proxy}")
            request.meta['proxy'] = current_proxy
