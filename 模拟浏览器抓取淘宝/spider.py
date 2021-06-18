import json
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from pyquery import PyQuery as pq
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
# wait = WebDriverWait(browser, 10)
# browser.set_window_size(1400, 900)
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
# browser = webdriver.Chrome(options=chrome_options)
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


def login():
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
    browser.get('https://www.taobao.com/')
    input = wait.until(
        Ec.presence_of_element_located((By.CSS_SELECTOR, '#q'))
    )
    submit = wait.until(
        Ec.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
    )
    input.send_keys('美食')
    submit.click()
    time.sleep(15)
    Cookies = browser.get_cookies()
    jsonCookies = json.dumps(Cookies)
    with open("taobao_cookies.json", 'w') as f:
        f.write(jsonCookies)


def cookie():
    # browser.delete_all_cookies()  # 删除本次打开网站生成的cookies
    with open("taobao_cookies.json", 'r', encoding='utf-8') as f:
        cookies = json.loads(f.read())
    for cookie in cookies:
        browser.add_cookie({'domain': '.taobao.com',  # 添加cookie
                           'name': cookie['name'],
                           'value': cookie['value'],
                           'path': '/',
                           'expires': None})


def serch():
    print('正在搜索')
    try:
        browser.get('https://www.taobao.com/')
        cookie()
        input = wait.until(
            Ec.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        submit = wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )
        input.send_keys('美食')
        submit.click()
        total = wait.until(Ec.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except TimeoutException:
        return serch()


def next_page(page_number):
    print('正在翻页', page_number)
    time.sleep(5)
    try:
        input = wait.until(
            Ec.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )
        submit = wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            Ec.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > '
                                                               'span'), str(page_number))
        )
        get_products()
    except TimeoutException:
        return next_page(page_number)


def get_products():
    wait.until(
        Ec.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item'))
    )
    html =browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        save_to_mongo(product)


def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert_one(result):
            print('存储成功', result)
    except Exception:
        print('存储失败', result)


def main():
    # login()
    serch()
    # total = int(str(total).split()[1])
    for i in range(2, 15):
        next_page(i)
    browser.close()


if __name__ == '__main__':
    main()