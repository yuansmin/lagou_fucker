# -*- coding: utf-8 -*-

import re
import hashlib
import requests

def login():
    login_url = 'https://passport.lagou.com/login/login.html'
    res = requests.get(login_url)
    token = re.findall(r'X_Anti_Forge_Token.*?=.*?\'(.*?)\'', res.text)[0]
    code = re.findall(r'X_Anti_Forge_Code.*?=.*?\'(.*?)\'', res.text)[0]
    print token, code
    raw_password = '2345678'
    first_encode = hashlib.md5(raw_password).hexdigest()
    g = 'veenike'
    password = hashlib.md5(g + first_encode + g).hexdigest()
    headers = {
        "X-Anit-Forge-Code": code,
        "X-Anit-Forge-Token": token,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Host": "passport.lagou.com",
        "Origin": "https://passport.lagou.com",
        "Referer": "https://passport.lagou.com/login/login.html",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "user_trace_token=20160701161934-8b11c9d3-3f64-11e6-8f4d-525400f775ce; LGUID=20160701161934-8b11cd92-3f64-11e6-8f4d-525400f775ce; index_location_city=%E6%88%90%E9%83%BD; login=false; unick=""; _putrc=""; JSESSIONID=ABAAABAAADGAACF861EB85D0879915F5E503DDD3CCB038A; X_HTTP_TOKEN=250b525cb7bde28801a8da2858919a49; _ga=GA1.2.1798033964.1467361198; _gid=GA1.2.1516935373.1496287125; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1494127386,1495790417,1495790506; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1496287125; _ga=GA1.3.1798033964.1467361198; LGSID=20170601111845-053ba028-4679-11e7-86f3-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2F; PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html%3Fts%3D1496281698842%26serviceId%3Dlagou%26service%3Dhttps%25253A%25252F%25252Fwww.lagou.com%25252F%26action%3Dlogin%26signature%3DA823E3FA1641558EFF21BD277AC52134; LGRID=20170601111845-053ba290-4679-11e7-86f3-525400f775ce",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    data = {
      'isValidate': 'true',
      'username': 'yuansmin@sina.com',
      'password': password,
      'request_form_verifyCode': '',
      'submit': ''
    }
    url = 'https://passport.lagou.com/login/login.json'
    res = requests.post(url, data=data, headers=headers)
    print res.text

if __name__ == '__main__':
    login()
