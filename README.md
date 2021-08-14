#  Exhausted-spider

- 一位肚皮朝天的的蜘蛛。
 - 爬虫千千万万，我要走属于自己的一条。现在每个网站防御体制不同，只有不断的磨练，才能爬虫学的好。
 - 以上所有内容我都会粗略讲解，在当时肯定能够实现的，如果后面失效，基本的思路不会怎么变的
 - 鄙人一位暨南大学20本科生，在计算机的道路上越走越远。
 - 欢迎私信我，与我交流，2911567026@qq.com邮件先联系

***

# 介绍

### 前言：

> 为了将每个demo联系起来，采用了仿AOP分层架构，进行了面向对象的再次加工，可以将整个项目克隆下来，然后在对应的层直接进行操作。

### 架构

- [业务层](https://github.com/hengyi666/Exhausted-spider/tree/main/control)
  - 华文处理logo与英文
  - ...
- 数据层
  - 华文处理logo与英文
  - ...
- [实例层](https://github.com/hengyi666/Exhausted-spider/tree/main/demo)
  - 抓取今日头条
  - 抓取微信文章
  - 抓取每日简报
  - 抓取猫眼电影Top100
  - 模拟浏览器抓取淘宝
- [工具层](https://github.com/hengyi666/Exhausted-spider/tree/main/tool)
  - 百度百科搜索
  - 谷歌浏览器搜索
  - 维基百科搜索
- [公共库](https://github.com/hengyi666/Exhausted-spider/blob/main/common.py)
- [数据库](https://github.com/hengyi666/Exhausted-spider/blob/main/database.py)

### 如何使用

> 首先在业务层直接创建对应的任务
>
> 其次根据自己需要引入相关文件
>
> 根据python使用类的规范以及操作对应的函数进行操作
>
> 通过此，能达到快速数据的获取
>
> 然后到数据层下进行对筛选数据的操作
>
> 在数据层可以转换数据类型，处理图片，保存内容等
>
> 最后达到的效果是根据实际情况快速爬虫

### To Do List：

- 谷歌浏览器搜索支持多个关键词的查询
- 多线程的优化

#  拓展

> 这里记录的是 运用的第三方库

 - 代理池  https://github.com/Python3WebSpider/ProxyPool

 - 繁体字-简体字互相转换 https://github.com/skydark/nstools/tree/master/zhtools

 - flashtext 寻找关键词 https://github.com/vi3k6i5/flashtext

 - requirements.txt  我把我所有的库都打包了

   ```python
    pip install -r requirements.txt
   ```
