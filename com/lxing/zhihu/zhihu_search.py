from com.lxing.zhihu.zhihu_login import ZhiHuLogin

class ZhiHuSearch(object):
    homeURL = 'https://www.zhihu.com'
    searchURL = ''
    def __init__(self, text):
        self.__search_text = text
        self.__loginclient = ZhiHuLogin()

    def do_search(self, url, addq):
        self.searchURL = url
        if addq:
            self.searchURL = self.homeURL + self.searchURL + self.__search_text
        soup = self.__loginclient.open(self.searchURL)
        return soup
