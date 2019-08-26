# -*- coding: utf-8 -*-
import pymongo
from pymongo.errors import DuplicateKeyError
from xspider.items import WeiboUserItem, WeiboReplyItem, WeiboTweetItem
from xspider.settings import MONGO_HOST, MONGO_PORT, MONGO_DATABASE, MONGO_USERNAME, MONGO_PASSWORD

class MongoPipeline(object):
    def __init__(self):
        db = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)[MONGO_DATABASE]
        db.authenticate(MONGO_USERNAME, MONGO_PASSWORD)
        self.WeiboAccounts = db["weibo.accounts"]
        self.WeiboTweets = db["weibo.tweets"]
        self.WeiboReplies = db["weibo.replies"]

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, WeiboUserItem):
            self.insert_item(self.WeiboAccounts, item)
        elif isinstance(item, WeiboTweetItem):
            self.insert_item(self.WeiboTweets, item)
        elif isinstance(item, WeiboReplyItem):
            self.insert_item(self.WeiboTweets, item)
        return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert_one(dict(item))
        except DuplicateKeyError:
            pass
        except Exception as err:
            print("[mongo]", err)

class ElasticPipeline(object):

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, WeiboUserItem):
            item.save_to_elastic()
        elif isinstance(item, WeiboTweetItem):
            item.save_to_elastic()
        # elif isinstance(item, WeiboReplyItem):
        #     self.insert_item(self.WeiboTweets, item)
        return item
