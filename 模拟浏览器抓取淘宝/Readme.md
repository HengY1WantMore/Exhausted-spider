#  模拟浏览器抓取淘宝
 

 1. 需要解决cookie
 2. 建议换上代理池
 3. 可以选择无浏览器操作

***
##  关键点

 1. 现在微博登录不行了，所以我选择的是扫码，保存cookie，然后我们进去浏览就不会跳转到登录页面了。
```python
	time.sleep(15)
    Cookies = browser.get_cookies()
    jsonCookies = json.dumps(Cookies)
    with open("taobao_cookies.json", 'w') as f:
        f.write(jsonCookies)
	browser.close()
```
我设置了15秒的时间扫码跳转，然后关闭。


 2. 开始爬取
```python
def get_products():
    wait.until(
        Ec.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item'))
    )
    html =browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        save_to_mongo(product)
```
##  使用步骤
 - 先login登录上去了
 - 再search开始爬取
##  优化建议
爬取20页左右便会叫你输入验证码，用上代理池可以试试。
如果后面成功了，我会传上来的，敬请期待。。。