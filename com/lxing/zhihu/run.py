from com.lxing.zhihu.zhuhu_deal import ZhiHuDeal

keyword = input("请输入关键词:")
try:
    ZhiHuDeal(keyword)
except Exception as e:
    print(e)
