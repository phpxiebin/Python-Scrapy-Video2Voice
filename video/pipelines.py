# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

class VideoPipeline(object):
    def process_item(self, item, spider):
        return item


import scrapy
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem


# 封面下载管道
class CoverPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['cover'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("项目不包含任何图像")
        item['cover_name'] = image_paths[0].split('/')[1]
        return item


import MySQLdb

# import MySQLdb.cursors

# MYSQL 连接信息
dbuser = 'root'
dbpass = 'root123'
dbname = 'leting'
dbhost = '127.0.0.1'
dbport = '3306'


# mysql数据库操作
class MySQLStorePipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(user=dbuser, passwd=dbpass, db=dbname, host=dbhost, charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    # 当spider被关闭时，调用
    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        print item['website']
        try:
            self.cursor.execute(

                "INSERT INTO `t_audio` (title, cover, audio, source, source_id, duration, website_title, website, release_time, audio_name, cover_name) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    item['title'], item['cover'], item['audio'], item['source'],
                    item['source_id'], item['duration'], item['website_title'], item['website'],
                    item['release_time'], item['audio_name'], item['cover_name'],
                )
            )
            # 提交sql语句
            self.conn.commit()

        except MySQLdb.Error, e:
            print e
        return item
