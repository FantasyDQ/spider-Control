# -*- coding:gbk -*-
from bs4 import BeautifulSoup
#import html5lib
from urllib.parse import urlparse
import re
import requests
import csv
from fake_useragent import UserAgent
ua=UserAgent()
from selenium import webdriver
import os
import time
from fake_useragent import UserAgent
ua=UserAgent()
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
try:
    from settings import SELENIUM_URL
except:
    SELENIUM_URL = "http://10.1.203.15:54444/wd/hub"
js_to_List=[]
def getNumofCommonSubstr(str1, str2):
    lstr1 = len(str1)
    lstr2 = len(str2)
    record = [[0 for i in range(lstr2 + 1)] for j in range(lstr1 + 1)]  # 多一位
    maxNum = 0  # 最长匹配长度
    p = 0  # 匹配的起始位
    for i in range(lstr1):
        for j in range(lstr2):
            if str1[i] == str2[j]:
                # 相同则累加
                record[i + 1][j + 1] = record[i][j] + 1
                if record[i + 1][j + 1] > maxNum:
                    # 获取最大匹配长度
                    maxNum = record[i + 1][j + 1]
                    # 记录最大匹配长度的终止位置
                    p = i + 1
                    # print(record)
    return maxNum
class Check_Gen_Url(object):
    topRootDomain = (
        '.com', '.la', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi',
        '.us', '.biz', '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn',
        '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
        '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br',
        '.bz', '.com.bz', '.net.bz', '.cc', '.com.co', '.net.co',
        '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
        '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
        '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms',
        '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
        '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
        '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', ".com.hk")
    @classmethod
    def get_domain_root(cls, url):
        domain_root = ""
        try:
            ## 若不是 http或https开头，则补上方便正则匹配规则
            if url[0:4] != "http" and url[0:5] != "https":
                url = "http://" + url
            reg = r'[^\.]+(' + '|'.join([h.replace('.', r'\.') for h in Check_Gen_Url.topRootDomain]) + ')$'
            pattern = re.compile(reg, re.IGNORECASE)
            parts = urlparse(url)
            host = parts.netloc
            m = pattern.search(host)
            res = m.group() if m else host
            domain_root = "-" if not res else res
        except Exception as ex:
            domain_root=" "
        return domain_root
def request_spider(url, timeout):
    headers = {'User-Agent': "{}".format(ua.random)}
    try:
        res = requests.get(url=url, headers=headers, allow_redirects=False, timeout=timeout)
    except Exception as e:
        return False,e
    try:
        try:
            html = res.content.decode('gbk')
        except:
            html = res.content.decode('utf-8')
    except:
        html = res.text
    return res,html
def get_word(html):
    Chinese_list=[]
    Chinese_list_plus=[]
    soup = BeautifulSoup(html, 'lxml')
    [s.extract() for s in soup([ 'style', 'script','[document]', 'head', 'title'])]
    visible_text = soup.getText()
    # visible_text_01=visible_text.replace('\n', '').replace('\r', '').replace(' ','').replace('\t','')
    visible_text_001 = visible_text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    visible_text_01 = ' '.join(visible_text_001.split())
    #visible_text_01 = visible_text_0001.lower()
    words = re.findall("{(.+?)}", visible_text_01)
    for word in words:
        pre = re.compile(u'[\u4e00-\u9fa5-\，\。]')
        res = re.findall(pre, word)
        res1 = ''.join(res)
        Chinese_list.append(res1)
    for i in Chinese_list:
        if len(i) != 0:
            Chinese_list_plus.append(i)
    China = ''.join(Chinese_list_plus)  # 语法：str.join(sequence)
    abc = re.sub(r"{(.*)}", '', visible_text_01)
    Ultimate_text = abc + China
    Chinese_list.clear()
    Chinese_list_plus.clear()
    return Ultimate_text
def selenium_or_not(url, html):
    yenei_list = []
    url_from_html = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html)
    if url_from_html:
        for meta_url_son in url_from_html:
            gen_meta_url_son = Check_Gen_Url.get_domain_root(meta_url_son)
            maxNum_meta_url = getNumofCommonSubstr(gen_meta_url_son, url)
            if maxNum_meta_url >= 7:
                yenei_list.append(meta_url_son)
    if 'http-equiv="refresh"' in html and len(yenei_list)==0 or 'HTTP-EQUIV="REFRESH"' in html and len(yenei_list)==0:
        return True
    else:
        yenei_list.clear()
        soup = BeautifulSoup(html, "lxml")
        Soup_script = soup.find_all('script')
        script_1 = str(Soup_script)
        if 'e.initEvent("click",true,true)' in script_1 :
            return True
        elif '.submit()</script>' in script_1:
            return True
        elif len(html) !=0 and len(script_1)/ len(html) >0.8:
            return True
        elif 'document.location.protocol' in script_1 :
            return False
        elif  'location.host' in script_1:
           return False
        elif 'window.location' in script_1 or 'location.href' in script_1 or 'document.location' in script_1:
            url_from_script_1 = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', script_1)
            if url_from_script_1:
                for son_url_from_script_1 in url_from_script_1:
                    genUrl_from_script_1 = Check_Gen_Url.get_domain_root(son_url_from_script_1)
                    gen_url = Check_Gen_Url.get_domain_root(url)
                    maxnum = getNumofCommonSubstr(genUrl_from_script_1, gen_url)
                    if maxnum >= 7:
                        yenei_list.append(son_url_from_script_1)
                if len(yenei_list) != 0:
                    yenei_list.clear()
                    return False
                else:
                    return True
            else:
                return True
        else:
            return False
def get_content(url, html):
    html_text = get_word(html)
    soup = BeautifulSoup(html, 'lxml')
    soup.prettify()
    try:
        try:
            title = soup.title.string
        except:
            title = soup.title.text
    except:
        title= soup.text.title()
    print(title)
    return [True, url, html_text, title, html,"requestSpider"]
def chrome_spider_son(url, SpiderTimeOut, SeleniumTimeOut):
    try:
        res,html=request_spider(url, SpiderTimeOut)
        print(res)
    except Exception as e:
        return [False,url,e,'','','']
    if res !=False:
        if res.status_code == 200:
            if selenium_or_not(url, html)==True:
                return chrome_spyder_01(url, SeleniumTimeOut,for_soup=True),"跳转"
            else:
                return get_content(url, html)
        elif 'location' in res.headers.keys():
            i=0
            new_url_01 = res.headers['location']
            while i<5 :
                if 'http' not in new_url_01:
                    new_url = url + new_url_01
                else:
                    new_url = new_url_01
                res_redirect,html__redirect=request_spider(new_url, SpiderTimeOut)
                if res_redirect==False:
                    break
                if res_redirect.status_code == 200:
                    break
                else:
                    i += 1
                    if res_redirect:
                        if res_redirect.headers['location']:
                            new_url_01=res_redirect.headers['location']
                        else:
                            break
                    else:
                        break
            if res_redirect != False:
                if res_redirect.status_code == 200:
                    if selenium_or_not(new_url, html__redirect) == False:
                        return get_content(new_url, html__redirect)
                    else:
                        return chrome_spyder_01(url, SeleniumTimeOut, for_soup=True)
                else:
                    return [False, url, '', '','','']
            else:
                return [False, url,'' , '','','']
        else:
            return [False, url, '', '','','']
    else:
        return [False, url, html, '','','']
def get_data(text):
    soup = BeautifulSoup(text.strip(),  "lxml")
    # print(soup.prettify())
    for tag in soup.find_all():
        # 删除具有无效内容的标签
        if tag.name in ["script", "style"]:
            tag.decompose()
    clean_data = re.sub(r"[^\u4e00-\u9fa50-9a-zA-z\s]+", "", soup.get_text().strip())
    html_data = re.sub(r"[\s]+", r" ", clean_data.lower())
    return html_data
def _init():
    chrome_options = webdriver.ChromeOptions()
    # 屏蔽Chrome的--ignore-certificate-errors提示及禁用扩展插件并实现窗口最大化
    # chrome_options.add_argument('--ignore-certificate-errors')
    # 禁用GPU加速
    chrome_options.add_argument('--ignore-ssl-errors=true')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ssl-protocol=TLSv1')
    chrome_options.add_argument("--window-size=1200x900")
    # 不遵守同源策略
    chrome_options.add_argument("disable-web-security")
    # 浏览器不提供可视化页面
    chrome_options.add_argument('headless')
    # 取消沙盒模式
    chrome_options.add_argument('no-sandbox')
    chrome_options.add_argument('disable-dev-shm-usage')
    # 设置浏览器分辨率（窗口大小）
    # chrome_options.add_argument('window-size=1920x3000')
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Remote(SELENIUM_URL, options=chrome_options,
                              desired_capabilities=DesiredCapabilities.CHROME)
    return browser
def chrome_spyder_01(url, timeout, for_soup=False):
    browser = _init()
    browser.set_page_load_timeout(timeout)
    try:
        browser.get(url)
        time.sleep(2)
    except Exception as e:
        browser.execute_script('window.stop()')
    try:
        tag_frame = browser.find_elements_by_xpath('//frame')
    except Exception as e:
        tag_frame = []
    if len(tag_frame) == 1:
        browser.switch_to.frame(tag_frame[0])
    try:
        tag_a = browser.find_elements_by_xpath('//a')
    except Exception as e:
        tag_a = []
    if len(tag_a) == 1:
        browser.execute_script("arguments[0].click();", tag_a[0])
        time.sleep(2)
    if len(browser.window_handles) == 2:
        browser.switch_to.window(browser.window_handles[1])
    cur_url = browser.current_url
    cur_url = re.sub('/$', '', cur_url)
    print(cur_url)
    try:
        page_text=browser.page_source
        soup = BeautifulSoup(page_text, "lxml")
        soup.prettify()
        try:
            try:
                title_content = soup.title.string
            except:
                title_content = soup.title.text
        except:
            title_content = soup.text.title()
    except Exception as e:
        browser.execute_script('window.stop()')
        browser.quit()
        return [False,url,e,'','','']
    browser.quit()
    if for_soup:
        html_content = get_data(page_text)
        return [True, cur_url, html_content, title_content, page_text,url+"'selenium_spider'"]
def makeUniqId():
    return str(int(time.time() * 1000000)) + ''.join(str(random.randint(0, 9)) for i in range(9))

def chrome_spyder(url):
    f = open('test02.csv', 'a+', encoding='utf-8')
    writer = csv.writer(f)
    if "http"  in url or "https"  in url:
        writer.writerow(chrome_spider_son(url,10,30))
    else:
        url = "http://" + url
        writer.writerow(chrome_spider_son(url,10,30))

