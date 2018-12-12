import sklearn
import jieba
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

class Config:
    netease_news = ['./data/news/ch_net_news_1.txt', './data/news/ch_net_news_2.txt']
    netease_reviews = ['./data/news/ch_net_reviews_1.txt', './data/news/ch_net_reviews_2.txt']
    netease_labels = ['./data/news/net_label_1']

    toutiao_news = ['./data/news/ch_toutiao_news_1.txt', './data/news/ch_toutiao_news_2.txt']
    toutiao_reviews = ['./data/news/ch_toutiao_reviews_1.txt', './data/news/ch_toutiao_reviews_2.txt',]
    toutiao_label = ['./data/news/toutiao_label_1', './data/news/toutiao_label_2']


class FeatureExtractor:
    def __init__(self, news, reviews, stop_words=None):
        self.news_files = news
        self.review_files = reviews
        self.news = {}
        self.reviews = {}

        self.__read_file()

        self.news_num = len(self.news)
        self.review_num = len(self.reviews)

        self.cnVct_news = CountVectorizer()
        self.cnVct_review = CountVectorizer()

        self.TfIdfVct = TfidfTransformer()
        self.lda = LatentDirichletAllocation()

    @staticmethod
    def pre_process(text):
        words = list(jieba.cut(text))
        return words

    def __read_file(self):

        news_dup_num = 0
        review_sourceless = 0

        for file in self.news_files:
            print('read news from %s' % file)
            with open(file, 'r', encoding='utf8') as fp:
                for line in fp.readlines():
                    columns = line.split('\t')
                    news_id = columns[0]

                    if len(columns) != 8:
                        continue
                    if news_id in self.news:
                        news_dup_num += 1
                        continue
                    # if news_id in self.news:
                    #     print(line)
                    #     print(self.news[news_id])
                    #     exit(1)
                    # assert news_id not in self.news
                    if file.startswith('net'):
                        self.news[news_id] = {'source': columns[1],
                                              'publish_time': columns[2],
                                              'type': columns[3],
                                              'headline': self.pre_process(columns[4]),
                                              'content': self.pre_process(columns[5]),
                                              'favor': int(columns[6]),
                                              'oppose': int(columns[7]),
                                              'reviews': []}
                    else:
                        self.news[news_id] = {'author_id': columns[1],
                                              'author_media': columns[2],
                                              'publish_time': columns[3],
                                              'headline': self.pre_process(columns[4]),
                                              'content': self.pre_process(columns[5]),
                                              'favor': int(columns[6]),
                                              'oppose': int(columns[7]),
                                              'reviews': []}
        print('%d news in total, %d news repeat' % (len(self.news), news_dup_num))

        for file in self.review_files:
            review_id = 0
            print('read reviews from %s' % file)
            with open(file, 'r', encoding='utf8') as fp:
                for line in fp.readlines():
                    columns = line.split('\t')
                    news_id = columns[0]
                    if news_id not in self.news:
                        review_sourceless += 1
                        continue
                    if len(columns) != 6:
                        continue
                    if file.startswith('net'):
                        self.reviews[review_id] = {'reviewer_id': int(columns[1]),
                                                   'oppose': int(columns[2]),
                                                   'favor': int(columns[3]),
                                                   'floor': int(columns[4]),
                                                   'content': self.pre_process(columns[5])}
                        self.news[news_id]['reviews'].append(review_id)
                        review_id += 1
                    else:
                        self.reviews[review_id] = {}
                        self.reviews[review_id] = {'favor': int(columns[1]),
                                                   'oppose': int(columns[2]),
                                                   'is_following': int(columns[3]),
                                                   'is_followed': int(columns[4]),
                                                   'content': self.pre_process(columns[5])}
                        self.news[news_id]['reviews'].append(review_id)
                        review_id += 1
        print('%d reviews in total, %d no source' % (len(self.reviews), review_sourceless))

        for news_id in self.news:
            self.news[news_id]['merge_review'] = self.merge_text(self.news[news_id]['reviews'])

        num_details = [0]*500
        for news_id in self.news:
            num_details[len(self.news[news_id]['reviews'])] += 1

        print('*'*10)
        print(num_details)

    def news_text(self):
        items = [(self.news[news_id], self.news['headline'], self.news['content']) for news_id in self.news]
        news_id = [item[0] for item in items]
        headlines = [item[1] for item in items]
        content = [item[2] for item in items]

        return news_id, headlines, content

    def reviews_text(self):
        reviews = [(review_id, self.reviews[review_id]) for review_id in range(self.review_num)]
        return reviews

    def build_vocab(self):
        news_di, headline, news = self.news_text()
        reviews = self.reviews_text()

    @staticmethod
    def merge_text(text_list):
        res = []
        for text in text_list:
            res.extend(text)
        return res

    def set_news_feature(self):
        news_id, headline, news = self.news_text()
        text_matrix = self.cnVct_news.fit_transform(headline+news).toarray()

        for i in range(self.news_num):
            nid = news_id[i]
            # bow
            self.news[nid]['headline_vec'] = text_matrix[i]
            self.news[nid]['content_vec'] = text_matrix[i+self.news_num]

            # news length
            self.news[nid]['length'] = len(self.news[nid]['content'])

            # favor/oppose
            self.news[nid]['favor_rate'] = self.news[nid]['favor'] / self.news[nid]['favor']+self.news[nid]['oppose']

            # 标题和文章相关度
            pass

    def set_reviews_feature(self):
        # reviews num
        for news in self.news:
            news['review_num'] = len(news['reviews'])

        # total length


# test
featureExtractor = FeatureExtractor(news=Config.netease_news+Config.toutiao_news,
                                    reviews=Config.netease_reviews+Config.toutiao_reviews)

featureExtractor.set_news_feature()
featureExtractor.set_reviews_feature()

