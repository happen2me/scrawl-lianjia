#! usr/bin/python #coding=utf-8
import os
import requests
from bs4 import BeautifulSoup
from datetime import timedelta, date
from peewee import *
import model
import time
import logging
import misc

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def find_between_r(s, first, last):
    try:
        start = s.rindex(first) + len(first)
        end = s.rindex(last, start)
        return s[start:end]
    except ValueError:
        return ""


def get_totalpage(url):
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    info = soup.find("div", {"class": "pageSty rf"})
    if info == None:
        return 1
    alist = info.find_all("a")
    try:
        page = int(alist[1].get_text().strip())
    except:
        page = 1
    return page


def GetSellByCommunitylist():
    with open('community_id.txt') as f:
        for line in f.readlines():
            data_source = []
            code = line.split(' ')[0]
            communityinfo = line.split(' ')[1]
            pages = get_totalpage("https://bj.5i5j.com/sold/%s" % code)
            for page in range(1, pages + 1):
                source_code = misc.get_source_code(
                    "https://bj.5i5j.com/sold/%s/n%d/" % (code, page))
                soup = BeautifulSoup(source_code, 'lxml')
                content = soup.find('ul', class_="pList zu")
                try:
                    lists = content.find_all('li')
                except:
                    continue

                for each in lists:
                    info_dict = {}
                    sTit = each.find("p", {"class": "sTit"})
                    title = sTit.strong.get_text().strip()
                    community = title.split(' ')[0]
                    listCon = each.find("div", {"class": "listCon"})
                    plist = listCon.find_all("p")
                    housetype = plist[1].get_text().strip().split(u'·')[0]
                    square = plist[1].get_text().strip().split(u'·')[1]
                    direction = plist[1].get_text().strip().split(u'·')[2]
                    dealdate = plist[2].get_text().strip().split(u'：')[1]
                    jiage = each.find("div", {"class": "jiage"})
                    totalPrice = jiage.strong.get_text().strip()
                    unitPrice = find_between_r(
                        jiage.p.get_text().strip(), u'价', u'元')
                    source = u"我爱我家"
                    status = u"暂无信息"
                    floor = u"暂无信息"
                    years = u"暂无信息"
                    link = "https://bj.5i5j.com%s" % each.a.get("href")
                    houseID = "5i5j%s" % find_between_r(
                        each.a.get("href"), '/', '.')
                    info_dict.update({u'title': title})
                    info_dict.update({u'houseID': houseID})
                    info_dict.update({u'link': link})
                    info_dict.update({u'community': community})
                    info_dict.update({u'years': years})
                    info_dict.update({u'housetype': housetype})
                    info_dict.update({u'square': square})
                    info_dict.update({u'direction': direction})
                    info_dict.update({u'floor': floor})
                    info_dict.update({u'status': status})
                    info_dict.update({u'source': source})
                    info_dict.update({u'totalPrice': totalPrice})
                    info_dict.update({u'unitPrice': unitPrice})
                    info_dict.update({u'dealdate': dealdate})
                    data_source.append(info_dict)

            with model.database.atomic():
                try:
                    model.Sellinfo.insert_many(data_source).upsert().execute()
                except:
                    pass
            logging.info("%s finish" % communityinfo)
            time.sleep(1)
