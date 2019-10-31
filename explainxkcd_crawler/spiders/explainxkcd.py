# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy
from explainxkcd_crawler.items import ExplainXkcdCrawlerItem
from explainxkcd_crawler.item_loader import ExplainXkcdCrawlerItemLoader
from bs4 import BeautifulSoup


class ExplainXkcdSpider(scrapy.Spider):
    name = 'explainxkcd'
    allowed_domains = ['explainxkcd.com']

    def __init__(self, start_id):
        self.start_urls = [
            'http://explainxkcd.com/wiki/index.php/' + str(start_id)
        ]

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.get('START_ID'))

    def parse(self, response):
        first_heading = response.xpath("//h1[@id='firstHeading']/text()").get()
        id = first_heading.split(": ")[0]
        title = first_heading.split(": ")[1]

        # Kayessian (after Dr. Michael Kay) formula for node-set intersection
        # see: http://stackoverflow.com/questions/14074462/get-siblings-from-header-until-next-header-in-an-unsemantic-table
        # or: http://stackoverflow.com/questions/4767430/xpath-axis-get-all-following-nodes-until
        # or: http://stackoverflow.com/questions/3428104/selecting-siblings-between-two-nodes-using-xpath
        # A - B = $A[count(.|$B)!=count($B)]
        kayessian_pattern = "{0}[count(.|{1})=count({1})]"

        start_explanation_xpath = "h2[contains(., 'Explanation')]"
        start_transcript_xpath = "h2[contains(., 'Transcript')]"
        start_trivia_xpath = "h2[contains(., 'Trivia')]"
        start_discussion_xpath = "h1[contains(., 'Discussion')]"

        sibling = "/following-sibling::node()[not(contains(@class, 'notice_tpl'))]"
        preceding = "/preceding-sibling::node()"

        explanation_xpath = kayessian_pattern.format(
            "//" + start_explanation_xpath + sibling,
            "../" + start_explanation_xpath + sibling +
            "[self::h2|self::h1|self::span[@id='Discussion']][1]" + preceding)
        transcript_xpath = kayessian_pattern.format(
            "//" + start_transcript_xpath + sibling,
            "../" + start_transcript_xpath + sibling +
            "[self::h2|self::h1|self::span[@id='Discussion']][1]" + preceding)
        trivia_xpath = kayessian_pattern.format(
            "//" + start_trivia_xpath + sibling,
            "../" + start_trivia_xpath + sibling +
            "[self::h2|self::h1|self::span[@id='Discussion']][1]" + preceding)

        item = ExplainXkcdCrawlerItemLoader(item=ExplainXkcdCrawlerItem(),
                                            response=response)
        item.add_value("id", id)
        item.add_value("title", title)
        item.add_xpath("xkcd_url", "//li[@class='plainlinks'][1]/a/@href")
        item.add_value("explain_xkcd_url", response.url)
        item.add_xpath("img_url", "//div[@id='mw-content-text']//img/@src")
        item.add_xpath("img_title_text",
                       "//div[@id='mw-content-text']//img/@alt")
        item.add_xpath("explanation_html", explanation_xpath)
        item.add_value("explanation_text",
                       self.get_text(response, explanation_xpath))
        item.add_xpath("transcript_html", transcript_xpath)
        item.add_value("transcript_text",
                       self.get_text(response, transcript_xpath))
        item.add_xpath("trivia_html", trivia_xpath)
        item.add_value("trivia_text", self.get_text(response, trivia_xpath))
        item.add_value(
            "incomplete",
            len(
                response.xpath(
                    "//table[contains(@class, 'notice_tpl')]").getall()) > 0)
        item.add_value("last_updated", datetime.now())
        yield item.load_item()

        for next in response.xpath("//span[starts-with(., 'Next')]/parent::a"):
            yield response.follow(next, self.parse)

    def get_text(self, response, xpath):
        return BeautifulSoup(" ".join(response.xpath(xpath).extract()),
                             features="lxml").get_text()
