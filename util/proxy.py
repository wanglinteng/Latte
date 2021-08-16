import datetime
import logging
import random
import time

import redis
from apscheduler.schedulers.background import BackgroundScheduler

from util.config import conf


class ProxiesReceiver(redis.Redis):
    def __init__(self, host=conf.proxy_redis_host, port=conf.proxy_redis_port, db=conf.proxy_redis_db):
        super().__init__(connection_pool=redis.ConnectionPool(host=host, port=port, db=db))
        self.proxy_cursor = 0
        self.proxy_list = []
        self.proxies_scheduler_start()

    def proxies_scheduler_start(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self._proxies_refresh, "interval", seconds=3, next_run_time=datetime.datetime.now())
        scheduler.start()
        time.sleep(1)  # wait _proxies_refresh exec

    def _proxies_refresh(self):
        """ extract ip from redis """
        self.proxy_cursor, ips = self.hscan(name=conf.proxy_redis_name, cursor=self.proxy_cursor, count=1000)
        if ips:
            self.proxy_list.clear()
            for ip in dict(ips).keys():
                self.proxy_list.append({'http': ip})

    def wait_proxies(self):
        """ 等待获取足够的代理ip """
        for i in range(300):
            proxy_num = self.hlen('use_proxy')
            if proxy_num > 4:
                return True
            print('\r wait for enough proxies(%d)... %ds' % (proxy_num, i), end='')
            time.sleep(1)
        logging.error("Not have enough proxies!Please check proxy module and run process again.")
        return False

    @property
    def all_proxies(self):
        return self.proxy_list

    @property
    def one_random(self):
        return random.choice(self.proxy_list)
