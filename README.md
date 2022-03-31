# MoiveSpider
爬取喜欢的豆瓣电影，分析其影评

**创建scrapy项目**

```
import scrapy startproject review moviereview
```

**使用scrapy-redis配置**

```
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'

ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300, #打开redis存储

}

REDIS_HOST = '192.168.1.80'
REDIS_PORT = 6379
```

**构建Item**

```
import scrapy

class MovieviewItem(scrapy.Item):
    review = scrapy.Field()
```

**构建爬虫**

```
scrapy genspider -t crawl  moviereview douban.com
```

```
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from ..items import MovieviewItem

class ReviewSpider(RedisCrawlSpider):
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
```

**爬取**

```
scrapy crawl review
```

**影评分析**

```
import jieba
import json
from redis import ConnectionPool,Redis
from wordcloud import WordCloud
import matplotlib.pyplot as plt

#获取影评
pool = ConnectionPool.from_url('redis://192.168.1.80:6379/0')
client = Redis(connection_pool=pool)
reviews = client.lrange('review:items',0,-1)
print('records',len(reviews))

#加载停用词
stopwords = set()
with open('ChineseStopWords_utf8.txt',encoding='utf-8') as f:
    for line in f:
        stopwords.add(line.rstrip('\r\n'))
    stopwords.add(' ')
    stopwords.add('，')
    stopwords.add('的')

print('ting', len(stopwords))

#中文分词
wordcount = {}
total = 0
for review in reviews:
    data = json.loads(review)["review"]
    for word in jieba.cut(data):
        if word not in stopwords:
            wordcount[word] = wordcount.get(word, 0) + 1
            total += 1

print('word', len(wordcount), 'total', total)
print(sorted(wordcount.items(), key=lambda x:x[1], reverse=True))


#使用词云绘图
wordcloud = WordCloud(font_path='simhei.ttf', max_font_size=80, scale=15)
wordcloud.fit_words(wordcount)#使用词频创建词云
plt.figure(1) #编号
plt.imshow(wordcloud) #将一个图显示在二维坐标轴上
plt.axis('off') #不打印坐标系
plt.show()
```

**效果图**

![Alt](1.png)