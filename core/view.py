import time

import requests

from core.filter import multi_html_001
from util.captcha import captcha_check
from util.common import url_encoder, print_json, is_un_human
from util.header import normal_header
from util.loghandler import LogHandler
from util.proxy import ProxiesReceiver


class View(object):
    """ 直接访问页面爬取数据 """

    def __init__(self, use_proxy=False):
        self.proxy = ProxiesReceiver() if use_proxy else None
        self.logger = LogHandler('view')

    def view_html(self, url, timeout=3):
        """ 直访网页 """
        html = ''
        try:
            session = requests.session()
            proxies = self.proxy.one_random if self.proxy else None
            ques = session.get(url=url, headers=normal_header(), proxies=proxies, timeout=timeout)
            html = ques.text
            if is_un_human(html):  # 触发知乎验证码
                r = captcha_check()
                self.logger.error('captcha_check {}'.format(r))
                time.sleep(10)
            return html
        except Exception as e:
            self.logger.info(html)
            self.logger.error(e)
            return html


if __name__ == '__main__':
    View = View()
    url = url_encoder(p_id='399612222')
    # url = url_encoder(question_id='309872833', answer_id='2059603386')
    # url = url_encoder(zvideo_id='1319352102603276288')
    html = View.view_html(url=url)
    data = multi_html_001(url=url, html=html)
    print_json(data)
