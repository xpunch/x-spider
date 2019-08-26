import os
import sys
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, analyzer, Completion, Keyword, Text, Integer, GeoPoint
from elasticsearch_dsl.connections import connections

sys.path.append(os.getcwd())
from xspider.settings import ELASTIC_HOST, ELASTIC_USERNAME, ELASTIC_PASSWORD

connections.create_connection(hosts=[ELASTIC_HOST], http_auth='{}:{}'.format(
    ELASTIC_USERNAME, ELASTIC_PASSWORD))


class WeiboTweetDoc(DocType):
    id = Keyword()
    url = Text()
    uid = Keyword()
    content = Text()
    likes_count = Integer()
    retweets_count = Integer()
    replies_count = Integer()
    client = Text()
    image_urls = Text()
    video_urls = Text()
    location = Text()
    geo = GeoPoint()
    is_origin = Boolean()
    origin_tweet = Text()
    tags = Text()
    created_at = Date()

    class Index:
        name = "weibo_tweets_2019_08_25_2"

class WeiboUserDoc(DocType):
    id = Keyword()
    name = Text()
    gender = Text()
    province = Text()
    city = Text()
    bio = Text()
    birthday = Text()
    tweets_count = Integer()
    follows_count = Integer()
    followers_count = Integer()
    sex_orientation = Text()
    sentiment = Text()
    vip_level = Text()
    authentication = Text()
    website = Text()
    labels = Text()
    tags = Text()

    class Index:
        name = "weibo_users"

if __name__ == "__main__":
    WeiboTweetDoc.init()
    WeiboUserDoc.init()
