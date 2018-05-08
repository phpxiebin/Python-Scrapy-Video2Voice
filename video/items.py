# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VideoItem(scrapy.Item):
    # 标题
    title = scrapy.Field()
    # 封面
    cover = scrapy.Field()
    # 音频地址 m3u8地址
    audio = scrapy.Field()
    # 描述
    describe = scrapy.Field()
    # 来源地址
    source = scrapy.Field()
    # 来源Id
    source_id = scrapy.Field()
    # 时长
    duration = scrapy.Field()
    # 分类
    category = scrapy.Field()
    # 内容详情
    details = scrapy.Field()
    # 来源网站标题
    website_title = scrapy.Field()
    # 来源标题
    website = scrapy.Field()
    # 标签
    tags = scrapy.Field()
    # 发布时间
    release_time = scrapy.Field()
    # 本地音频文件名
    audio_name = scrapy.Field()
    # 本地封面文件名
    cover_name = scrapy.Field()
