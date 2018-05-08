# -*- coding: utf-8 -*-
import scrapy, re, os, subprocess, time, hashlib, time
from video.items import VideoItem
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


# 抓取安徽详情并将视频转音频
class AhtvSpider(scrapy.Spider):
    name = 'ahtv'
    allowed_domains = ['www.ahtv.cn']
    start_urls = [
        'http://www.ahtv.cn/v/lanmu/xayk/',
        'http://www.ahtv.cn/v/lanmu/cjxwc/',
        'http://www.ahtv.cn/v/lanmu/js1sj/',
        'http://www.ahtv.cn/v/lanmu/mrxwb/',
        'http://www.ahtv.cn/v/lanmu/dysj/',
        'http://www.ahtv.cn/v/lanmu/ycx/',
        'http://www.ahtv.cn/v/lanmu/xwdyx/',
        'http://www.ahtv.cn/v/lanmu/ahxwlb/split/',
        'http://www.ahtv.cn/v/lanmu/yx60/',
        'http://www.ahtv.cn/v/lanmu/xwgsh/',
        'http://www.ahtv.cn/v/lanmu/xwwbc/',
        'http://www.ahtv.cn/v/lanmu/dyxc/',
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
        uls = response.xpath('//*[@id="f02"]/div[1]/div/ul')
        # 循环解析列表
        for ul in uls:
            lis = ul.xpath('li')
            for li in lis:
                item = VideoItem()
                item['website_title'] = response.xpath('//title/text()').extract()[0]
                item['website'] = response.url
                item['source'] = li.xpath('a/@href').extract()[0]
                item['source_id'] = item['source'].split('.')[-2].split('/')[-1]
                item['title'] = li.xpath('a/@title').extract()[0]
                item['cover'] = li.xpath('a/img/@src').extract()[0]
                item['duration'] = li.xpath('p[2]/span/text()').extract()[0].replace('片长：', '')
                item['release_time'] = li.xpath('p[3]/span/text()').extract()[0]

                yield scrapy.FormRequest(item['source'], callback=self.parseItems, meta={'item': item},
                                             dont_filter=True, headers=self.default_headers)

    # 获取详情页信息
    def parseItems(self, response):
        item = response.meta['item']
        # 获取视频来源m3u8链接
        item['audio'] = re.findall('id="m3u8"  value="(.*?)" />', response.body)[0]
        # 创建md5对象
        hl = hashlib.md5()
        hl.update(item['source'])
        item['audio_name'] = hl.hexdigest() + ".mp3"
        yield item
