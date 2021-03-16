import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from steylerbank.items import Article


class SteylerbankSpider(scrapy.Spider):
    name = 'steylerbank'
    start_urls = ['https://www.steyler-bank.de/ueber-uns/presseservice-news/c1968.html']

    def parse(self, response):
        articles = response.xpath('//div[@class="eb_content-width"]//div[@class="eb_list_item"]')
        for article in articles:
            link = article.xpath('.//a[1]/@href').get()
            date = article.xpath('.//span[@class="eb_bold"]/text()').get()
            if date:
                date = date.strip()
            else:
                return

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@title="weiter"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="eb_mod_news_detail"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
