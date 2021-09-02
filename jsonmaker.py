###################################################################
"""
在这个区域连接数据库
获得想要操作的数据
开始组装标准格式

例如：
拿到了2个关键词 key
拿到了2个黑名单域名 black_domain
"""
import json

first = dict()
key1 = '华为'
key2 = '加密'
black_domain1 = 'sohu.com'
black_domain2 = 'xinlang.com'

key = dict(enumerate([key1, key2]))
black_domain = dict(enumerate([black_domain1, black_domain2]))
first['key'] = key
first['black_domain'] = black_domain

# 到这里 已经构造出一个了
second = dict.copy(first)  # 我们复制一个用于演示

# 构造整个数组 用于保存
final_list = dict(enumerate([first, second]))
filename = 'demo.json'
with open(filename, 'w') as file_obj:
    json.dump(final_list, file_obj, ensure_ascii=False)
###################################################################
"""
小提示：
demo.json 因为要处理中文，请注意转码
pycharm快捷键整理json格式 为： CTRL + ALT + L 
"""

