import time

import redis
from bs4 import BeautifulSoup

from util.config import conf
from util.decorator import singleton


@singleton
class RedisClient(redis.Redis):
    """
        1. 存储搜索候选词(句子)
        2. 排重、防止重复爬取浪费资源
        3. 存储话题树结构
        4. 存储话题信息
    """

    def __init__(self, host=conf.storage_redis_host, port=conf.storage_redis_port, db=conf.storage_redis_db):
        super().__init__(connection_pool=redis.ConnectionPool(host=host, port=port, db=db))

    def block_pop(self, key):
        """ 模拟阻塞获取集合内元素 """
        while True:
            elem = super().spop(key)
            if elem:
                return elem
            else:
                time.sleep(1)

    def save_candidate_keywords(self, keywords):
        """ 待搜索关键词存入KEYWORDS_TMP中 """
        self.sadd('KEYWORDS_TMP', keywords)

    def count_candidate_keywords(self):
        return self.scard('KEYWORDS_TMP')

    def save_topic_message(self, d):
        """话题信息写入"""
        name = BeautifulSoup(d.get("name"), 'lxml').get_text()
        introduction = BeautifulSoup(d.get("introduction"), 'lxml').get_text()
        best_answers_count = max(d.get("best_answers_count", 0), d.get('top_answer_count', 0))  # 搜索与api此字段不同，兼容
        if self.hset('TOPIC_MESSAGE', d.get('id'),
                     str({"name": name,
                          'introduction': introduction,
                          "questions_count": d.get("questions_count"),  # 问题数
                          "best_answers_count": best_answers_count,
                          'followers_count': d.get("followers_count")})):  # 关注者
            # 记录新增topic，用于后续DAG拓展
            self.sadd('TOPIC_MESSAGE_TMP', d.get('id'))

    def pop_keywords(self):
        """ 取一个关键词 """
        return self.block_pop('KEYWORDS_TMP').decode('utf-8')

    def pop_url(self):
        """ 取一个url """
        return self.block_pop('URLS_TMP').decode('utf-8')

    def save_url(self, url):
        """ 记录url任务完毕 """
        self.sadd('URLS', url)

    def save_candidate_url(self, url):
        """ 保存待爬取url """
        if not self.sismember('URLS', url):  # 防止重复爬取
            self.sadd('URLS_TMP', url)

    def save_candidate_urls(self, urls):
        """ 保存待爬取url, 兼容多条"""
        if isinstance(urls, list):
            for u in urls:
                self.save_candidate_url(u)
        if isinstance(urls, str):
            self.save_candidate_url(urls)


redis_cli = RedisClient()
