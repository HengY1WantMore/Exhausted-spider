from common import get_multiple_num
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

# browser = webdriver.Chrome('/Users/hengyi/Desktop/chromedriver')
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


class imitation:
    def __init__(self, location, num):
        self.location = location
        self.num = num

    def get_info(self):  # 拿到链接
        want = []
        info = get_multiple_num(self.location, 1)
        index = info.index(str(self.num))
        for each in info[index + 1:]:
            if str(each)[:2] == '--':
                break
            else:
                want.append(each)
        return want

    def operation(self):  # 操作浏览器
        url_info = self.get_info()
        browser.get(url_info[1])
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
    for x in range(3):
        imitation('./record.txt', x).operation()
