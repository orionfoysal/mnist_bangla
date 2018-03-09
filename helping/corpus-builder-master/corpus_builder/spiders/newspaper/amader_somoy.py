# -*- coding: utf-8 -*-

from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from corpus_builder.templates.spider import CommonSpider


class AmaderSomoySpider(CommonSpider):
    name = 'amader_somoy'
    allowed_domains = ['dainikamadershomoy.com']
    base_url = 'http://www.dainikamadershomoy.com'
    start_request_url = base_url

    content_body = {
        'css': '.dtl_section p::text'
    }

    rules = (
        Rule(LinkExtractor(
            allow='(?<=com)\/\w.*\/\d.*\/.*'
        ),
            callback='parse_content'),
    )

    allowed_configurations = [
        ['start_page'],
        ['start_page', 'end_page'],
        ['category', 'start_page'],
        ['category', 'start_page', 'end_page'],
    ]

    def request_index(self, response):
        categories = list(set(response.css('#menu_category a::attr("href")').extract()))
        categories = [urlparse(x).path.split('/')[-1] for x in categories]

        if self.category:
            if self.category in categories:
                categories = [self.categories]
            else:
                raise ValueError('invalid category slug. available slugs: %s' % ", ".join(categories))

        for category in categories:
            for page in range(int(self.start_page), int(self.end_page) + 1):
                yield scrapy.Request(self.base_url + '/all-news/' + category + '/?pg={0}'.format(str(page)),
                                     callback=self.start_news_requests)

    def start_news_requests(self, response):
        news_links = list(set(response.css('.all_news_content_block a::attr("href")').extract()))

        for link in news_links:
            yield self.make_requests_from_url(link)
