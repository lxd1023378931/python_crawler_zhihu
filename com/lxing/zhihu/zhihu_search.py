from com.lxing.zhihu.zhihu_login import ZhiHuLogin

class ZhiHuSearch(object):
    homeURL = 'https://www.zhihu.com'
    def __init__(self, text):
        self.__search_text = text
        self.__loginclient = ZhiHuLogin()

    def do_search(self, url, addq, auth=False):
        self.__searchURL = url
        if addq:
            self.__searchURL = self.homeURL + self.__searchURL + self.__search_text
        soup = self.__loginclient.open(self.__searchURL, auth=auth)
        return soup
