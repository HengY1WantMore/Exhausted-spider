#  搜狗来抓取微信原文

 - 这个算偏难的了，我会把关键点讲清楚

***
##  关键点

 1. cookie 先到 https://weixin.sogou.com/ 下登录你的微信，打开F12刷新，看到请求头里面的cookie复制下来
 2. type = 2 是代表文章的意思
 3. 根据拿到的url构造新的url，他比我们拿到的差点参数
```python
def get_detail(url):
    global true_url
    header = {
        'Cookie': '#'
    }
    b = int(random.random() * 100) + 1
    a = url.find("url=")
    result_url = url + "&k=" + str(b) + "&h=" + url[a + 4 + 21 + b: a + 4 + 21 + b + 1]
    url = "https://weixin.sogou.com" + result_url
    response_html = requests.get(url, headers=header).text.replace(' ', '')
    pattern = re.compile('url\+=\'(.*?);', re.S)
    items = re.findall(pattern, response_html)
    true_url = ''.join(items).replace('\'', '')
    try:
        response = requests.get(true_url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None
```
我直接把答案贴出来了
4. 后面的就是正常的分析和储存了
5. 注：只要拿到了微信本身的url，微信是没有爬虫的限制的

##  使用建议
 - 在本地部署proxypool 　https://github.com/Python3WebSpider/ProxyPool
 - 可以使用mongo，也可以使用mysql
