from scrapy.selector import HtmlXPathSelector
from cto.items import CtoItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request

class PageSpider(CrawlSpider):
    name = "cto"
    allowed_domains = ["raleigh.craigslist.org"]
    start_urls = ["http://raleigh.craigslist.org/cto/"]

    rules = ( Rule( SgmlLinkExtractor(allow='http://raleigh.craigslist.org/cto/'),
                    callback='parse_page', follow=True ),
              )
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        rows = hxs.select('//div[@class="content"]/p[@class="row"]')

        for row in rows:
            item = CtoItem()
            link = row.xpath('.//span[@class="pl"]/a')
            item['title'] = link.xpath("text()").extract()
            item['link'] = link.xpath("@href").extract()
            item['price'] = row.xpath('.//span[@class="l2"]/span[@class="price"]/text()').extract()

            url = 'http://raleigh.craigslist.org{}'.format(''.join(item['link']))
            yield Request(url=url, meta={'item': item}, callback=self.parse_item_page)


    def parse_item_page(self, response):
        hxs = HtmlXPathSelector(response)

        item = response.meta['item']
        item['description'] = hxs.select('//section[@id="postingbody"]/text()').extract()
        return item
