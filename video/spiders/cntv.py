
# -*- coding: utf-8 -*-
import scrapy, re, os, subprocess, time, hashlib
from video.items import VideoItem
import timeFunc

class CntvSpider(scrapy.Spider):
    name = 'cntv'
    allowed_domains = ['http://tv.cntv.cn']
    start_urls = [
        'http://tv.cntv.cn/videoset/C10152',
        'http://tv.cntv.cn/videoset/C10153',
        'http://tv.cntv.cn/videoset/C11268',
        'http://tv.cntv.cn/videoset/C10095',
        'http://tv.cntv.cn/videoset/C10085',
        'http://tv.cntv.cn/videoset/C10097',
        'http://tv.cntv.cn/videoset/C39021',
        'http://tv.cntv.cn/videoset/C11239',
        'http://tv.cntv.cn/videoset/VSET100253310601',
        'http://tv.cntv.cn/videoset/VSET100200238245',
        'http://tv.cntv.cn/video/C11272/',
        'http://tv.cntv.cn/videoset/C11269',
        'http://tv.cntv.cn/videoset/C11271',
        'http://tv.cntv.cn/videoset/C11135',
        'http://tv.cntv.cn/videoset/VSET100257891955',
        'http://tv.cntv.cn/videoset/C11375',
        'http://tv.cntv.cn/videoset/C33926',
        'http://tv.cntv.cn/videoset/C33921',
        'http://tv.cntv.cn/videoset/C10190',
        'http://tv.cntv.cn/videoset/C11094',
        'http://tv.cntv.cn/videoset/C10188',
        'http://tv.cntv.cn/videoset/C11299',
        'http://tv.cntv.cn/videoset/C11085',
        'http://tv.cntv.cn/videoset/VSET100200239215',
        'http://tv.cntv.cn/videoset/C14074',
    ]

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        "connection": "close"
    }

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
        #音频保存路径
        'AUDIO_STORE': '/data/wwwroot/default/leting_audio/'
    }

    def parse(self, response):
        divs = response.xpath('//*[@id="page_body"]/div[4]/div[1]/div[5]/div[2]/div[1]')
        # 循环解析列表
        for div in divs:
            uls = div.xpath('ul')
            for ul in uls:
                lis = ul.xpath('li')
                for li in lis:
                    item = VideoItem()
                    item['website_title'] = response.xpath('//title/text()').extract()[0]
                    item['website'] = response.url
                    item['source'] = 'http://tv.cntv.cn' + li.xpath('a/@href').extract()[0]
                    item['source_id'] = item['source'].split('/')[-1]
                    item['title'] = li.xpath('h3/a/text()').extract()[0]
                    item['cover'] = li.xpath('a/img/@src').extract()[0]
                    item['release_time'] = ''
                    #item['duration'] = ''
                    yield scrapy.FormRequest(item['source'], callback=self.parseItems, meta={'item': item},
                                             dont_filter=True, headers=self.default_headers)

    # 获取详情页信息
    def parseItems(self, response):
        item = response.meta['item']
        # m3u8视频下载地址
        item['audio'] = 'http://cntv.hls.cdn.myqcloud.com/asp/hls/850/0303000a/3/default/' + item['source_id'] + '/850.m3u8'
        # 创建md5对象
        videoSeconds = timeFunc.getSeconds(item['audio'])
        if videoSeconds<180:
            hl = hashlib.md5()
            hl.update(item['source'])
            item['audio_name'] = hl.hexdigest() + ".mp3"
            item['duration'] = videoSeconds
            subprocess.call(
                'ffmpeg -i ' + item['audio'] + ' -f mp3 -vn "' + self.custom_settings['AUDIO_STORE'] + item[
                'audio_name'] + '"',
                shell=True)
            yield item
        else:
            pass

