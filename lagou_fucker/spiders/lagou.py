# -*- coding: utf-8 -*-
# @Date    : 2017-05-27 15:55:50
# @Author  : fancy (fancy@thecover.co)
import re
import json
import sqlite3
import requests
from urllib import urlencode

from scrapy import Spider, Request, FormRequest


GET_FIRST = lambda x: x[0] if x else ''

# 143992 total_count

class LagouFucker(Spider):
    name = 'lagou_fucker'
    download_delay = 0.5
    start_urls = ['https://www.lagou.com/gongsi/0-0-0']
    company_api = 'https://www.lagou.com/gongsi/0-0-0.json'
    cmps_url = 'https://www.lagou.com/gongsi/%s.html'
    header = {
        'Referer': 'https://www.lagou.com/gongsi/0-0-0',
        'Cookie': 'user_trace_token=20160701161934-8b11c9d3-3f64-11e6-8f4d-525400f775ce; LGUID=20160701161934-8b11cd92-3f64-11e6-8f4d-525400f775ce; TG-TRACK-CODE=jobs_code; SEARCH_ID=c45eb1baafc14948abadb01fd019e1bb; JSESSIONID=ABAAABAAAGFABEF9951A51201660F9EA5286D9E98B356D1; _putrc=60FFC9F2AE6D7E20; login=true; unick=%E8%A2%81%E6%98%8E; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=27; _gat=1; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E6%88%90%E9%83%BD; _gid=GA1.2.257588957.1496200492; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1494127386,1495790417,1495790506; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1496223853; _ga=GA1.2.1798033964.1467361198; LGSID=20170531174400-ace1f827-45e5-11e7-8329-525400f775ce; LGRID=20170531174413-b45a2e2e-45e5-11e7-9545-5254005c3644'
        }
    int_p = re.compile(r'\d+')

    def make_req(self, page_num):
        data = {
            'first': 'false',
            'pn': str(page_num),    # page_number
            'sortField': '0',
            'havemark': '0'
        }
        # body = urlencode(data)
        # req = Request(
        #     self.company_api, method='POST', callback=self.parse,
        #     headers=self.header, dont_filter=True, body=body)
        req = FormRequest(self.company_api, callback=self.parse,
            dont_filter=True, formdata=data, headers=self.header)
        req.meta.update({'page_num': page_num})
        return req

    def start_requests(self):
        self.cnx = sqlite3.connect('sqlite.db')
        self.cur = self.cnx.cursor()
        req = self.make_req(1)
        yield req

    def filter_duplicat(self, url, type=0):
        ''' type: (0, company) (1, jobs)
        '''
        if type == 0:
            sql = 'select count(id) from company where url=?'
        else:
            sql = 'select count(id) from jobs where url=?'
        result = self.cur.execute(sql, (url, )).fetchone()[0]
        return bool(result)

    def parse(self, response):
        with open('company_list.json', 'a') as f:
            f.write('%s\n' % response.body)
        data = json.loads(response.body)
        for cmps in data['result']:
            url = self.cmps_url % cmps['companyId']
            if self.filter_duplicat(url):
                print 'duplicat %s' % url
                continue
            req = Request(url, callback=self.index_parse)
            req.meta['info'] = cmps
            yield req

        page_num = response.meta['page_num']
        yield self.make_req(page_num+1)

        # companys = response.xpath(
        #     '//div[@id="company_list"]/ul/li/dl/dt[1]/a/@href').extract()
        # for url in companys:
        #     pass

    def index_parse(self, response):
        try:
            info = response.meta['info']
            # company = {
            #     'url': response.url,
            #     'brief': info['companyFeatures'],
            #     'name': info['companyFullName'],
            #     'logo': info['companyLogo'],
            #     'shortname': info['companyShortName'],
            #     'process_': info['financeStage'],
            #     'type': info['industryField'],
            #     'interview_rate': info['interviewRemarkNum'],
            #     'resume_rate': info['processRate'],
            #     'city': info['city'],
            #     'jobs_count': info['positionNum']
            # }
            company_info = response.xpath(
                '//script[@id="companyInfoData"]/text()').extract()[0]
            with open('company_info.json', 'a') as f:
                f.write('%s\n' % company_info.encode('utf-8'))
            data = json.loads(company_info)
            data['url'] = response.url
            try:
                data['interview_rate'] = float(
                    response.xpath(
                        '//*[@class="comprehensive-review clearfix"]/span[@class="score"]/text()'
                        ).extract()[0])
            except Exception as e:
                data['interview_rate'] = 0
            count = self.int_p.findall(data['baseInfo']['companySize'])
            try:
                data['baseInfo']['companySize'] = int(count[0])
            except:
                data['baseInfo']['companySize'] = 0
            data['products_brief'] = ','.join(map(
                lambda x: x['product'], data['products']))
            self.save_company(info, data)
        except Exception as e:
            import pdb; pdb.set_trace()

    def save_company(self, info, detail):
        try:
            sql = 'insert into company(name, logo, url, brief, '\
                'comment_count, jobs_count, resume_rate, city_id, '\
                'last_login_text, process_, employee_count, products, '\
                'description, interview_rate, interview_count, shortname) '\
                'values (?,?,?,?, ?,?,?,?, ?,?,?,?, ?,?,?,?)'
            city_id = self.get_target_id('city', 'name', info['city'])
            dataInfo = detail['dataInfo']
            baseInfo = detail['baseInfo']
            a = self.cur.execute(sql, (info['companyFullName'], info['companyLogo'],
                detail['url'], info['companyFeatures'], dataInfo['experienceCount'],
                dataInfo['positionCount'], dataInfo['resumeProcessRate'],
                city_id, dataInfo['lastLoginTime'], baseInfo['financeStage'],
                baseInfo['companySize'], detail['products_brief'],
                detail['introduction']['companyProfile'], detail['interview_rate'],
                dataInfo['experienceCount'], detail['coreInfo']['companyShortName'])
            )
            self.cnx.commit()
            company_id = a.lastrowid
            industryField = map(
                lambda x: x.strip(),
                detail['baseInfo']['industryField'].split(',')
                )
            for field in industryField:
                type_id = self.get_target_id('type', 'name', field)
                self.cur.execute('insert into company_type(company_id, type_id) '\
                    'values(?,?)', (company_id, type_id))
            self.cnx.commit()
            for tag in detail['labels']:
                tag_id = self.get_target_id('tags', 'name', tag)
                self.cur.execute('insert into company_tag(company_id, tag_id) '\
                    'values(?,?)', (company_id, tag_id))
            self.cnx.commit()
        except Exception as e:
            import pdb; pdb.set_trace()


    def get_target_id(self, table, condition, value):
        try:
            res = self.cur.execute(
                'select id from %s where %s=?' % (table, condition),
                (value, )).fetchone()
            if not res:
                a = self.cur.execute(
                    'insert into %s(%s) values(?)' % (table, condition),
                    (value, ))
                return a.lastrowid
            return res[0]
        except Exception as e:
            import pdb; pdb.set_trace()

    def close(self, reason):
        self.cnx.close()


# import threading
# import threadpool


# class SlowLagouFucker(Spider):

#     cnx = None
#     cur = None

#     def __init__(self):
#         self.cnx = sqlite3.connect('sqlite.db')
#         self.cur = self.cnx.cursor()

#     def

