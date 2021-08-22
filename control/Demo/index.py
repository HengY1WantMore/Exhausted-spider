from tool.googleSelenium import *
from tqdm import tqdm

if __name__ == '__main__':
    # 参数设置
    white_list = ['facebook', 'youtube']
    black_list = ['sohu']
    length = None
    is_open = 1
    max_times = 3
    # list_info = ['俄罗斯中华文化教育促进会', '阿根廷华文教育基金会', '南非中文教师协会', '中韩子女教育协会', '德国华达中文学校', '内卡河畔华文学堂', '全美中文学校协会']
    list_info = ['淘宝', '京东', '淘宝', '京东', '淘宝', '京东']
    # 开始任务
    print('Mission Start')
    executor = ThreadPoolExecutor(max_workers=5)
    f_list = []
    for index, each_index in enumerate(list_info):
        one_info = {
            'index': index,
            'key': each_index,
            'want': ['logo', '服装'],
            'num': 2,
            'withe': white_list,
            'black': black_list,
            'length': length,
            'is_open': is_open,
            'max_times': max_times,
        }
        future = executor.submit(multithreading, one_info)
        f_list.append(future)
    thread_wait(f_list)
    # 进行重新排序
    all_info = shellSort(all_info)
    print('Start Reordering')
    for each_one in tqdm(all_info):
        log('./record_sort.txt', f"{each_one['index']}\n")
        for url_handle in each_one['res']:
            log('./record_sort.txt', f"{url_handle}\n")
        for url_protect in each_one['protect']:
            log('./record_sort.txt', f"{url_protect}\n")
        log('./record_sort.txt', f"--##########################################\n")
    print('Mission Over')
