# 信息收集爬虫框架

[![build](https://github.com/SO-JNU/stuhealth/workflows/build/badge.svg)](https://github.com/SO-JNU/stuhealth/actions)

Python 编写的进行数据筛选与收集工具。
##  快速部署
```bash
# git下载
$ git clone https://github.com/hengyi666/Exhausted-spider.git
```
##  快速上手

```bash
# 首次使用需要安装依赖
$ pip3 install -r requirements.txt

# 进行单次查询
$ python3 spider-main.py -k '字节' -w '取消大小周'

# 批量查询
$ python3 spider-main.py -b demo.json
```

## 参数说明

| 参数          | 简写 | 说明                                                         |
| ------------- | ---- | :----------------------------------------------------------- |
| `--key`       | `-k` | 查找锚标题，可能跳转到其他地方，涉及面更广<br>Google会限制搜索结果必须是那些在anchor文字里包含了我们所有查询关键词的网页<br/>请用逗号隔开！ |
| `--want`      | `-w` | 查找正文内容出现地关键词<br />Google的allintext在网页内容里查找字符串<br />请用逗号隔开 |
| `--batch`     | `-b` | 批量处理文件                                                 |
| `--max-times` | `-m` | 允许请求的最大次数                                           |
| `--port`      | `-p` | 开启代理的端口，默认为7890                                   |
| `--open`      | `-p` | 是否开启代理，默认是开启                                     |
| `--ip`        | `i`  | 代理走的ip，默认是`127.0.0.1`本机                            |
| `--pages`     | `-p` | 请求页数，默认是3页                                          |
| `--record`    | `-r` | 记录的位置，默认是`./record/record.json`                     |
| `--thread`    | `-t` | 开启的线程数，默认是3个线程                                  |
| `--help`      | `-h` | 显示参数说明。                                               |

##  文件目录

```
├─ record
│  ├─ recoed,json
│  
├─   common.py 公共库
│
├─   database.py 数据库包装
│
├─   demo.json 样式.json
│
├─   jsonmaker.py json生成器
│
├─   requirements.txt 依赖包
│
├─   seleImitation.py 模拟筛选
│
├─   spider-main.py 操作文件
│
├─   spider.py  项目文件
│
├─   demo 我写的一些样例小项目
└─
```

##  注意事项

> 1. 首先会检测环境变量中是否存在
>    - 若强制通过后，报错请到百度自行解决下
> 2. 会检测保存路径所在的文件夹是否存在
>    - 若不存在，则会自动创建
> 3. 面对多线程处理，请根据你的电脑要求酌情选择线程数
>    - 这里我推荐的是3个线程
>    - 线程选择的范围是 0-8个
>    - 高于5个将会触发彩蛋

##  说明书

>- 单次查询 不支持黑名单选项以及过滤词
>
>- 线程查询 支持黑名单选项以及过滤词
>- 选择存在过滤词时 ：筛选效率会大大降低，请酌情选择

- 信息按照以下格式示例保存为 JSON 文件：

```json
[{
  "0": { "key": {"0": "华为","1": "加密"},
        "black_domain": {"0": "sohu.com","1": "xinlang.com"},
    	"black_want" :{"0": "歌手","1": "演员"}
  },
  "1": {"key": {"0": "华为","1": "加密"},
        "black_domain": {"0": "sohu.com","1": "xinlang.com"},
    	"black_want" :{"0": "歌手","1": "演员"}
}]
```

- 处理完后，请到默认保存路径的`./record/record.json`下

  - 在头部＋一个`[`
  - 在尾部+一个`]`
  - 并删掉最后一行的`,`

  这样会形成新的处理文件，方便下一步的筛选

##  使用教程

###  第一步：创建json用于数据的查找以及筛选

> 1. 使用`database.py`或者`common.py`读取数据库文件或者excel表格
>
> 2. 到`jsonmaker.py`文件下开始组装
>
>    ```PYTHON
>    import json
>    """
>    小提示：
>    demo.json 因为要处理中文，请注意转码
>    pycharm快捷键整理json格式 为： CTRL + ALT + L 
>    通常是for循环创建，这里我就拿具体的例子进行演示
>    """
>    first = dict()
>    key1 = '华为'
>    key2 = '加密'
>    black_domain1 = 'sohu.com'
>    black_domain2 = 'xinlang.com'
>    
>    key = dict(enumerate([key1, key2]))
>    black_domain = dict(enumerate([black_domain1, black_domain2]))
>    first['key'] = key
>    first['black_domain'] = black_domain
>    
>    second = dict.copy(first)  # 我们复制一个用于演示
>    
>    # 构造整个数组 用于保存
>    final_list = dict(enumerate([first, second]))
>    filename = 'demo.json'
>    with open(filename, 'w') as file_obj:
>        json.dump(final_list, file_obj, ensure_ascii=False)
>    ```
>
> 3. 到生成的`demo.json`下头尾分别加上`[` 和`]` 

### 第二步：开始任务

>在终端输入
>
>```bash
>$ python3 spider-main.py -b demo.json
>```
>
>根据提示进行操作

###   第三步：筛选数据

> 1. 进入`seleImitation.py` 中
>
>    ```python
>    if __name__ == '__main__':
>        location = './record/record.json'
>        res = json.load(open(location, 'r', encoding='utf-8'))
>        for x in range(len(res)):
>            imitation(res[x]).operation()
>    ```
>
> 2. 请根据具体的情况更改
>
> 3. >详情：
>    >
>    >这个是为了方便你不用将收集下来的连接一个个打开
>    >如果使用的是多线程进行
>    >那么会根据你的线程数
>    >例如 5个线程数 * 3 页
>    >那么就要根据标题自行规整到指定区域
>    >
>    >这个文件通过读取json格式，一口气打开所涉及的网站
>    >之后在不关掉的前提下，可以自行地安装插件
>    >也可以自行地打开新的标签进行浏览
>    >最后在控制台敲1 进行下一个循环
>    >如果中途需要退出
>    >那么直接结束程序即可

##  计划

> 1. 根据json文件进行整理
>
>    > 这个的化，老版本我是用的希尔排序根据index排序的
>    >
>    > 而这个会从source的出现顺序以及page进行归类
>    >
>    > 如果笨办法是有，但复杂度套高了
>    >
>    > 所以期待大佬们的pr
>

> `期待更新，也期待大佬们的建议与pr`
=======
> 最后达到的效果是根据实际情况快速爬虫

###  计划

> - 指定页数翻页查询
> - ban掉禁用词语
> - 准备大更新


##  拓展

- 代理池 https://github.com/Python3WebSpider/ProxyPool
- 繁体字-简体字互相转换 https://github.com/skydark/nstools/tree/master/zhtools
- flashtext 寻找关键词 https://github.com/vi3k6i5/flashtext



