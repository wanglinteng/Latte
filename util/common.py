import json
import os
import time

from util.config import conf, OUTPUT_DIR
from util.redis_cli import redis_cli


def url_encoder(p_id=None, question_id=None, answer_id=None, zvideo_id=None):
    """ 构造url """
    if p_id:
        return "https://zhuanlan.zhihu.com/p/{}".format(p_id)

    if question_id and answer_id:
        return "https://www.zhihu.com/question/{}/answer/{}".format(question_id, answer_id)

    if zvideo_id:
        return "https://www.zhihu.com/zvideo/{}".format(zvideo_id)

    return ''


def url_decoder(url):
    """ url 类型解析"""
    if 'zhuanlan' in url:  # zhuanlan -> article
        return 'article'
    if 'answer' in url:
        return 'answer'
    if 'zvideo' in url:
        return 'zvideo'
    return 'other'


def print_json(d):
    """ json 格式化打印"""
    json_dicts = json.dumps(d, indent=4, ensure_ascii=False)
    print(json_dicts)


def process_kill_all(p_list):
    """ 杀掉所有进程 """
    for p in p_list:
        if p.is_alive():
            p.kill()


def process_start_all(p_list):
    """ 启动所有进程 """
    for p in p_list:
        if not p.is_alive():
            p.start()


def process_check(p_list):
    """ 进程状态检测"""
    for p in p_list:
        if not p.is_alive():
            return False
    return True


def redis_monitor(p_list):
    """ 状态监控，显示抓取到数量 """
    while process_check(p_list):
        print(
            '{}:{}\t'
            'KEYWORDS_TMP:{}\t'
            'TOPIC_DAG:{}\tTOPIC_MESSAGE:{}\tTOPIC_MESSAGE_TMP:{}\t'
            'URLS:{}\tURLS_TMP:{}'.format(
                conf.proxy_redis_name,
                redis_cli.hlen(conf.proxy_redis_name),
                redis_cli.scard('KEYWORDS_TMP'),
                redis_cli.hlen('TOPIC_DAG'),
                redis_cli.hlen('TOPIC_MESSAGE'),
                redis_cli.scard('TOPIC_MESSAGE_TMP'),
                redis_cli.scard('URLS'),
                redis_cli.scard('URLS_TMP')))
        time.sleep(3)
    process_kill_all(p_list)


def get_cur_output_dir():
    """ 当前写入文件夹 """
    return os.path.join(OUTPUT_DIR, time.strftime("%Y%m%d", time.localtime()))
