# -*- coding: utf-8 -*-

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, Identity


class ExplainXkcdCrawlerItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    explanation_html_in = Join()
    explanation_text_in = Join()
    explanation_tokens_in = Identity()
    transcript_html_in = Join()
    transcript_text_in = Join()
    transcript_tokens_in = Identity()
    trivia_html_in = Join()
    trivia_text_in = Join()
    trivia_tokens_in = Identity()
