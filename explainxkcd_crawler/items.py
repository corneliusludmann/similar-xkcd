# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ExplainXkcdCrawlerItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    xkcd_url = scrapy.Field()
    explain_xkcd_url = scrapy.Field()
    img_url = scrapy.Field()
    img_title_text = scrapy.Field()
    explanation_html = scrapy.Field()
    explanation_text = scrapy.Field()
    explanation_tokens = scrapy.Field()
    transcript_html = scrapy.Field()
    transcript_text = scrapy.Field()
    transcript_tokens = scrapy.Field()
    trivia_html = scrapy.Field()
    trivia_text = scrapy.Field()
    trivia_tokens = scrapy.Field()
    incomplete = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)
