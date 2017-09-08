import datetime
import json
import os
import re
import sys
import time

from bs4 import BeautifulSoup

from com.lxing.zhihu.zhihu_search import ZhiHuSearch


class ZhiHuDeal(object):
    __search = None
    __search_url = '/search?type=content&q='
    __search_more = "/r/search?correction=1&type=content&offset="
    __search_offset = 0
    __search_limit = 10
    __answers_more_include = 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics'
    __answers_more_limit = 20
    def __init__(self, text):
        self.__text = text
        self.__search = ZhiHuSearch(self.__text)
        self.__dirpath = os.path.join(sys.path[0], datetime.datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(self.__dirpath) or not os.path.isdir(self.__dirpath):
            os.mkdir(self.__dirpath)
        with open(os.path.join(self.__dirpath, self.__text + ".txt"), 'w') as f:
            f.truncate()
        self.__findAndDealSubject(self.__search_url)

    def __findAndDealSubject(self, url):
        result = self.__search.do_search(url, True)
        if result.status_code == 200:
            if result.apparent_encoding == 'utf-8':
                html = result.content.decode('utf-8')
            else:
                list = json.loads(result.content)['htmls']
                html = ""
                for i in range(len(list)):
                    html += list[i]
        else:
            print("服务器链接失败:"+str(result.status_code))
            return
        soup = BeautifulSoup(html, "html.parser")
        lilist = soup.find_all("li", attrs={'class': re.compile("item")})
        self.__deal_list_subject(lilist)
        self.__search_offset += self.__search_limit
        if len(lilist) is not 0:
            search_more = self.__search_more + str(self.__search_offset) + "&q="
            self.__findAndDealSubject(search_more)

    def __deal_list_subject(self, list):
        if len(list) == 0:
            return
        for i in range(len(list)):
            a = list[i].find("a", attrs={'class': re.compile("js-title-link")})
            if a is not None:
                href = a.get('href')
                if not 'https://zhuanlan.zhihu.com' in href:
                    self.__findAndDealAnswer(href)
                else:
                    continue

    def __findAndDealAnswer(self, url):
        result = self.__search.do_search(self.__search.homeURL + url, False)
        if result.status_code == 200:
            html = result.content.decode('utf-8')
            soup = BeautifulSoup(html, "html.parser")
            question = soup.find('meta', attrs={'itemprop': 'url'}).get("content").replace(self.__search.homeURL+"/question/","")

            data_state = soup.find('div', attrs={'id': 'data'}).get("data-state")
            datas = json.loads(data_state)

            url = datas['question']['answers'][question]['next'].replace(self.__search.homeURL, "")

            meta = soup.find('meta', attrs={'itemprop': re.compile("name")})
            title = meta.get("content")
            self.__write("\n\n\n\n======================================================="+title+"=============================================\n", None)
            answers = datas['entities']['answers']
            for key in answers:
                self.__write(BeautifulSoup(answers[key]['content'], "html.parser").get_text()+"\n", answers[key]['author']['name'])
            self.__continueLoadAnswers(url)
        else:
            print("服务器链接失败:" + str(result.status_code) + " : " + str(result.reason))
            return

    def __continueLoadAnswers(self, url):
        result = self.__search.do_search(url.replace('limit=3', 'limit=100'), False)
        if result.status_code == 200:
            response = json.loads(result.content.decode('utf-8'))
            paging = response['paging']
            datas = response['data']
            for data in datas:
                self.__write('\n'+BeautifulSoup(data['content'], "html.parser").get_text()+'\n', data['author']['name'])
            if not paging['is_end']:
                self.__continueLoadAnswers(paging['next'])
            else:
                return
        else:
            print("服务器链接失败:" + str(result.status_code) + " : " + str(result.reason))
            return

    def __write(self, content, author):
        print("****Waiting"+str(round(time.time()))+"****")
        with open(os.path.join(self.__dirpath, self.__text + ".txt"), 'a+', encoding='utf-8') as f:
            if author is not None:
                f.write("\n**************************"+author+"\n")
            f.write(content)
        f.close()
