# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PicspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tag = scrapy.Field()
    image_urls = scrapy.Field()
    images_data = scrapy.Field()
    img_path = scrapy.Field()
    img_big_path = scrapy.Field()
    file_path = scrapy.Field()
