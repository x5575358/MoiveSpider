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

