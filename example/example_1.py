import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from core.filter import multi_html_001
from core.mtask import Mtask
from core.search import Search, search_001
from core.view import View
from util.common import url_decoder
from util.config import OUTPUT_DIR
from util.loghandler import LogHandler
from util.redis_cli import redis_cli


class Example1(object):
    """
        TASK_1 候选词写入redis待搜索

        TASK_2 候选词搜索 -> topic(redis)
                        -> relevant_query(文件)
                        -> article/zvideo/answer url待爬取(redis)

        TASK_3 url爬取结果写入文件
    """

    def __init__(self, use_proxy=True):
        self.search = Search(use_proxy=use_proxy)
        self.view = View(use_proxy=use_proxy)
        self.logger = LogHandler('example_1')

    def write_keywords(self, file_path):
        """ 候选词写入"""
        with open(file_path, 'r') as f:
            for line in f.readlines():
                try:
                    line = line.strip('\n')
                    redis_cli.save_candidate_keywords(line)  # keywords存储、新增keywords放入暂存区
                except Exception as e:
                    self.logger.error(e)

    def search_keywords(self):
        """ 候选词搜索 """
        while True:
            keywords = redis_cli.pop_keywords()
            res = self.search.multi(t='general', min_record=50, keywords=keywords)
            analyse = search_001(res)

            # topic 话题写入 TOPIC_MESSAGE、如新增需再次写入 TOPIC_MESSAGE_TMP供后续任务使用
            topic = analyse.get('topic', [])
            for t in topic:
                redis_cli.save_topic_message(t)

            # relevant_query 搜索推荐 写入文件
            relevant_query = analyse.get('relevant_query', [])
            if relevant_query:
                with open(os.path.join(OUTPUT_DIR, 'relevant_query'), 'a+') as f:
                    f.write(json.dumps({keywords: relevant_query}, ensure_ascii=False) + '\n')

            # article, zvideo, answer 新增 url 写入 URLS_TMP 供后续任务使用
            urls = analyse.get('article', []) + analyse.get('answer', []) + analyse.get('zvideo', [])
            redis_cli.save_candidate_urls(urls)

    def view_urls(self):
        """ 候选URL搜索"""
        while True:
            url = redis_cli.pop_url()
            html = self.view.view_html(url=url)
            data = multi_html_001(url=url, html=html)
            if data:
                with open(os.path.join(OUTPUT_DIR, url_decoder(url)), 'a+') as f:
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
                    redis_cli.save_url(url=url)


if __name__ == '__main__':
    Example1 = Example1()
    Mtask = Mtask()
    Example1.write_keywords(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'example_1_candidate'))  # 候选词写入
    t = [Example1.search_keywords, Example1.view_urls]  # 候选词搜索 候选url访问
    Mtask.run(t)
