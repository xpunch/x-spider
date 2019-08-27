
import os
import sys
from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, analyzer, Completion, Keyword, Text, Integer, GeoPoint
from elasticsearch_dsl.connections import connections

sys.path.append(os.getcwd())
from xspider.settings import ELASTIC_HOST, ELASTIC_USERNAME, ELASTIC_PASSWORD
connections.create_connection(hosts=[ELASTIC_HOST], http_auth='{}:{}'.format(
    ELASTIC_USERNAME, ELASTIC_PASSWORD))


class WeiboTweetDoc(Document):
    id = Keyword()
    url = Text(fields={'key': Keyword()})
    uid = Keyword()
    content = Text(analyzer="ik_max_word", search_analyzer="ik_max_word", fields={
                   'key': Keyword()})
    likes_count = Integer()
    retweets_count = Integer()
    replies_count = Integer()
    client = Text(analyzer="ik_max_word", search_analyzer="ik_max_word", fields={
        'key': Keyword(), })
    image_urls = Text()
    video_urls = Text()
    location = Text(analyzer="ik_max_word", search_analyzer="ik_max_word", fields={
        'key': Keyword(), })
    geo = GeoPoint()
    is_origin = Boolean()
    origin_tweet = Text()
    tags = Text(analyzer="ik_max_word", search_analyzer="ik_max_word", fields={
        'key': Keyword(), })
    created_at = Date()

    class Index:
        name = "weibo_tweets"


class WeiboUserDoc(Document):
    id = Keyword()
    name = Text(analyzer="ik_max_word", search_analyzer="ik_max_word", fields={
        'key': Keyword(), })
    gender = Text(fields={'key': Keyword(), })
    province = Text(fields={'key': Keyword(), })
    city = Text(fields={'key': Keyword(), })
    bio = Text(analyzer="ik_max_word", search_analyzer="ik_max_word", fields={
        'key': Keyword(), })
    birthday = Text(fields={'key': Keyword(), })
    tweets_count = Integer()
    follows_count = Integer()
    followers_count = Integer()
    sex_orientation = Text(fields={'key': Keyword(), })
    sentiment = Text(fields={'key': Keyword(), })
    vip_level = Text(fields={'key': Keyword(), })
    authentication = Text(fields={'key': Keyword(), })
    website = Text()
    labels = Text(analyzer="ik_max_word", search_analyzer="ik_max_word", fields={
        'key': Keyword(), })
    tags = Text(analyzer="ik_max_word", search_analyzer="ik_max_word", fields={
        'key': Keyword(), })

    class Index:
        name = "weibo_users"


if __name__ == "__main__":
    WeiboTweetDoc.init()
    WeiboUserDoc.init()
