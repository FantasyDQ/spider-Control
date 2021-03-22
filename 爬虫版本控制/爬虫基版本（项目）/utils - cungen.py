import re
import time
import requests
import certifi

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from func_timeout import func_set_timeout
from func_timeout import func_timeout, FunctionTimedOut

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from settings import (
    executable_path,
    spider_timeout,
    selenium_js_timeout,
    selenium_payload_timeout,
)

from fake_useragent import UserAgent

ua = UserAgent(verify_ssl=False)
headers = {"User-Agent": ua.random}


def getNumofCommonSubstr(str1, str2):
    """Args:
        Two strings
    Returns:
        Returns the maximum consecutive same substring length of two strings
    """
    lstr1 = len(str1)
    lstr2 = len(str2)
    record = [[0 for i in range(lstr2 + 1)] for j in range(lstr1 + 1)]
    maxNum = 0
    p = 0
    for i in range(lstr1):
        for j in range(lstr2):
            if str1[i] == str2[j]:
                record[i + 1][j + 1] = record[i][j] + 1
                if record[i + 1][j + 1] > maxNum:
                    maxNum = record[i + 1][j + 1]
                    p = i + 1
    return maxNum


class Check_Gen_Url(object):
    topRootDomain = (
        ".com",
        ".la",
        ".io",
        ".co",
        ".info",
        ".net",
        ".org",
        ".me",
        ".mobi",
        ".us",
        ".biz",
        ".xxx",
        ".ca",
        ".co.jp",
        ".com.cn",
        ".net.cn",
        ".org.cn",
        ".mx",
        ".tv",
        ".ws",
        ".ag",
        ".com.ag",
        ".net.ag",
        ".org.ag",
        ".am",
        ".asia",
        ".at",
        ".be",
        ".com.br",
        ".net.br",
        ".bz",
        ".com.bz",
        ".net.bz",
        ".cc",
        ".com.co",
        ".net.co",
        ".nom.co",
        ".de",
        ".es",
        ".com.es",
        ".nom.es",
        ".org.es",
        ".eu",
        ".fm",
        ".fr",
        ".gs",
        ".in",
        ".co.in",
        ".firm.in",
        ".gen.in",
        ".ind.in",
        ".net.in",
        ".org.in",
        ".it",
        ".jobs",
        ".jp",
        ".ms",
        ".com.mx",
        ".nl",
        ".nu",
        ".co.nz",
        ".net.nz",
        ".org.nz",
        ".se",
        ".tc",
        ".tk",
        ".tw",
        ".com.tw",
        ".idv.tw",
        ".org.tw",
        ".hk",
        ".co.uk",
        ".me.uk",
        ".org.uk",
        ".vg",
        ".com.hk",
    )

    @classmethod
    def get_domain_root(cls, url):
        """Args:
            Enter a url
        Returns:
            Return its root domain
        """
        try:
            if url[0:4] != "http" and url[0:5] != "https":
                url = "http://" + url
            reg = (
                r"[^\.]+("
                + "|".join([h.replace(".", r"\.") for h in Check_Gen_Url.topRootDomain])
                + ")$"
            )
            pattern = re.compile(reg, re.IGNORECASE)
            parts = urlparse(url)
            host = parts.netloc
            m = pattern.search(host)
            res = m.group() if m else host
            domain_root = "-" if not res else res
        except Exception as ex:
            domain_root = " "
        return domain_root


def request_spider(url, timeout):
    """Args:
        Enter url, wait time

    Returns:
        Response of the return page

    Raises:
        May not be accessible or timeout

    """
    s = requests.session()
    s.keep_alive = False
    try:
        r = s.head(url, allow_redirects=True)
    except requests.exceptions.TooManyRedirects:
        r = s.head(url)
    if r.status_code // 100 == 4 or r.status_code // 100 == 5:
        return None
    else:
        pass

    if "Content-Type" in r.headers or "content-type" in r.headers:
        if ( "text" in r.headers["content-type"]
                or "html" in r.headers["content-type"]
        ) or ("text" in r.headers["Content-Type"]
              or "html" in r.headers["Content-Type"]):
            res = requests.get(
                url=url,
                headers=headers,
                timeout=timeout,
                verify=certifi.where(),
            )
        else:
            return None
    else:
        res = requests.get(
            url=url,
            headers=headers,
            timeout=timeout,
            verify=certifi.where(),
        )
    return res


def get_word(html):
    """Args:
        html crawled by request
    Returns:
        Return the plain text of the page
    """
    Chinese_list = []
    Chinese_list_plus = []
    soup = BeautifulSoup(html, "lxml")
    try:
        title_content = soup.title.string.strip()
    except (AttributeError, KeyError):
        title_content = ""
    [s.extract() for s in soup(["style", "script", "[document]", "head", "title"])]
    visible_text = soup.getText()
    visible_text_001 = (
        visible_text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    )
    visible_text_01 = " ".join(visible_text_001.split())
    words = re.findall("{(.+?)}", visible_text_01)
    for word in words:
        pre = re.compile(u"[\u4e00-\u9fa5-\，\。]")
        res = re.findall(pre, word)
        res1 = "".join(res)
        Chinese_list.append(res1)
    for i in Chinese_list:
        if len(i) != 0:
            Chinese_list_plus.append(i)
    China = "".join(Chinese_list_plus)
    abc = re.sub(r"{(.*)}", "", visible_text_01)
    Ultimate_text = abc + China
    Chinese_list.clear()
    Chinese_list_plus.clear()
    return title_content,Ultimate_text


def selenium_or_not(url, html):
    """Args:
        url and html crawled by request

    Returns:
        According to the returned content, analyze whether selenium crawler needs to be executed
    """
    soup = BeautifulSoup(html, "lxml")
    Soup_script = soup.find_all("script")
    Soup_meta = soup.find_all("meta")
    script_1 = str(Soup_script)
    meta_1 = str(Soup_meta)
    url_from_meta = re.findall(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        meta_1,
    )
    url_from_script_1 = re.findall(
        "http[s]?://(5dc5e92d73b7?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        script_1,
    )
    if url_from_meta:
        page_in = False
        for meta_url_son in url_from_meta:
            gen_meta_url_son = Check_Gen_Url.get_domain_root(meta_url_son)
            maxNum_meta_url = getNumofCommonSubstr(gen_meta_url_son, url)
            if maxNum_meta_url >= 7:
                page_in = True
                break
        if (re.search(r'http-equiv="refresh', meta_1) and not page_in) or (
            re.search(r'HTTP-EQUIV="REFRESH"', meta_1 ) and not page_in
        ):
            return True
    if len(html) == 0:
        return True
    elif (
        re.search(r'e.initEvent("click",true,true)',script_1)
        or re.search(r'.submit()</script>',script_1)
        or re.search(r'window.shareName',script_1)
        or re.search(r'(window).bind',script_1)
        or re.search(r'window.location.search',script_1)
        or (re.search(r'console',script_1) and re.search(r'app',script_1))
        or (len(html) != 0 and len(script_1) / len(html) > 0.8)
        or  (re.search(r'Android', script_1) and re.search(r'Linux', script_1) and re.search(r'iPhone', script_1))
        or  (re.search(r'curProtocol', script_1) and re.search(r'window.location.protocol', script_1))
        or re.search(r'vConsole', script_1)
    ):
        return True

    elif re.search(r'FRAMESET', html) and re.search(r'iframe', html):
        return True
    elif (
            re.search(r'window.location', script_1)
        or re.search(r'location.href', script_1)
        or re.search(r'document.location', script_1)

    ):
        page_in_0 = False
        if url_from_script_1:
            for son_url_from_script_1 in url_from_script_1:
                genUrl_from_script_1 = Check_Gen_Url.get_domain_root(
                    son_url_from_script_1
                )
                gen_url = Check_Gen_Url.get_domain_root(url)
                maxnum = getNumofCommonSubstr(genUrl_from_script_1, gen_url)
                if maxnum >= 7:
                    page_in_0 = True
                    break
            if not page_in_0:
                return True
        else:
            return True
    else:
        return False


def get_content(url, html):
    """Args:
        Enter the html crawled by url and request
    Returns:
        Return info of the crawler result，[True, url, html_text, title, html,"requestSpider"]
    """
    title,html_text_pre = get_word(html)
    html_text = title+html_text_pre
    return [True, url, html_text, title, html, "requestSpider"]


def chrome_spider_son(url, SpiderTimeOut, selenium_jsTimeout, SeleniumTimeOut, service):
    """Args:
        Enter the url, the waiting time of the request crawler, the waiting time of the selenium crawler
    Returns:
        Return the INFO of a crawler, including crawler status, url, page content, page text, page title, crawler type.
    Raises:
        It may not be accessed or timed out. Or the webpage did not jump to a normally accessible page within five times, or jumped to an inaccessible page.
    """

    """ Args:
               Enter the url, the waiting time of the request crawler, the waiting time of the selenium crawler
           Returns:
               Return the INFO of a crawler, including crawler status, url, page content, page text, page title, crawler type.
           Raises:
               It may not be accessed or timed out. Or the webpage did not jump to a normally accessible page within five times, or jumped to an inaccessible page.
           """

    res = request_spider(url, SpiderTimeOut)
    if res:
        html = get_html(res)
        if (
            selenium_or_not(url, html) == True
            or len(get_content(url, html)[2]) <= 5
        ):
            return chrome_spyder_01(
                url, selenium_jsTimeout, SeleniumTimeOut, service
            )
        else:
            return get_content(url, html)
    else:
        return [False, url, "{}---requestFailed".format(url), "", "", ""]


def get_html(res):
    try:
        html = res.content.decode("gbk")
    except UnicodeDecodeError:
        try:
            html = res.content.decode("utf-8")
        except UnicodeDecodeError:
            html = res.text
    return html


def get_data(text):
    """Args:
        Enter the page html obtained by selenium
    Returns:
        Return the plain text of the page
    """
    soup = BeautifulSoup(text.strip(), "lxml")
    try:
        title_content = soup.title.string.strip()
    except (AttributeError, KeyError):
        title_content = ""
    for tag in soup.find_all():
        if tag.name in ["script", "style"]:
            tag.decompose()
    clean_data = re.sub(r"[^\u4e00-\u9fa50-9a-zA-z\s]+", "", soup.get_text().strip())
    html_content_pre = re.sub(r"[\s]+", r" ", clean_data.lower())
    html_content = title_content + html_content_pre
    return title_content,html_content


def _init(service):
    """
    Returns:
            Return a set webdriver
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors=true")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("disable-web-security")
    chrome_options.add_argument("headless")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("no-sandbox")
    chrome_options.add_argument("blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("{}".format(headers))
    chrome_options.add_argument("disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Remote(service.service_url, options=chrome_options)
    return browser


def chrome_spyder_01(url, js_timeout, timeout, service):
    """Args:
        Enter the url, the waiting time of the selenium crawler
    Returns:
        Return the INFO of a crawler, including crawler status, url, page content, page text, page title, crawler type.
    Raises:
        It may time out.
    """
    browser = _init(service)
    browser.set_window_size(800, 1000)
    browser.set_page_load_timeout(timeout)
    browser.set_script_timeout(js_timeout)
    try:
        browser.get(url)
    except TimeoutException as e:
        browser.quit()
        return [False, url, e, "", "", ""]
    try:
        browser.switch_to.alert.accept()
    except Exception as e:
        pass
    if browser.find_elements_by_xpath("//frame"):
        tag_frame = browser.find_elements_by_xpath("//frame")
    else:
        tag_frame = []
    if len(tag_frame) == 1:
        browser.switch_to.frame(tag_frame[0])
    if browser.find_elements_by_xpath("//a"):
        tag_a = browser.find_elements_by_xpath("//a")
    else:
        tag_a = []
    if len(tag_a) == 1:
        browser.execute_script("arguments[0].click();", tag_a[0])
        time.sleep(1)
    if len(browser.window_handles) == 2:
        browser.switch_to.window(browser.window_handles[1])
    cur_url = browser.current_url
    cur_url = re.sub("/$", "", cur_url)
    try:
        page_text = browser.page_source
        title_content,html_content = get_data(page_text)
    except TimeoutException as e:
        browser.quit()
        return [False, url, e, "", "", ""]
    browser.delete_all_cookies()
    browser.close()
    browser.quit()
    return [True, url, html_content, title_content, page_text, cur_url]


class UrlError(Exception):
    pass

@func_set_timeout(17)
def task(url, service):
    return chrome_spider_01(url, service)


def chrome_spider_01(url, service):
    """Args:
        input a url
    Returns:
        Return the INFO of a crawler, including crawler status, url, page content, page text, page title, crawler type.
    """
    url_ori = url.strip()
    if url_ori.startswith("http") or url_ori.startswith("https"):
        url = url_ori
    else:
        url = "http://" + url_ori
    regular = re.match(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        url,
    )
    if regular:
        result = chrome_spider_son(
            url, spider_timeout, selenium_js_timeout, selenium_payload_timeout,service
        )
        result[1] = url_ori
        return result
    else:
        raise UrlError("{},it's  not a url".format(url))


def chrome_spider(url, service):
    try:
        return task(url, service)
    except FunctionTimedOut:
        return [False, url, "spider_funTimeout", "", "", ""]
