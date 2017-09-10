import requests, os, sys, datetime, time, shutil
class TxtDownload(object):
    __path = os.path.join(sys.path[0], "txt")
    def __init__(self, text, delay=0):
        self.__delay = delay
        if os.path.exists(self.__path) and os.path.isdir(self.__path):
            shutil.rmtree(self.__path)
            os.mkdir(self.__path)
        else:
            os.mkdir(self.__path)
    def doDownload(self, title, content):
        with open(os.path.join(self.__path, title + '.txt'), 'wb') as f:
            f.write(bytes(content, 'utf-8'))
