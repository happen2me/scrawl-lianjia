import core
import model
import settings
import logging


def get_communitylist(city):
    res = []
    for community in model.Community.select():
        if community.city == city:
            res.append(community.title)
    return res


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    regionlist = settings.REGIONLIST  # only pinyin support
    city = settings.CITY
    model.database_init()
    logging.info("Scrawling House Info")
    core.GetHouseByRegionlist(city, regionlist)
    # core.GetRentByRegionlist(city, regionlist)
    # Init,scrapy celllist and insert database; could run only 1st time
    # logging.info("Scrawling Community Info")
    # core.GetCommunityByRegionlist(city, regionlist)
    # communitylist = get_communitylist(city)  # Read celllist from database
    # core.GetSellByCommunitylist(city, communitylist)
