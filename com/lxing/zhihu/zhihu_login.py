import requests
import time, json, os, sys, subprocess, queue
from bs4 import BeautifulSoup as BS
class ZhiHuLogin(object):
    TYPE_PHONE_NUM = 'phone_num'
    TYPE_EMAIL = 'email'
    loginURL = r'http://www.zhihu.com/login/{0}'
    homeURL = r'http://www.zhihu.com'
    captchaURL = r"http://www.zhihu.com/captcha.gif"
    user_agent_list = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'
                  ,'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
                  ,'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
                  ,'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'
                  ,'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
                  ,'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "www.zhihu.com",
        "Upgrade-Insecure-Requests": "1",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "authorization": ""
    }
    proxies = {'http': 'http://120.76.55.49:8088'}
    captchaFile = os.path.join(sys.path[0], "captcha.gif")
    cookieFile = os.path.join(sys.path[0], "cookie")

    def __init__(self ):
        os.chdir(sys.path[0])
        self.__session = requests.Session()
        authorization_path = os.path.join(sys.path[0], 'authorization')
        if os.path.exists(authorization_path) and os.path.isfile(authorization_path):
            with open(os.path.join(authorization_path), 'r') as f:
                auth = f.read()
                if not auth == '':
                    self.headers['authorization'] = auth
        else:
            print("Error:因登录系统无法获取身份认证信息authorization，请自行获取并在同级目录下新建名为authorization文件并将authorization写入")
        self.__session.headers = self.headers
        self.__cookie = self.loadCookie()
        self.__user_agent = queue.Queue()
        for user_agent in self.user_agent_list:
            self.__user_agent.put(user_agent)
            self.__user_agent.put(user_agent)
        if self.__cookie:
            self.__session.cookies.update(self.__cookie)
        else:
            print("没有找到cookie文件，请调用login方法登录一次！")
            self.__username = input("\n请输入手机号:")
            self.__password = input("\n请输入密码:")
            self.__login()

    def __login(self):
        self.__loginURL = self.loginURL.format(self.__getUsernameType())
        html = self.open(self.homeURL).text
        soup = BS(html, "html.parser")
        _xsrf = soup.find("input", {"name": "_xsrf"})["value"]

        while True:
            captcha = self.open(self.captchaURL).content
            with open(self.captchaFile, 'wb') as output:
                output.write(captcha)
            print("=" * 50)
            print("已打开验证码图片，请识别:")
            subprocess.call(self.captchaFile, shell=True)
            captcha = input("请输入验证码:")
            os.remove(self.captchaFile)

            data = {
                "_xsrf": _xsrf,
                "password": self.__password,
                "remember_me": "true",
                self.__getUsernameType(): self.__username,
                "captcha": captcha
            }
            res = self.__session.post(self.__loginURL, data=data)
            print("=" * 50)
            if res.status_code == 200:
                print("登录成功")
                self.__saveCookie()
                break
            else:
                print("登录失败")
                print("错误信息 --->", res.json()["msg"])

    def __getUsernameType(self):
        """判断用户名类型
        经测试，网页的判断规则是纯数字为phone_num，其他为email
        """
        if self.__username.isdigit():
            return self.TYPE_PHONE_NUM
        return self.TYPE_EMAIL

    def __saveCookie(self):
        """cookies 序列化到文件
        即把dict对象转化成字符串保存
        """
        with open(self.cookieFile, "w") as output:
            sessions = self.__session.cookies
            cookies = sessions.get_dict()
            json.dump(cookies, output)
            print("=" * 50)
            print("已在同目录下生成cookie文件：", self.cookieFile)

    def loadCookie(self):
        """读取cookie文件，返回反序列化后的dict对象，没有则返回None"""
        if os.path.exists(self.cookieFile):
            print("=" * 50)
            with open(self.cookieFile, "r") as f:
                cookie = json.load(f)
                return cookie
        return None

    def open(self, url, delay=2, timeout=10):
        """打开网页，返回<a href="https://www.baidu.com/s?wd=Response%E5%AF%B9%E8%B1%A1&tn=44039180_cpr&fenlei=mv6quAkxTZn0IZRqIHckPjm4nH00T1dBPAFhPWf3n1mzPymvmhf0IAYqnWm3PW64rj0d0AP8IA3qPjfsn1bkrjKxmLKz0ZNzUjdCIZwsrBtEXh9GuA7EQhF9pywdQhPEUiqkIyN1IA-EUBtdPWc3nHc4rH6zP1T4njf3Pjf" target="_blank" class="baidu-highlight">Response对象</a>"""
        if delay:
            time.sleep(delay)
        user_agent = self.__user_agent.get()
        self.headers['User-Agent'] = user_agent
        self.__user_agent.put(user_agent)
        self.__session.headers = self.headers
        return self.__session.get(url, timeout=timeout)

    def getSession(self):
        return self.__session


