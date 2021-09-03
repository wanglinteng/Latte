import hashlib
import json
import os
import random
from urllib.parse import quote

import execjs
import requests

from util.config import PROJECT_DIR

user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"]
try:
    with open(os.path.join(PROJECT_DIR, 'util', 'user-agent_0.1.11.json'), 'r') as f:
        d = json.load(f)
        user_agents_tmp = d.get('browsers', {}).get('chrome', [])
        if user_agents_tmp:
            user_agents = user_agents_tmp
except Exception as e:
    print('user_agents load exception {}'.format(e))


def gen_header(url_part, q, type, d_c0='"ACDXfhlXcBKPThgCFcQdt5d4_bWmqk79pmQ=|1609556670"'):
    """
        init:
            cd x-zse-96/
            npm install jsdom

        refer document:
            https://blog.csdn.net/qq_26394845/article/details/118183245
    """
    f = "+".join(["101_3_2.0", url_part, d_c0])
    fmd5 = hashlib.new('md5', f.encode()).hexdigest()

    _cur_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(_cur_dir, 'x-zse-96/g_encrypt.js'), 'r') as f:
        ctx1 = execjs.compile(f.read(), cwd=r'{}'.format(os.path.join(_cur_dir, 'x-zse-96')))
    encrypt_str = ctx1.call('b', fmd5)

    header = {
        "referer": "https://www.zhihu.com/search?type={}&q={}".format(type, q),
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        'cookie': 'd_c0={}'.format(d_c0),
        "x-api-version": "3.0.91",
        "x-zse-93": "101_3_2.0",
        "x-zse-96": "2.0_{}".format(encrypt_str)
    }
    return header


def normal_header():
    header = {"user-agent": random.choice(user_agents)}
    return header


if __name__ == '__main__':
    kw = 'www'
    qkw = quote(kw)
    type = 'general'  # general | topic
    url_part = '/api/v4/search_v3?t={}&q={}&correction=1&offset=0&limit=20&filter_fields=&lc_idx=0&show_all_topics=1'.format(
        type, qkw)
    headers = gen_header(url_part=url_part, q=qkw, type=type, d_c0='"ACDXfhlXcBKPThgCFcQdr3f7_bWmqk79pmQ=|1609556670"')
    sessions = requests.session()
    r = sessions.get(url='https://www.zhihu.com{}'.format(url_part), headers=headers, timeout=3).json()
    # print(headers)
    # print(r)

    # r = normal_header()
    # print_json(r)
