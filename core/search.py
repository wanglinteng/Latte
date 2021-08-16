from urllib.parse import quote, urlparse, parse_qs, urlencode

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ReadTimeout, RequestException
from urllib3.util.retry import Retry

from core.filter import search_001
from util.common import print_json
from util.header import gen_header
from util.loghandler import LogHandler
from util.proxy import ProxiesReceiver


class Search(object):
    """
        搜索数据爬取模块，目前支持综合、用户、话题、视频模块。
        综合：general
        用户：people
        话题：topic
        视频：zvideo
    """

    def __init__(self, use_proxy=False):
        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5)))
        self.proxy = ProxiesReceiver() if use_proxy else None
        self.logger = LogHandler('search')

    @staticmethod
    def next_to_url(next):
        """ 第2/3/4..次请求URL解析 """
        nextparse = urlparse(next)
        aram_list = parse_qs(nextparse.query)
        next_query = {
            'correction': aram_list.get('correction')[0],
            'lc_idx': aram_list.get('lc_idx')[0],
            'limit': aram_list.get('limit')[0],
            'offset': aram_list.get('offset')[0],
            'q': aram_list.get('q')[0],
            'search_hash_id': aram_list.get('search_hash_id')[0],
            'show_all_topics': aram_list.get('show_all_topics')[0],
            't': aram_list.get('t')[0],
        }
        next_query = urlencode(next_query)
        url_part = '/api/v4/search_v3?' + next_query
        url = 'https://www.zhihu.com' + url_part
        qtw = quote(aram_list.get('q')[0])
        return qtw, url_part, url

    def multi(self, t, keywords, min_record=30, timeout=3):
        """
            t: general、people、topic、zvideo
            keywords: 搜索关键词
            min_record：最少搜索记录，如不足最小有多少返回多少
            timeout: request 超时时间
        """
        q = quote(keywords)
        general_url_part = '/api/v4/search_v3?t={}&q={}&correction=1&offset=0&limit=20&filter_fields=&lc_idx=0&show_all_topics=1'.format(
            t, q)
        next = ''
        url = ''
        res = []
        first_q = True
        is_end = False
        record = 0
        while is_end is False and record < min_record:
            try:
                # first request
                if first_q:
                    url = 'https://www.zhihu.com' + general_url_part
                    headers = gen_header(url_part=general_url_part, q=q, type=t)
                    proxies = self.proxy.one_random if self.proxy else None
                    results = self.session.get(url=url, headers=headers, proxies=proxies,
                                               timeout=timeout).json()
                    first_q = False

                # not first, must search_hash_id parameter
                else:
                    q, general_url_part, url = self.next_to_url(next=next)
                    headers = gen_header(url_part=general_url_part, q=q, type=t)
                    proxies = self.proxy.one_random if self.proxy else None
                    results = self.session.get(url=url, headers=headers, proxies=proxies,
                                               timeout=timeout).json()

                # next: 下一页URL, is_end: 是否获取结束
                paging = results.get('paging', {})
                is_end = paging.get('is_end', True)
                next = paging.get('next', '')

                # 解析results
                data = results.get('data', None) if results else None
                # self.logger.info('general info {}'.format(data))
                if not data:
                    continue
                record += len(data)
                res.extend(data)

                # exit no data
                if is_end or not next:
                    return res

            except RequestException as re:
                self.logger.warn((re, url))
            except ReadTimeout as rte:
                self.logger.warn((rte, url))
            except KeyError as ke:
                self.logger.warn((ke, url))
            except Exception as e:
                raise e
        return res


if __name__ == '__main__':
    Search = Search()
    r = Search.multi(t='general', min_record=50, keywords="自然语言处理")  # t: general/people/topic/zvideo
    r = search_001(r)  # 搜索结果过滤
    print_json(r)