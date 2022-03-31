from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from ..items import MovieviewItem

class ReviewSpider(RedisCrawlSpider):#可替换CrawlSpider
    name = 'review'
    allowed_domains = ['douban.com']
    #使用CrawlSpider类时属于普通模式，需要放开该参数
    # url = 'https://movie.douban.com/subject/6424756/comments'
    # start_urls = [url]

    redis_key = 'mvew:start_urls'

    rules = (
        Rule(LinkExtractor(allow=r'start=\d+'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        contents = response.xpath('//span[@class="short"]/text()')
        for content in contents:
            item = MovieviewItem()
            item['review'] = content.get()
            yield item

