import os
import time
from configparser import ConfigParser

from util.decorator import LazyProperty
from util.decorator import singleton

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')
LOG_DIR = os.path.join(PROJECT_DIR, 'logs')


try:
    for path in [OUTPUT_DIR, LOG_DIR]:
        if not os.path.exists(path):
            os.makedirs(path)
except Exception as e:
    print('mkdir exception {}'.format(e))


@singleton
class Config(object):
    def __init__(self):
        self.cfg = ConfigParser()
        self.cfg.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'), encoding='utf-8')

    @LazyProperty
    def storage_redis_host(self):
        return self.cfg.get('REDIS', 'storage_redis_host')

    @LazyProperty
    def storage_redis_port(self):
        return self.cfg.get('REDIS', 'storage_redis_port')

    @LazyProperty
    def storage_redis_db(self):
        return self.cfg.get('REDIS', 'storage_redis_db')

    @LazyProperty
    def proxy_redis_host(self):
        return self.cfg.get('REDIS', 'proxy_redis_host')

    @LazyProperty
    def proxy_redis_port(self):
        return self.cfg.get('REDIS', 'proxy_redis_port')

    @LazyProperty
    def proxy_redis_db(self):
        return self.cfg.get('REDIS', 'proxy_redis_db')

    @LazyProperty
    def proxy_redis_name(self):
        return self.cfg.get('REDIS', 'proxy_redis_name')

    @LazyProperty
    def stream_log_level(self):
        return int(self.cfg.get('RUN_LOG', 'stream_log_level'))

    @LazyProperty
    def file_log_level(self):
        return int(self.cfg.get('RUN_LOG', 'file_log_level'))


conf = Config()

if __name__ == '__main__':
    print(conf.storage_redis_host)
