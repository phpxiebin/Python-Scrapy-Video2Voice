# -*- coding: utf-8 -*-
import scrapy, re, os, subprocess, time, hashlib, time
from video.items import VideoItem


# 抓取山东广播电视台详情并将视频转音频
class IqiluSpider(scrapy.Spider):
    name = 'iqilu'
    allowed_domains = ['v.iqilu.com']
    start_urls = [
        'http://v.iqilu.com/sdws/zasd/',
        'http://v.iqilu.com/qlpd/mrxw/',
        'http://v.iqilu.com/ggpd/msztc1/',
        'http://v.iqilu.com/ggpd/xwwbc/',
        'http://v.iqilu.com/jcdb/jnxw/',
        'http://v.iqilu.com/jcdb/qdxw/',
        'http://v.iqilu.com/sdws/wswjxw/',
        'http://v.iqilu.com/sdws/sdxwlb/',
    ]

    custom_settings = {
        # 图片保存路径
        'IMAGES_STORE': '/data/wwwroot/default/leting_image/',
        # 90天的图片失效期限
        'IMAGES_EXPIRES': 90,
        # 图片下载管道
        'ITEM_PIPELINES': {
            'video.pipelines.CoverPipeline': 1,
            'video.pipelines.MySQLStorePipeline': 2,
        },
        'SPIDER_MIDDLEWARES': {
            'scrapy_deltafetch.DeltaFetch': 100
        },
        'DELTAFETCH_ENABLED': True,
        # 音频保存路径
        'AUDIO_STORE': '/data/wwwroot/default/leting_audio/'
    }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        "connection": "close"
    }

    def parse(self, response):
        dls = response.xpath('//*[@id="jmzhanshi1"]/dl')
        # 循环解析列表
        for dl in dls:
            item = VideoItem()
            item['website_title'] = response.xpath('//title/text()').extract()[0]
            item['website'] = response.url
            item['source'] = dl.xpath('dt/a/@href').extract()[0]
            item['source_id'] = item['source'].split('.')[-2].split('/')[-1]
            item['title'] = dl.xpath('dt/a/@title').extract()[0]
            item['cover'] = dl.xpath('dt/a/img/@src').extract()[0]
            item['release_time'] = dl.xpath('dd[2]/text()').extract()[0].split(' ')[4].strip('\t')
            item['duration'] = ''

            today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            # 仅获取当天
            if (today == item['release_time']):
                yield scrapy.FormRequest(item['source'], callback=self.parseItems, meta={'item': item},
                                         dont_filter=True, headers=self.default_headers)

    # 获取详情页信息
    def parseItems(self, response):
        item = response.meta['item']
        # mp4视频地址
        item['audio'] = re.findall('"stream_url": "(.*?)"', response.body)[0]
        # 创建md5对象
        hl = hashlib.md5()
        hl.update(item['source'])
        item['audio_name'] = hl.hexdigest() + ".mp3"
        yield item
