FROM toru2220/scrapy-chrome

LABEL org.label-schema.docker.dockerfile="Dockerfile" \
    org.label-schema.name="xpunch" \
    org.label-schema.url="http://phytro.com" \
    maintainer="XPunch Team<chengqiaosheng@gmail.com>"

ADD . .

RUN pip install python-dateutil redis scrapy_redis pymongo elasticsearch-dsl==6.4.0

CMD ["scrapy" ,"crawl" , "weibo"]