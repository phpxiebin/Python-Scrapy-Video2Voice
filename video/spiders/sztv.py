# -*- coding: utf-8 -*-
import scrapy

# 抓取深圳台详情并将视频转音频
class SztvSpider(scrapy.Spider):
    name = 'sztv'
    allowed_domains = ['api.scms.sztv.com.cn']
    start_urls = [
        'https://api.scms.sztv.com.cn:8443/api/com/article/getArticleList?tenantId=ysz&specialtype=1&banner=1&catalogId=7901&page=1'
    ]

    def parse(self, response):
        print response.body
