from urllib.parse import urlencode
from common import list_split
from common import get_multiple_num
from selenium import webdriver

if __name__ == '__main__':
    name_list = []
    url_list = []
    info = get_multiple_num('./transaction/huashang/record.txt', 1)
    for index, each in enumerate(info):
        each = each.split(' ')
        name = each[0].split('-')[1]
        name_list.append(name.replace(':', ''))

    for each in name_list:
        data = {'keyword': each, }
        name_encode = str(urlencode(data)).split('=')[1]
        url = 'https://baike.baidu.com/item/' + name_encode
        # url = 'https://zh.wikipedia.org/wiki/' + name_encode
        url_list.append(url)
    new_url = list_split(url_list, 5)
    # print(new_url)

    option = webdriver.ChromeOptions()
    option.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(options=option)
    for one in new_url:
        browser.get(one[0])
        length = len(one)
        if length >= 2:
            for each in one[1:]:
                browser.execute_script(f"window.open('{each}')")
        input_flag = input('完成后请输入1')
        while input_flag != str(1):
            input_flag = input('完成后请输入1,否则退出手动退出程序')
        handles = browser.window_handles
        for handle in handles:
            if handle != browser.current_window_handle:
                browser.close()
                browser.switch_to.window(handle)
