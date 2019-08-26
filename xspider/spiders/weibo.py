# -*- coding: utf-8 -*-
import re
import datetime
import scrapy
import dateutil.parser

from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider
from lxml import etree

from xspider.spiders.utils import convert_weibo_time, extract_weibo_reply, extract_weibo_tweet
from xspider.items import WeiboTweetItem, WeiboUserItem, WeiboGeoPoint
from xspider.settings import REDIS_KEY


class WeiboSpider(RedisSpider):
    name = 'weibo'
    base_url = "https://weibo.cn"
    allowed_domains = ["weibo.cn"]
    redis_key = REDIS_KEY

    custom_settings = {
        'CONCURRENT_REQUESTS': 10,
        "DOWNLOAD_DELAY": 5,
    }

    def parse(self, response):
        if response.url.endswith('page=1'):
            # if current is page one, then fetch last pages
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_count in range(2, all_page + 1):
                    page_url = response.url.replace(
                        'page=1', 'page={}'.format(page_count))
                    yield Request(page_url, callback=self.parse, dont_filter=True, meta=response.meta)

        # fetch current page
        tree_node = etree.HTML(response.body)
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                tweet_item = WeiboTweetItem()
                tweet_item['crawled_at'] = dateutil.parser.parse(
                    datetime.datetime.utcnow().isoformat())
                tweet_reply_url = tweet_node.xpath(
                    './/a[contains(text(),"转发[")]/@href')[0]
                tweet_ids = re.search(
                    r'/repost/(.*?)\?uid=(\d+)', tweet_reply_url)
                tweet_item['user_id'] = tweet_ids.group(2)
                tweet_item['_id'] = '{}_{}'.format(
                    tweet_ids.group(2), tweet_ids.group(1))
                created_time_info_node = tweet_node.xpath(
                    './/span[@class="ct"]')[-1]
                created_time_info = created_time_info_node.xpath('string(.)')
                if "来自" in created_time_info:
                    tweet_item['created_at'] = convert_weibo_time(
                        created_time_info.split('来自')[0].strip())
                    tweet_item['client'] = created_time_info.split('来自')[
                        1].strip()
                else:
                    tweet_item['created_at'] = convert_weibo_time(
                        created_time_info.strip())

                likes_count = tweet_node.xpath(
                    './/a[contains(text(),"赞[")]/text()')[-1]
                tweet_item['likes_count'] = int(
                    re.search(r'\d+', likes_count).group())

                retweets_count = tweet_node.xpath(
                    './/a[contains(text(),"转发[")]/text()')[-1]
                tweet_item['retweets_count'] = int(
                    re.search(r'\d+', retweets_count).group())

                replies_count = tweet_node.xpath(
                    './/a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()')[-1]
                tweet_item['replies_count'] = int(
                    re.search(r'\d+', replies_count).group())

                images = tweet_node.xpath('.//img[@alt="图片"]/@src')
                if images:
                    tweet_item['image_urls'] = images

                videos = tweet_node.xpath(
                    './/a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    tweet_item['video_urls'] = videos

                map_node = tweet_node.xpath('.//a[contains(text(),"显示地图")]')
                if map_node:
                    map_node = map_node[0]
                    map_node_url = map_node.xpath('./@href')[0]
                    geo_point = re.search(r'xy=(.*?)&', map_node_url).group(1)
                    tweet_item['geo'] = geo_point
                    tweet_item['location'] = map_node.xpath(
                        './preceding-sibling::a/text()')[0]

                retweet_node = tweet_node.xpath(
                    './/a[contains(text(),"原文评论[")]/@href')
                if retweet_node:
                    tweet_item['origin_tweet'] = retweet_node[0]
                else:
                    tweet_item['is_origin'] = True

                user_url = "https://weibo.cn/{}/info".format(
                    tweet_item['user_id'])
                yield Request(url=user_url, callback=self.parse_user_account, dont_filter=True, meta=response.meta, priority=100)

                # fetch whole content when context is incompleted
                all_content_link = tweet_node.xpath(
                    './/a[text()="全文" and contains(@href,"ckAll=1")]')
                if all_content_link:
                    all_content_url = self.base_url + \
                        all_content_link[0].xpath('./@href')[0]
                    yield Request(all_content_url, callback=self.parse_whole_content, meta={'item': tweet_item},
                                  priority=1)
                else:
                    tweet_html = etree.tostring(tweet_node, encoding='unicode')
                    tweet_item['content'] = extract_weibo_tweet(tweet_html)
                    yield tweet_item

            except Exception as e:
                self.logger.error("parse:", e)

    def parse_whole_content(self, response):
        tree_node = etree.HTML(response.body)
        tweet_item = response.meta['item']
        content_node = tree_node.xpath('//*[@id="M_"]/div[1]')[0]
        tweet_html = etree.tostring(content_node, encoding='unicode')
        tweet_item['content'] = extract_weibo_tweet(tweet_html)
        yield tweet_item

    def parse_user_account(self, response):
        account_item = WeiboUserItem()
        account_item['crawled_at'] = dateutil.parser.parse(
            datetime.datetime.utcnow().isoformat())
        selector = Selector(response)
        account_item['_id'] = re.findall(r'(\d+)/info', response.url)[0]
        text1 = ";".join(selector.xpath(
            'body/div[@class="c"]//text()').extract())
        nick_name = re.findall('昵称;?[：:]?(.*?);', text1)
        gender = re.findall('性别;?[：:]?(.*?);', text1)
        place = re.findall('地区;?[：:]?(.*?);', text1)
        briefIntroduction = re.findall('简介;?[：:]?(.*?);', text1)
        birthday = re.findall('生日;?[：:]?(.*?);', text1)
        sex_orientation = re.findall('性取向;?[：:]?(.*?);', text1)
        sentiment = re.findall('感情状况;?[：:]?(.*?);', text1)
        vip_level = re.findall('会员等级;?[：:]?(.*?);', text1)
        authentication = re.findall('认证;?[：:]?(.*?);', text1)
        labels = re.findall('标签;?[：:]?(.*?)更多>>', text1)
        if nick_name and nick_name[0]:
            account_item['name'] = nick_name[0].replace(u"\xa0", "")
        if gender and gender[0]:
            account_item['gender'] = gender[0].replace(u"\xa0", "")
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            account_item['province'] = place[0]
            if len(place) > 1:
                account_item['city'] = place[1]
        if briefIntroduction and briefIntroduction[0]:
            account_item['bio'] = briefIntroduction[0].replace(u"\xa0", "")
        if birthday and birthday[0]:
            account_item['birthday'] = birthday[0]
        if sex_orientation and sex_orientation[0]:
            account_item['sex_orientation'] = sex_orientation[0].replace(
                u"\xa0", "")
        if sentiment and sentiment[0]:
            account_item['sentiment'] = sentiment[0].replace(u"\xa0", "")
        if vip_level and vip_level[0]:
            account_item['vip_level'] = vip_level[0].replace(u"\xa0", "")
        if authentication and authentication[0]:
            account_item['authentication'] = authentication[0].replace(
                u"\xa0", "")
        if labels and labels[0]:
            account_item['labels'] = labels[0].replace(
                u"\xa0", ",").replace(';', '').strip(',')
        yield Request(self.base_url + '/u/{}'.format(account_item['_id']),
                      callback=self.parse_account_detail,
                      meta={'item': account_item}, dont_filter=True, priority=200)

    def parse_account_detail(self, response):
        account_item = response.request.meta['item']
        text = response.text
        tweets_count = re.findall(r'微博\[(\d+)\]', text)
        if tweets_count:
            account_item['tweets_count'] = int(tweets_count[0])
        follows_count = re.findall(r'关注\[(\d+)\]', text)
        if follows_count:
            account_item['follows_count'] = int(follows_count[0])
        followers_count = re.findall(r'粉丝\[(\d+)\]', text)
        if followers_count:
            account_item['followers_count'] = int(followers_count[0])
        yield account_item


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl('weibo_spider')
    process.start()
