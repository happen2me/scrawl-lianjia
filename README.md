# lianjia-scrawler
[![Licenses](https://img.shields.io/badge/license-bsd-orange.svg)](https://opensource.org/licenses/BSD-3-Clause)
+ 该项目提供一个链家网全国房源爬虫工具，数据存储目前支持Mysql,Sqlite和Postgres。非常方便转化成csv等格式文件。
+ 利用Python Pandas ([source code](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/data/lianjia.ipynb))分析链家在线房源数据，本项目提供了一个例子可以参考。
+ 由于链家的反爬虫机制，所以该项目限制了爬虫速度。
+ 此代码仅供学习与交流，请勿用于商业用途，后果自负。
+ 下图为利用爬虫数据做的微信小程序和可视化分析网站。
+ **如果觉得好，请给项目点颗星来支持吧～～** 
![alt text](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/screenshots/wechat.jpg)
![alt text](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/screenshots/homepage_1.png)

## 使用说明
+ 下载源码并安装依赖包
```
1. git clone https://github.com/XuefengHuang/lianjia-scrawler.git
2. cd lianjia-scrawler
# If you'd like not to use [virtualenv](https://virtualenv.pypa.io/en/stable/), please skip step 3 and 4.
3. virtualenv lianjia
4. source lianjia/bin/activate
5. pip install -r requirements.txt
6. python scrawl.py
```

+ 设置数据库信息以及爬取城市行政区信息（支持三种数据库格式）
```
DBENGINE = 'mysql' #ENGINE OPTIONS: mysql, sqlite3, postgresql
DBNAME = 'test'
DBUSER = 'root'
DBPASSWORD = ''
DBHOST = '127.0.0.1'
DBPORT = 3306
CITY = 'bj' # only one, shanghai=sh shenzhen=sh......
REGIONLIST = [u'chaoyang', u'xicheng'] # 只支持拼音
```

+ 运行 `python scrawl.py`! (请注释16行如果已爬取完所想要的小区信息)

+ 可以修改`scrawl.py`来只爬取在售房源信息或者成交房源信息或者租售房源信息

+ 该程序提供两种方式爬取房源信息，一个是根据行政区，另一个是根据小区名。 但是根据行政区的只显示前100页的数据，对于像北京朝阳这种房源比较多的区，最好通过小区名才能爬全。具体内容请看下一部分。


## 相关爬虫函数介绍
```
行政区列表：
regionlist = ['chaoyang', 'haidian'] 目前仅支持拼音

小区列表，可通过GetCommunityByRegionlist爬虫得到
communitylist = [u'万科星园', u'上地东里']

根据行政区来爬虫小区信息, 返回regionlist里面所有小区信息。
core.GetCommunityByRegionlist(city, regionlist)

根据行政区来爬虫在售房源信息， 返回regionlist里面所有在售房源信息。
由于链家限制，仅支持爬前100页数据，可使用GetHouseByCommunitylist。
core.GetHouseByRegionlist(city, regionlist)

根据小区来爬虫在售房源房源信息，返回communitylist里面所有在售房源信息。
core.GetHouseByCommunitylist(city, communitylist)

根据行政区来爬虫出租房源信息，返回regionlist里面所有出租房源信息。
由于链家限制，仅支持爬前100页数据，可使用GetRentByCommunitylist。
core.GetRentByRegionlist(city, regionlist)

根据小区来爬虫出租房源信息，返回communitylist里面所有出租房源信息。
core.GetRentByCommunitylist(city, communitylist)

根据小区来爬虫成交房源信息，返回communitylist里面所有成交房源信息。
部分数据无法显示因为这些数据仅在链家app显示
core.GetSellByCommunitylist(city, communitylist)


```

## 新增[北京建委存放量房源](http://210.75.213.188/shh/portal/bjjs2016/index.aspx)信息爬虫:
+ 代码存放在[`jianwei`](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/jianwei/jianwei.py)目录

## 分析北京住城区房源信息
+ 详情请参考[`data`](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/data/lianjia.ipynb)目录

## 新增[北京我爱我家](https://bj.5i5j.com/)成交房源信息爬虫:
+ 根据`community_id.txt`文件的小区信息爬取各个小区的成交房源信息。
+ 使用方法
```
在scrawl.py中加入
import woaiwojia
woaiwojia.GetSellByCommunitylist()
```

## 更多截图
![alt text](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/screenshots/community_1.png)
