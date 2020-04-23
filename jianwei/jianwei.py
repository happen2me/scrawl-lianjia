#! usr/bin/python
# coding=utf-8
from __future__ import print_function
import os
import requests
from bs4 import BeautifulSoup
from peewee import *

BASE_URL = 'http://210.75.213.188/shh/portal/bjjs2016/'
PAGE = 2940

username = 'root'
password = ''
dbname = 'jianwei'
host = '127.0.0.1'

database = MySQLDatabase(
    dbname,
    host=host,
    port=3306,
    user=username,
    passwd=password,
    charset='utf8',
    use_unicode=True,
)


class BaseModel(Model):

    class Meta:
        database = database


class House(BaseModel):
    id = PrimaryKeyField()
    district = CharField()
    name = CharField()
    type = CharField()
    square = FloatField()
    price = FloatField()
    agency = CharField()
    time = DateField()
    url = CharField()
    direction = CharField()
    floor = CharField()
    total_floor = CharField()
    year = IntegerField()
    decoration = CharField()


def database_init():
    database.connect()
    database.create_tables([House], safe=True)
    database.close()


def get_source_code(url):
    try:
        #result = requests.get(url, headers=hds[random.randint(0,len(hds)-1)])
        result = requests.get(url)
        source_code = result.content
    except Exception as e:
        print(e)
        return

    return source_code


def parse_house(url, info_dict):
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    divtag = soup.find_all('div', class_="infolist_box")
    tds = []
    for dttag in divtag:
        bodytag = dttag.find_all("tbody")
        for body in bodytag:
            trtag = body.find_all("tr")
            for tr in trtag:
                tds.append(tr.findAll('td'))
    try:
        info_dict.update({'direction': tds[1][1].get_text().strip()})
        info_dict.update({'floor': tds[3][0].get_text().strip()})
        info_dict.update({'total_floor': tds[3][1].get_text().strip()})
        info_dict.update({'year': tds[4][0].get_text().strip()})
        info_dict.update({'decoration': tds[5][0].get_text().strip()})
    except:
        pass
    House.insert(**info_dict).upsert().execute()

database_init()
for i in range(0, PAGE + 1):
    tds = []
    source_code = get_source_code(BASE_URL + 'list.aspx?pagenumber=' + str(i))
    soup = BeautifulSoup(source_code, 'lxml')
    divtag = soup.find_all('div', class_="infolist_box")
    for dttag in divtag:
        bodytag = dttag.find_all("tbody")
        for body in bodytag:
            trtag = body.find_all("tr")
            for tr in trtag:
                tds.append(tr.findAll('td'))
    for td in tds:
        info_dict = {}
        info_dict.update({'id': td[0].get_text().strip()})
        info_dict.update({'district': td[1].get_text().strip()})
        info_dict.update({'name': td[2].get_text().strip()})
        info_dict.update({'type': td[3].get_text().strip()})
        info_dict.update({'square': td[4].get_text().strip()})
        info_dict.update({'price': td[5].get_text().strip()[:-2]})
        info_dict.update({'agency': td[6].get_text().strip()})
        info_dict.update({'time': td[7].get_text().strip()})
        info_dict.update({'url': BASE_URL + td[8].a.get('href')})
        parse_house(BASE_URL + td[8].a.get('href'), info_dict)
    print('Page%d Finish' % i)
