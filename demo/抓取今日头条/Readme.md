#  今日头条
 - 这个还是比较简单的，中规中矩。
 - 其中的cookie等其他数据，可以先用浏览器跑一遍记录下来。
 - 因为我不能保证是否过期了。
***
##  关键点
```python
def get_page_detail(url):
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    response = requests.get(url, headers=header)
    Location = response.history[1].headers['Location']
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'cookie': 'MONITOR_WEB_ID=ea59629f-01a6-439d-8874-cc8b7cd5753a; tt_webid=6972174752517834277; '
                  'ttcid=999598b8d4e041fd9f3430799ddd46fb40; csrftoken=4275442e0e2606d73174f88366a704f5; '
                  'tt_webid=6972174791597327884; _S_DPR=1; _S_IPAD=0; FRM=new; PIXIEL_RATIO=1; WIN_WH=1920_258; '
                  '_S_WIN_WH=1920_607; __ac_nonce=060c31ee100e439b83679; '
                  '__ac_signature=_02B4Z6wo00f01X3xdcwAAIDAqjdYtuVUaMV91XFAAD'
                  '.DoOUxpWK4q7ID81tjZ3dof5JEe5TXezk6bmCBsfBWp7dyIiEzVB'
                  '-oES80VpJSPZW2KaVLXyy158jscrGnT7bDVlzUhPHY2kjSrEKhef; '
                  's_v_web_id=verify_kps2nerm_BD5KmYF5_SpIY_40oU_Ax1O_uBMkzj9ilAY5; '
                  'ttwid=1%7CsvA4DAjzDo2S1tCI3XlLmW8UXaVg70o-H-NKvnoBlpY%7C1623400346'
                  '%7C40078901d5dd652c35345368cee2611f90d66189a7e0069c7d823173d401441c; '
                  'tt_scid=58wlylcC46FFZhmNU6KavcoEwTcrcIWcItR6lOB9jYgqMiXRQRvix479F6hQsk4gba2c '
    }
    response = requests.get(Location, headers=header)
    try:
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求出错')
        return None
```
**Location = response.history[1].headers['Location']**
你的明白他的跳转中带的地址就是我们想要的，然后直接拿下来！
搞定