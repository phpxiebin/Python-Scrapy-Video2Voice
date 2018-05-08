# -*- coding: utf-8 -*-
import scrapy, re, os, subprocess, time, hashlib
from video.items import VideoItem


# 抓取荔枝网新闻详情并将视频转音频
class GdtvSpider(scrapy.Spider):
    name = 'gdtv'
    allowed_domains = ['http://v.gdtv.cn/']
    start_urls = ['http://v.gdtv.cn/news/wjxw/',
                  'http://v.gdtv.cn/news/zdbd/',
                  'http://v.gdtv.cn/star/cjly/',
                  'http://v.gdtv.cn/star/gdxwlb/',
                  'http://v.gdtv.cn/star/xwzgf/',
                  'http://v.gdtv.cn/star/zbqq/',
                  'http://v.gdtv.cn/tvs1/jryx/',
                  'http://v.gdtv.cn/ty/zwtyxw/',
                  'http://v.gdtv.cn/ty/wjtyxw/',
                  'http://v.gdtv.cn/ty/zqxsj/',
                  'http://v.gdtv.cn/news/jrjd/',
                  'http://v.gdtv.cn/tvs1/jsbg/']

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

    # 获取视频列表页
    def parse(self, response):
        uls = response.xpath('/html/body/div[3]/div[2]/div[1]/div[2]/ul')
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
                item['release_time'] = li.xpath('div[@class="cdate"]/text()').extract()[0]
                item['duration'] = li.xpath('div[@class="cduration"]/text()').extract()[0]
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
        # 获取视频时长(仅取分钟)、当天日期
        minute = int(item['duration'].split(':')[0])
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        # 播放时长超过6分钟的丢弃，仅获取当天
        if (today == item['release_time']) and (minute < 6):
            subprocess.call(
                'ffmpeg -i ' + item['audio'] + ' -f mp3 -vn "' + self.custom_settings['AUDIO_STORE'] + item[
                    'audio_name'] + '"',
                shell=True)
            yield item
        else:
            pass
