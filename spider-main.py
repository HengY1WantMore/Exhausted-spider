import argparse
import os
import sys
from spider import *
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait as thread_wait

batch_flag = False

parser = argparse.ArgumentParser(
    description='This is a tool for searching keywords to find specified urls',
    epilog='Source on GitHub: https://github.com/hengyi666/Exhausted-spider\nAuthor: Hengyi',
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    '-k',
    '--key',
    required=False,
    type=str,
    help='Keywords to be present in the title'
)
parser.add_argument(
    '-w',
    '--want',
    required=False,
    type=str,
    help='Keywords should exist in the body content'
)
parser.add_argument(
    '-b',
    '--batch',
    required=False,
    type=str,
    help='Specify a JSON file to perform batch check-in. See README.md for details.'
)
parser.add_argument(
    '-m',
    '--max-times',
    required=False,
    default=3,
    type=int,
    help='Number of max_times trying for requesting. Default is 3.'
)
parser.add_argument(
    '-p',
    '--port',
    required=False,
    default=7890,
    type=int,
    help='Port for Agent. Default is 7890.'
)
parser.add_argument(
    '-o',
    '--open',
    action='store_true',
    help='Using the agent'
)
parser.add_argument(
    '-i',
    '--ip',
    required=False,
    default='127.0.0.1',
    type=str,
    help='The default is to run the agent from 127.0.0.1.'
)
parser.add_argument(
    '-s',
    '--pages',
    required=False,
    default=3,
    type=int,
    help='The default browser filters pages.'
)
parser.add_argument(
    '-r',
    '--record',
    required=False,
    default='./record/record1.json',
    type=str,
    help='Write record to the specified path.'
)
parser.add_argument(
    '-t',
    '--thread',
    required=False,
    default=3,
    type=int,
    help='Number of threads for multithreading. Default is 3.'
)
args = parser.parse_args()

# 检测环境变量
key = os.getenv('chromedriver', 'null')
if key == 'null':
    print('- Warning!!!')
    print('- The Chromedriver Environment does not exist!')
    flag = input('Are U sure to continue, if Yes, push 1:')
    if flag != '1':
        print('- GoodBye')
        sys.exit(0)
else:
    print('- Congratulations. The Chromedriver Environment variables have been detected')


# 检测是否存在文件夹
path = '/'.join(args.record.split('/')[:-1])
if not os.path.exists(path):
    print('- No Record folder was detected')
    print(f'- The Record folder will be created at {path}')
    os.mkdir(path)

# 获取名单
new_list = []
if args.batch:
    all_list = ['key', 'want', 'black_domain', 'black_want']
    for x in json.load(open(args.batch, 'r', encoding='utf-8')):
        new_dic = dict()
        new_dic['black_want_flag'] = False
        for k, v in x.items():
            for key, value in v.items():
                if k in all_list:
                    new_dic[k] = v
                if key == 'key' or 'want':
                    batch_flag = True
                if key == 'black_want':
                    new_dic['black_want_flag'] = True
            new_list.append(new_dic)

# 至少存在标题关键词或者内容关键词
if args.key is None and args.want is None and not batch_flag:
    print('- Sorry, Application Error.')
    print('- Reason: At least one title or content keyword exists.')
    sys.exit(0)

# 针对堆项目
if args.batch:
    print('- Separate Settings for --key or --want will not take effect')
    print('- Enter the multithreaded task area')
    print(f'- The number of open threads is {args.thread}')
    if args.thread > 8 or args.thread < 0:
        print(f'- Sorry, The program does not support the set number of threads.')
        sys.exit(0)
    elif args.thread >= 5:
        print('- Easter egg: Oh! You have a computer that works so well.')
        print(f'- Otherwise, check whether the performance meets the standard.')
    else:
        executor = ThreadPoolExecutor(max_workers=args.thread)
        f_list = []
        for each in new_list:
            future = executor.submit(thread_find, each, args.max_times, args.port, args.open, args.ip, args.pages, args.record)
            f_list.append(future)
        thread_wait(f_list)
        print('- Multithreaded task completed')
        print(f"- Please go to the {args.record} to view the results")
        sys.exit(0)

# 针对单一任务
search_way = ''
# 处理关键词  情况一： 只存在标题关键词
if args.key and args.want is None:
    key_str = str(args.key).replace(',', '')
    search_way = key_str
# 处理关键词  情况二： 只存在内容关键词
elif args.want and args.key is None:
    want_str = str(args.want).replace(',', '')
    search_way = 'allintext:' + want_str
# 处理关键词  情况三： 二者都存在
elif args.key and args.want:
    key_str = str(args.key).replace(',', ' ')
    want_str = str(args.want).replace(',', ' ')
    search_way = key_str + ' intext:' + want_str

print("- Start working on a single task")
print(search_way)
Selenium(args.port, args.open, args.max_times, args.ip, args.pages, args.record, None, None, search_way).want_operation(False)
print('- Mission Over.')
print(f"- Please go to the {args.record} to view the results")
sys.exit(0)

