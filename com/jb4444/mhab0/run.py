import requests
from bs4 import BeautifulSoup as BS
from com.jb4444.mhab0.picdownload import PicDownload
from com.jb4444.mhab0.txtdownload import TxtDownload
class Titlename88(object):
    __homeurl = 'http://【Figure It Out】'
    __listurl = 'http://【Figure It Out】/{0}/{1}.html'
    #图片区
    __pic = 'p0'
    #文学区
    __txt = 't0'

    def __init__(self):
        typename = input("\n\n请选择资源类型【图片/文字】:\n")
        if typename == '图片':
            self.__type = self.__pic
        elif typename == '文字':
            self.__type = self.__txt
        else:
            print("类型输入有误。")
            return
        if self.__type == self.__txt:
            self.__txtdownload = TxtDownload(self.__type)
        for i in range(8):
            i += 1
            self.__i = i
            if self.__type == self.__pic:
                self.__picdownload = PicDownload(self.__type + str(i))
            url = self.__listurl.format(self.__type + str(i), 'index')
            print("*******************************************************************************"+url)
            self.__getListPage(url)
    def __getListPage(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            html = response.content
            soup = BS(html, 'html.parser')
            lilist = soup.find('div', attrs={'id': 'channel'}).find_all('li')
            print(soup.find('div', attrs={'id': 'page'}).find('strong').get_text())
            index = soup.find('div', attrs={'id': 'page'}).find('strong').get_text().split('/')
            for li in lilist:
                detaila = li.find('a')
                if detaila is not None:
                    detailurl = self.__homeurl + detaila.get('href')
                    self.__getTypeMethod(detailurl)

            print(int(index[1]) - int(index[0]))
            if int(index[1]) - int(index[0]) == 0:
                return
            next_url = self.__listurl.format(self.__type + str(self.__i), 'list_' + str(int(index[1]) - int(index[0])))
            print(next_url)
            self.__getListPage(next_url)
    def __getTypeMethod(self,url):
        if self.__type == self.__pic:
            self.__getPicPage(url)
        elif self.__type == self.__txt:
            self.__getTxtPage(url)
        else:
            return
    def __getPicPage(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            print("图片下载成功：" + url)
            html = response.content.decode('utf-8')
            soup = BS(html, 'html.parser')
            imglist = soup.find('div', attrs={'id': 'view1'}).find_all('img')
            for img in imglist:
                if img is None:
                    continue
                img_src = img.get('src')
                if img_src == None:
                    continue
                self.__picdownload.doDownload(img_src)
    def __getTxtPage(self, url):
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            print("文章下载成功："+url)
            html = response.content.decode('utf-8')
            soup = BS(html, 'html.parser')
            title = "0" + str(self.__i) + soup.find("title").get_text().replace('  - 88titlename88', '')
            view2 = soup.find("div", attrs={'id': 'view2'})
            content = ""
            if view2 is not None:
                p = view2.find('p')
                if p is not None:
                    content = p.get_text()
            self.__txtdownload.doDownload(title, content)

Titlename88()