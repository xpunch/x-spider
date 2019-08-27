# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from xspider.itemselastic import WeiboTweetDoc, WeiboUserDoc
import geohash


class WeiboTweetItem(Item):
    _id = Field()
    user_id = Field()
    content = Field()
    likes_count = Field()
    retweets_count = Field()
    replies_count = Field()
    client = Field()
    image_urls = Field()
    video_urls = Field()
    location = Field()
    geo = Field()
    is_origin = Field()
    origin_tweet = Field()
    tags = Field()
    created_at = Field()
    crawled_at = Field()

    def save_to_elastic(self):
        doc = WeiboTweetDoc()
        doc.id = self["_id"]
        doc.uid = self["user_id"]
        doc.content = self["content"]
        doc.likes_count = self["likes_count"]
        doc.retweets_count = self["retweets_count"]
        doc.replies_count = self["replies_count"]
        if "client" in self:
            doc.client = self["client"]
        if "image_urls" in self:
            doc.image_urls = self["image_urls"]
        if "video_urls" in self:
            doc.video_urls = self["video_urls"]
        if "location" in self:
            doc.location = self["location"]
        if "geo" in self:
            geo = self['geo'].split(",")
            doc.geo = [float(geo[0]),float(geo[1])]
        if "is_orgin" in self:
            doc.is_orgin = self["is_orgin"]
        if "orgin_tweet" in self:
            doc.origin_tweet = self["orgin_tweet"]
        if "tags" in self:
            doc.tags = self["tags"]
        if "created_at" in self:
            doc.created_at = self["created_at"]
        doc.save()
        return


class WeiboUserItem(Item):
    _id = Field()
    name = Field()
    gender = Field()
    province = Field()
    city = Field()
    bio = Field()
    birthday = Field()
    tweets_count = Field()
    follows_count = Field()
    followers_count = Field()
    sex_orientation = Field()
    sentiment = Field()
    vip_level = Field()
    authentication = Field()
    website = Field()
    labels = Field()
    tags = Field()
    crawled_at = Field()

    def save_to_elastic(self):
        doc = WeiboUserDoc()
        doc.id = self['_id']
        doc.name = self['name']
        if 'gender' in self:
            doc.gender = self['gender']
        if 'province' in self:
            doc.province = self['province']
        if 'city' in self:
            doc.city = self['city']
        if 'bio' in self:
            doc.bio = self['bio']
        # birthday = Date()
        doc.tweets_count = self['tweets_count']
        doc.follows_count = self['follows_count']
        doc.followers_count = self['followers_count']
        if 'sex_orientation' in self:
            doc.sex_orientation = self['sex_orientation']
        if 'sentiment' in self:
            doc.sentiment = self['sentiment']
        if 'vip_level' in self:
            doc.vip_level = self['vip_level']
        if 'authentication' in self:
            doc.authentication = self['authentication']
        if 'website' in self:
            doc.website = self['website']
        if 'labels' in self:
            doc.labels = self['labels']
        doc.save()
        return


class WeiboReplyItem(Item):
    _id = Field()
    user_id = Field()
    content = Field()
    tweet_url = Field()
    likes_count = Field()
    tags = Field()
    created_at = Field()
    crawled_at = Field()


class WeiboGeoPoint(Field):
    lat = Field()
    lon = Field()
