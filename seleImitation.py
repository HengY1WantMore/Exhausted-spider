"""
这个是为了方便你不用将收集下来的连接一个个打开
如果使用的是多线程进行
那么会根据你的线程数
例如 5个线程数 * 3 页
那么就要根据标题自行规整到指定区域

这个文件通过读取json格式，一口气打开所涉及的网站
之后在不关掉的前提下，可以自行地安装插件
也可以自行地打开新的标签进行浏览
最后在控制台敲1 进行下一个循环
如果中途需要退出
那么直接结束程序即可
"""

import json
from common import get_multiple_num
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


class imitation:
    def __init__(self, each):
        self.each = each
        self.source = ''
        self.page = 1

    def get_info(self):  # 拿到链接
        self.source = self.each['source']
        self.page = self.each['page']
        url_list = list(self.each['url'].values())
        return url_list

    def operation(self):  # 操作浏览器
        url_info = self.get_info()
        print(f'目标：{self.source} 页数：{self.page}')
        browser.get(url_info[0])
        length = len(url_info)
        if length >= 2:
            for each in url_info[1:]:
                browser.execute_script(f"window.open('{each}')")
        input_flag = input('完成后请输入1')
        while input_flag != str(1):
            input_flag = input('完成后请输入1,否则退出手动退出程序')
        handles = browser.window_handles
        for handle in handles:
            if handle != browser.current_window_handle:
                browser.close()
                browser.switch_to.window(handle)


if __name__ == '__main__':
    location = './record/record.json'
    res = json.load(open(location, 'r', encoding='utf-8'))
    for x in range(len(res)):
        imitation(res[x]).operation()
