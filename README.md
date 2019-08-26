# X Spider
A spider written in python, used to fetch information from Sina Weibo.

# Scrapy
This project is based on scrapy, seperated into Cookie and Spider. They are both scrapy project, Cookie is ued to generate cookies for authentication, so Spider can use those cookies to crawl data from target site.

# Cookie
Used to generate cookies for web crawlling.

# Initialize
Used to init start url for crawlling, can start by search key words of tweets.

# Usage
## Search tweets of Weibo by key word
```
python cookie/weibo.py
python init/tweets_by_keyword.py
```