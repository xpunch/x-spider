#!/usr/bin/env python
# encoding: utf-8
import redis
import sys
import os
import datetime

sys.path.append(os.getcwd())
from xspider.settings import REDIS_HOST, REDIS_PORT, REDIS_KEY, REDIS_PASSWORD

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)
for key in r.scan_iter(REDIS_KEY):
    r.delete(key)

url_format = "https://weibo.cn/search/mblog?hideSearchFrame=&keyword={}&advancedfilter=1&starttime={}&endtime={}&sort=time&page=1"
# 搜索的关键词，可以修改
keyword = "文创"
# 搜索的起始日期，可修改 微博的创建日期是2009-08-16 也就是说不要采用这个日期更前面的日期了
date_start = datetime.datetime.strptime("2019-08-24", '%Y-%m-%d')
# 搜索的结束日期，可修改
date_end = datetime.datetime.strptime("2019-08-25", '%Y-%m-%d')
time_spread = datetime.timedelta(days=1)
while date_start < date_end:
    next_time = date_start + time_spread
    url = url_format.format(keyword, date_start.strftime(
        "%Y%m%d"), next_time.strftime("%Y%m%d"))
    r.lpush(REDIS_KEY, url)
    date_start = next_time
