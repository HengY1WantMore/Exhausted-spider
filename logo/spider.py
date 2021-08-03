import time
import xlrd
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# browser = webdriver.Chrome('/Users/hengyi/Desktop/chromedriver')
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


# 日志记录
def log(location, text):
    with open(location, "a+", encoding='utf-8') as f:
        f.write(text)


def record(info):
    log('record.txt', info + '\n')


# 获取数据
def get_info_excel(file, col):
    res = []
    wb = xlrd.open_workbook(filename=file)  # 打开文件
    sheet = wb.sheet_by_index(0)  # 通过索引获取表格
    col = sheet.col(col)[1:]  # 获取到目标
    for one in col:
        res.append(one.value)
    return res


# 浏览器请求
def get_info(want):
    browser.get('https://www.google.com.hk/search?q=1')
    input = wait.until(
        Ec.presence_of_element_located((By.CSS_SELECTOR, '#tsf > div:nth-child(1) > div.A8SBwf > div.RNNXgb > div > div.a4bIc > input'))
    )
    submit = wait.until(
        Ec.element_to_be_clickable((By.CSS_SELECTOR, '#tsf > div:nth-child(1) > div.A8SBwf > div.RNNXgb > button'))
    )
    input.clear()
    input.send_keys(want)
    submit.click()
    time.sleep(3)
    p = browser.find_elements_by_css_selector('.g')[:4]
    for x in p:
        content = str(x.text).split('\n')
        record(str(content))
    log('record.txt', '\n ################################################################## \n')


if __name__ == "__main__":
    file = 'aim_test.xlsx'
    name = enumerate(get_info_excel(file, 2)[:847])
    # for index, one in name:
    #     log('record.txt', f"第{index+848}个\n")
    #     get_info(one)
    # for index, one in name:
    #     log('info2.txt', f"第{index}个 {one} \n")
    #     log('info2.txt', '\n')
    #     log('info2.txt', '############### \n')

