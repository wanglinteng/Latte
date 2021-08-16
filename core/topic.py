from json.decoder import JSONDecodeError

import requests
from requests.exceptions import ReadTimeout, RequestException

from util.common import print_json
from util.header import normal_header
from util.loghandler import LogHandler
from util.proxy import ProxiesReceiver


class Topic(object):
    """
        知乎话题树 https://www.zhihu.com/topic/19776749/organize/entire#anchor-children-topic
    """

    def __init__(self, use_proxy=False):
        self.session = requests.Session()
        self.proxy = ProxiesReceiver() if use_proxy else None
        self.logger = LogHandler('topic')

    def topic_extend(self, topic_id, parent=False, child=False):
        """ 拓展话题、查找某个节点的父子节点 """

        results = []
        first_q = True
        is_end = False
        next = ''
        url = ''

        # select child or parent
        if not child and not parent:
            raise Exception("""must child or parent! """)
        if child:
            url = 'https://www.zhihu.com/api/v3/topics/{}/children'.format(topic_id)  # 子话题api
        if parent:
            url = 'https://www.zhihu.com/api/v3/topics/{}/parent'.format(topic_id)  # 父话题api

        try:
            while is_end is False:
                if first_q:
                    request_url = url
                    first_q = False
                else:
                    request_url = next
                    request_url = 'https' + request_url[4:]
                proxies = self.proxy.one_random if self.proxy else None
                header = normal_header()
                req = self.session.get(url=request_url, headers=header, proxies=proxies, timeout=3)

                if not req:  # 获取父（子）话题有可能不存在
                    return results
                for p in req.json()['data']:
                    results.append(p)

                paging = req.json()['paging']
                is_end = paging.get('is_end', True)
                next = paging.get('next', '')
                if is_end:
                    return results

        except RequestException as re:
            self.logger.warn(re)
        except ReadTimeout as rte:
            self.logger.warn(rte)
        except Exception as e:
            raise e

    def topic_crawler(self, topic_id, num, top_activity=False, essence=False):

        url = ''
        q_json = None
        req = None
        results = []

        # select top_activity_url or essence_url
        if not top_activity and not essence:
            raise Exception("""must top_activity or essence! """)

        for offset in range(0, num, 10):
            if top_activity:
                url = "https://www.zhihu.com/api/v4/topics/{}/feeds/top_activity?before_id=0&limit=10&offset=0&after_id={}".format(
                    topic_id, offset)  # 讨论问题
            if essence:
                url = "https://www.zhihu.com/api/v4/topics/{}/feeds/essence?limit=10&offset={}".format(topic_id,
                                                                                                       offset)  # 精华问题

            try:
                proxies = self.proxy.one_random if self.proxy else None
                headers = normal_header()
                req = self.session.get(url=url, headers=headers, proxies=proxies, timeout=5)
                q_json = req.json() if req else {}
                for p in q_json.get('data', []):
                    results.append(p)

            except Exception as e:
                self.logger.warn((e, url))
            except JSONDecodeError as e:
                self.logger.error((e, url, req))

            if str(q_json.get('paging', {}).get('is_end', 'none')).lower() == 'true':  # 没有更多内容
                return results
        return results


if __name__ == '__main__':
    Topic = Topic()
    # # r = Topic.extend_topic(topic_id='19567592', child=True)
    # r = Topic.topic_extend(topic_id='19567592', parent=True)
    r = Topic.topic_crawler(topic_id='19588260', num=30, essence=True)
    print_json(r)
