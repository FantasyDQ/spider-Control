# -*- coding:utf-8 -*-
from utils import chrome_spyder
from multiprocessing import cpu_count
from threading import Thread
import threading
lock=threading.Lock()
def get_url(urls):
    lock.acquire()
    if len(urls)==0:
        return ""
    else:
        url=urls[0]
        del urls[0]
    lock.release()
    return url
class Spider(Thread):
    def __init__(self, name):
        super(Spider, self).__init__()
        self.name=name
    def run(self):
        while True:
            url=get_url(urls)
            chrome_spyder(url)
if __name__=="__main__":
    with open('360_wangyefenlei.txt', "r", encoding='ISO-8859-1') as f:  
        C = f.read()
        urls= C.split()
    for i in range(0,cpu_count()):
        thread=Spider('thread{}'.format(i))
        thread.start()
        thread.join()