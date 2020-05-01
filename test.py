from bs4 import BeautifulSoup
import misc
from core import check_block


def has_span_with_class_label(tag):
    return tag.name=='li' and tag.find('span')


def get_house_by_url(url):
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return

    intro = soup.find(id="introduction")
    transaction_labels = intro.find_all(has_span_with_class_label)
    name_dict={
        u'配备电梯': 'elevator',
        u'产权所属': 'propertytype',
        u'建筑结构': 'buildingstructure',
        u'建筑类型': 'buildingtype',
        u'梯户比例': 'elevatorratio',
        u'交易权属': 'transactionownership'
    }
    res = {}
    for label in transaction_labels:
        spans = label.find_all("span")
        if len(spans) > 1:
            key = spans[0].string.strip()
            val = spans[1].string.strip()
            if key in name_dict:
                res[name_dict[key]] = val
        elif len(spans) > 0:
            key = spans[0].string.strip()
            val = label.get_text()
            if key in name_dict:
                res[name_dict[key]] = val
    return res


if __name__ == "__main__":
    url = "https://cd.lianjia.com/ershoufang/106103490739.html"
    res = get_house_by_url(url)
    print(res)