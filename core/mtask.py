from util.common import process_start_all, process_kill_all, redis_monitor
from util.proxy import ProxiesReceiver
from multiprocessing import Process


class Mtask(object):
    """ 多任务爬取 """

    def __init__(self, use_proxy=True):
        self.task_list = list()
        self.ProxiesReceiver = ProxiesReceiver()
        if use_proxy:
            self.check_proxy()

    def check_proxy(self):
        """ 检查代理 """
        if not self.ProxiesReceiver.wait_proxies():
            process_kill_all(self.task_list)
            return False
        return True

    def run(self, tasks):
        """ 多进程任务 """
        for t in tasks:
            self.task_list.append(Process(target=t, name=t.__name__))
            print('{} starting...'.format(t.__name__))
        process_start_all(self.task_list)
        redis_monitor(self.task_list)

    def kill(self):
        process_kill_all(self.task_list)
