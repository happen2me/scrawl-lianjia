# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import settings
import model
import misc
import time
import datetime
import urllib2
import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
BASE_URL = u"http://%s.lianjia.com/" % (settings.CITY)


def get_house_percommunity(communityname):
    url = BASE_URL + u"ershoufang/rs" + \
        urllib2.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_sh_total_pages(url)

    if total_pages == None:
        row = model.Houseinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + \
                u"ershoufang/d%drs%s/" % (page,
                                          urllib2.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("div", {"class": "info"})
        i = 0
        log_progress("GetHouseByCommunitylist",
                     communityname, page + 1, total_pages)
        data_source = []
        hisprice_data_source = []
        for name in nameList:  # per house loop
            i = i + 1
            info_dict = {}
            try:
                housetitle = name.find("div", {"class": "prop-title"})
                info_dict.update({u'title': housetitle.a.get('title')})
                info_dict.update({u'link': housetitle.a.get('href')})
                info_dict.update({u'houseID': housetitle.a.get('key')})

                houseaddr = name.find("span", {"class": "info-col row1-text"})
                info = houseaddr.get_text().split('|')
                info_dict.update({u'housetype': info[0].strip()})
                info_dict.update({u'square': info[1].strip()})
                info_dict.update({u'floor': info[2].strip()})
                try:
                    info_dict.update({u'direction': info[3].strip()})
                except:
                    info_dict.update({u'direction': ''})
                info_dict.update({u'decoration': ''})

                housefloor = name.find("span", {"class": "info-col row2-text"})
                detail = housefloor.get_text().split('|')
                info_dict.update({u'years': detail[-1].strip()})

                community = name.find("a", {"class": "laisuzhou"})
                info_dict.update(
                    {u'community': community.span.get_text().strip()})
                info_dict.update({u'followInfo': ''})

                tax = name.find("div", {"class": "property-tag-container"})
                info_dict.update({u'taxtype': "".join(tax.get_text().split())})

                totalPrice = name.find(
                    "span", {"class": "total-price strong-num"})
                info_dict.update(
                    {u'totalPrice': totalPrice.get_text().strip()})

                unitPrice = name.find(
                    "span", {"class": "info-col price-item minor"})
                info_dict.update({u'unitPrice': unitPrice.get_text().strip()})
            except:
                continue
            # houseinfo insert into mysql
            data_source.append(info_dict)
            hisprice_data_source.append(
                {"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"]})
            # model.Houseinfo.insert(**info_dict).upsert().execute()
            #model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()

        with model.database.atomic():
            model.Houseinfo.insert_many(data_source).upsert().execute()
            model.Hisprice.insert_many(hisprice_data_source).upsert().execute()
        time.sleep(1)


def get_sell_percommunity(communityname):
    url = BASE_URL + u"chengjiao/rs" + \
        urllib2.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_sh_total_pages(url)

    if total_pages == None:
        row = model.Sellinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + \
                u"chengjiao/d%drs%s/" % (page,
                                         urllib2.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetSellByCommunitylist",
                     communityname, page + 1, total_pages)
        data_source = []
        for name in soup.findAll("div", {"class": "info"}):
            i = i + 1
            info_dict = {}
            try:
                housetitle = name.findAll("div", {"class": "info-row"})[0]
                info_dict.update({u'title': housetitle.a.get('title')})
                info_dict.update({u'link': housetitle.a.get('href')})
                info_dict.update({u'houseID': housetitle.a.get('key')})
                houseinfo = housetitle.get_text().strip().split(' ')
                info_dict.update({u'housetype': houseinfo[1].strip()})
                info_dict.update(
                    {u'square': houseinfo[2].strip('').split('\n')[0]})

                houseaddr = name.find("div", {"class": "row1-text"})
                info = houseaddr.get_text().split('|')
                info_dict.update({u'floor': info[0].strip()})
                try:
                    info_dict.update({u'direction': info[1].strip()})
                except:
                    info_dict.update({u'direction': ''})
                info_dict.update({u'status': info[2].strip()})

                years = name.find("span", {"class": "c-prop-tag2"})
                info_dict.update({u'years': years.get_text().strip()})

                community = name.find("span", {"class": "cj-text"})
                info_dict.update({u'community': community.get_text().strip()})

                totalPrice = name.find("span", {"class": "strong-num"})
                info_dict.update(
                    {u'totalPrice': totalPrice.get_text().strip()})

                unitPrice = name.find(
                    "div", {"class": "info-col price-item minor"})
                info_dict.update({u'unitPrice': unitPrice.get_text().strip()})

                source = name.find(
                    "div", {"class": "info-col deal-item minor"})
                info_dict.update({u'source': source.get_text().strip()})

                dealdate = name.find(
                    "div", {"class": "info-col deal-item main strong-num"})
                info_dict.update(
                    {u'dealdate': dealdate.get_text().strip().replace('.', '-')})

            except:
                continue
            # Sellinfo insert into mysql
            data_source.append(info_dict)
            # model.Sellinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            model.Sellinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)


def get_community_perregion(regionname=u'pudong'):
    url = BASE_URL + u"xiaoqu/" + regionname + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_sh_total_pages(url)

    if total_pages == None:
        row = model.Community.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"xiaoqu/" + regionname + "/d%d/" % page
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("div", {"class": "info-panel"})
        i = 0
        log_progress("GetCommunityByRegionlist",
                     regionname, page + 1, total_pages)
        data_source = []
        for name in nameList:  # Per house loop
            i = i + 1
            info_dict = {}
            try:
                communitytitle = name.find("a", {"name": "selectDetail"})
                title = communitytitle.get_text().strip('\n')
                link = communitytitle.get('href')
                id = communitytitle.get('key')
                info_dict.update({u'title': title})
                info_dict.update({u'link': link})
                info_dict.update({u'id': id})

                district = name.find("a", {"class": "ad"})
                info_dict.update({u'district': district.get_text()})

                cons = name.find("div", {"class": "con"})
                bizcircle = cons.findAll("a")
                info_dict.update(
                    {u'bizcircle': bizcircle[1].get_text().strip()})

                try:
                    tagList = name.find("span", {"class": "fang-subway-ex"})
                    info_dict.update({u'tagList': tagList.get_text().strip()})
                except:
                    info_dict.update({u'tagList': ''})

                onsale = name.find("span", {"class": "num"})
                info_dict.update({u'onsale': onsale.get_text().strip()})

                price = name.find("div", {"class": "price"})
                info_dict.update({u'price': price.span.get_text().strip()})

                communityinfo = get_communityinfo_by_url(link)
                for key, value in communityinfo.iteritems():
                    info_dict.update({key: value})

            except:
                continue
            # communityinfo insert into mysql
            data_source.append(info_dict)
            # model.Community.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            model.Community.insert_many(data_source).upsert().execute()
        time.sleep(1)


def get_rent_percommunity(communityname):
    url = BASE_URL + u"zufang/rs" + \
        urllib2.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_sh_total_pages(url)

    if total_pages == None:
        row = model.Rentinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + \
                u"rent/d%drs%s/" % (page,
                                    urllib2.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByCommunitylist",
                     communityname, page + 1, total_pages)
        data_source = []
        nameList = soup.findAll("div", {"class": "info-panel"})
        for name in nameList:
            i = i + 1
            info_dict = {}
            try:
                info = name.find("a", {"name": "selectDetail"})
                info_dict.update({u'title': info.get('title')})
                info_dict.update({u'link': info.get('href')})
                info_dict.update({u'houseID': info.get('key')})

                where = name.find("div", {"class": "where"})
                wheres = where.find_all("span")
                info_dict.update({u'region': wheres[0].get_text().strip()})
                info_dict.update({u'zone': wheres[1].get_text().strip()})
                info_dict.update({u'meters': wheres[2].get_text().strip()})

                other = name.find("div", {"class": "con"})
                info_dict.update({u'other': "".join(other.get_text().split())})

                info_dict.update({u'subway': ""})
                info_dict.update({u'decoration': ""})
                info_dict.update({u'heating': ""})

                price = name.find("div", {"class": "price"})
                info_dict.update(
                    {u'price': int(price.span.get_text().strip())})

                pricepre = name.find("div", {"class": "price-pre"})
                info_dict.update(
                    {u'pricepre': "".join(pricepre.get_text().split())})

            except:
                continue
            # Rentinfo insert into mysql
            data_source.append(info_dict)
            # model.Rentinfo.insert(**info_dict).upsert().execute()

            with model.database.atomic():
                model.Rentinfo.insert_many(data_source).upsert().execute()
            time.sleep(1)


def get_house_perregion(district):
    url = BASE_URL + u"ershoufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_sh_total_pages(url)
    if total_pages == None:
        row = model.Houseinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"ershoufang/%s/d%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetHouseByRegionlist", district, page + 1, total_pages)
        data_source = []
        hisprice_data_source = []
        nameList = soup.findAll("div", {"class": "info"})
        for name in nameList:  # per house loop
            i = i + 1
            info_dict = {}
            try:
                housetitle = name.find("div", {"class": "prop-title"})
                info_dict.update({u'title': housetitle.a.get('title')})
                info_dict.update({u'link': housetitle.a.get('href')})
                info_dict.update({u'houseID': housetitle.a.get('key')})

                houseaddr = name.find("span", {"class": "info-col row1-text"})
                info = houseaddr.get_text().split('|')
                info_dict.update({u'housetype': info[0].strip()})
                info_dict.update({u'square': info[1].strip()})
                info_dict.update({u'floor': info[2].strip()})
                try:
                    info_dict.update({u'direction': info[3].strip()})
                except:
                    info_dict.update({u'direction': ''})
                info_dict.update({u'decoration': ''})

                housefloor = name.find("span", {"class": "info-col row2-text"})
                detail = housefloor.get_text().split('|')
                info_dict.update({u'years': detail[-1].strip()})

                community = name.find("a", {"class": "laisuzhou"})
                info_dict.update(
                    {u'community': community.span.get_text().strip()})
                info_dict.update({u'followInfo': ''})

                tax = name.find("div", {"class": "property-tag-container"})
                info_dict.update({u'taxtype': "".join(tax.get_text().split())})

                totalPrice = name.find(
                    "span", {"class": "total-price strong-num"})
                info_dict.update(
                    {u'totalPrice': totalPrice.get_text().strip()})

                unitPrice = name.find(
                    "span", {"class": "info-col price-item minor"})
                info_dict.update({u'unitPrice': unitPrice.get_text().strip()})
            except:
                continue
            # houseinfo insert into mysql
            data_source.append(info_dict)
            hisprice_data_source.append(
                {"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"]})
            # model.Houseinfo.insert(**info_dict).upsert().execute()
            #model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()

            with model.database.atomic():
                model.Houseinfo.insert_many(data_source).upsert().execute()
                model.Hisprice.insert_many(
                    hisprice_data_source).upsert().execute()
            time.sleep(1)


def get_rent_perregion(district):
    url = BASE_URL + u"zufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_sh_total_pages(url)
    if total_pages == None:
        row = model.Rentinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"zufang/%s/d%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByRegionlist", district, page + 1, total_pages)
        data_source = []
        nameList = soup.findAll("div", {"class": "info-panel"})
        for name in nameList:
            i = i + 1
            info_dict = {}
            try:
                info = name.find("a", {"name": "selectDetail"})
                info_dict.update({u'title': info.get('title')})
                info_dict.update({u'link': info.get('href')})
                info_dict.update({u'houseID': info.get('key')})

                where = name.find("div", {"class": "where"})
                wheres = where.find_all("span")
                info_dict.update({u'region': wheres[0].get_text().strip()})
                info_dict.update({u'zone': wheres[1].get_text().strip()})
                info_dict.update({u'meters': wheres[2].get_text().strip()})

                other = name.find("div", {"class": "con"})
                info_dict.update({u'other': "".join(other.get_text().split())})

                info_dict.update({u'subway': ""})
                info_dict.update({u'decoration': ""})
                info_dict.update({u'heating': ""})

                price = name.find("div", {"class": "price"})
                info_dict.update(
                    {u'price': int(price.span.get_text().strip())})

                pricepre = name.find("div", {"class": "price-pre"})
                info_dict.update(
                    {u'pricepre': "".join(pricepre.get_text().split())})

            except:
                continue
            # Rentinfo insert into mysql
            data_source.append(info_dict)
            # model.Rentinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            model.Rentinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)


def get_communityinfo_by_url(url):
    source_code = misc.get_source_code(BASE_URL + url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    communityinfos = soup.findAll("div", {"class": "col-2 clearfix"})
    res = {}
    for info in communityinfos:
        try:
            infos = info.findAll("li")
            housetype = infos[0].find("span", {"class": "other"})
            year = infos[1].find("span", {"class": "other"})
            cost = infos[2].find("span", {"class": "other"})
            service = infos[3].span.find(text=True, recursive=False)
            company = infos[4].span.find(text=True, recursive=False)
            res.update({'housetype': housetype.get_text().strip()})
            res.update({'year': year.get_text().strip()})
            res.update({'cost': cost.get_text().strip()})
            res.update({'service': service.strip()})
            res.update({'company': company.strip()})

        except:
            continue
    return res


def check_block(soup):
    if soup.title.string == "414 Request-URI Too Large":
        logging.error(
            "Lianjia block your ip, please verify captcha manually at lianjia.com")
        return True
    return False


def log_progress(function, address, page, total):
    logging.info("Progress: %s %s: current page %d total pages %d" %
                 (function, address, page, total))
