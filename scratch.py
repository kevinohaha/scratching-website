#可参考网站：简书，CSDN
#爬取成功：
#	基金协会，中信证券，天眼查
#爬取失败：
#	东方财富
#数据接口：
#	天眼查（付费，但是有漏洞，似乎仅仅在第一次使用时扣费，之后不再扣费），tushare(开源免费)
#爬取上万条数据后最好使用try except机制更robust

#1.pyechart 绘图
from pyecharts import Bar 
bar = Bar('贷款加权平均利率','单位：%')
kwargs = dict(
    name = '月份',
    x_axis = ['2016.03','2016.06','2016.09','2016.12','2017.03','2017.06','2017.09','2017.12','2018.03','2018.06','2018.09','2018.12','2019.03' ],
              y_axis = [5.24,
                        5.2,

                        5.15,
                        
                        5.22,
                        
                        5.45,
                        
                        5.6,
                        
                        5.71,
                        
                        5.71,
                        
                        5.91,
                        
                        5.94,
                        
                        5.92,
                        5.64,
                        5.69
                        ]
)
bar.add(**kwargs)
bar.render('bar01.html')

from pyecharts import Bar 
bar = Bar('国内十大券商排名','净资产')
kwargs = dict(
    name = '券商名称',
    x_axis = ['中信证券','国泰君安','海通证券','华泰证券','广发证券','招商证券',
'申万宏源','银河证券','国信证券','东方证券',],
    y_axis = [13050,12352,10965,10059,7961,7795,6490,6471,
5152,5127]
)
bar.add(**kwargs)
bar.render('bar02.html')

******************************************************************
#2.爬虫静态网页通用例1（看源码筛选标签）：（headers的内容根据自身电脑网页进行更改）
import urllib
from urllib.request import urlopen
from urllib.error import HTTPError,URLError
from bs4 import BeautifulSoup
import re
import pprint
import pandas as pd

header = headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"}

url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/manager/managerList.html#'
request = urllib.request.Request(url, headers=header)
context = ssl._create_unverified_context()
res = urllib.request.urlopen(request, context=context)
soup=BeautifulSoup(res.read(),'lxml')
tags=soup.find_all('tr')#得到标签为tr的内容（网页表格）

********************************************************************
#3.爬取静态网页通用例2（看源码筛选标签）
#直接使用urlopen（）对网页进行获取容易遭到reject。
def get_info(url) -> list:
	try:
		html = urlopen(url)
	except(HTTPError,URLError):
		return None
	try:
		paper_info = BeautifulSoup(html.read(),features = "lxml")
		tag = paper_info.find("div", {"class":"legal-person"}).findAll("td")
	except(AttributeError):
		return None
	return tag

infomation = []

def info2 (web):
	information = []
	for i in range(len(web)):
		for j in range(4):
			information.append(web[i].findAll("span")[j].get_text())
	return information

x=[]
for i in range(1,56): #循环爬取56页网页的数据
	url = str('http://www.cs.ecitic.com/newsite/cpzx/jrcpxxgs/zgcp/index_'+str(i)+'.html')
	a = get_info(url)
	x.append(info2(a))

b=[]
for i in range(55):
	for j in range(len(x[i])):
		b.append(x[i][j])

result = [b[i:i+4] for i in range(0,len(b),4)]
result = pd.DataFrame(result)

result.to_csv("zhongxinxx.csv",index = False, sep = ',', encoding = "gb18030")

********************************************************************
#4.爬取基金协会数据，数据为动态加载的json格式
#headers内容根据网页request hearder内容进行修改
#POST /amac-infodisc/api/pof/manager HTTP/1.1
from urllib.parse import urlencode
import requests
import json
import datetime
base_url =  'http://gs.amac.org.cn/amac-infodisc/api/pof/manager?'       # 请求 url 所携带参数的前面部分
fund_base_url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/manager/'   # 基金 url 前面的部分
lis_json = []       

headers = {
'Accept': 'application/json, text/javascript, */*; q=0.01',
'Content-Type': 'application/json',
'Origin': 'http://gs.amac.org.cn',
'Referer': 'http://gs.amac.org.cn/amac-infodisc/res/pof/manager/managerList.html',
'Content-Length': '2',
'Host': 'gs.amac.org.cn',
'Accept-Language': 'zh-CN,zh;q=0.9',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
'Accept-Encoding': 'gzip, deflate',
'Connection': 'keep-alive',
'X-Requested-With': 'XMLHttpRequest'
}

def get_page(page):
	params = {                                                  
		'rand': 0.3042983067077353,
		'page': 2,
		'size': 100
	}
	url = base_url + urlencode(params)
	try:
		r = requests.post(url,headers=headers,data=json.dumps({}))      # post 方法，将 Request Payload 的信息转换成 json 格式然后提交
		if r.status_code == 200:
			return r.json()
	except requests.ConnectionError as e:
		print('Error',e.args)

def parse_page(r_json):
    if r_json:
        items = r_json.get('content')
        for item in items:
            info = {}
            info['是否失信'] = item.get('inBlacklist')
            info['私募基金管理人名称'] = item.get('managerName')
            info['法定代表人'] = item.get('artificialPersonName')
            info['办公地点'] = item.get('officeAddress')
            info['基金数目'] = item.get('fundCount')
            establishDate = item.get('establishDate')
            info['成立时间'] = str(datetime.datetime.fromtimestamp(establishDate/1000).date()) if establishDate else ''       # 成立时间有可能为空，防止这种情况而报错
            registerDate = item.get('registerDate')
            info['登记时间'] = str(datetime.datetime.fromtimestamp(registerDate/1000).date()) if registerDate else ''
            info['基金链接'] = fund_base_url + item.get('url')
            yield info

def write_to_json(lis):
	with open('info.json','w',encoding='utf-8') as f:
		json.dump({'info':lis},f,ensure_ascii=False)

def main():
    for page in range(244):
        r_json = get_page(page)
        results = parse_page(r_json)
        for result in results:
            lis_json.append(result)
    write_to_json(lis_json)

if __name__ == '__main__':
    main()

#导出json
import xlwt
jsonfile3 = test
workbook = xlwt.Workbook()
sheet1 = workbook.add_sheet('test4')
ll = list(jsonfile3[0][0].keys())
for i in range(0,len(ll)):
    sheet1.write(0,i,ll[i])

for j in range(0,len(jsonfile3)):
    m = 0
    ls = list(jsonfile3[j][0].values())
    for k in ls:
        sheet1.write(j+1,m,k)
        m += 1

workbook.save('XXX.xls')

*******************************************************************
#5.使用天眼查API（需要付费）
import requests
name = [jsonfile[i]['私募基金管理人名称'] for i in range(len(jsonfile))]
test = []
url2 = [str('http://open.api.tianyancha.com/services/open/ic/baseinfoV2/2.0?name=')+i for i in aa]

i=0
for i in range(216,len(aa)):
	try:
		response = requests.get(url2[i], headers={'Authorization': 'a1f0ca96-d320-4176-8f79-6477de7ccf2f'})
		test.append([{
			'name' : response.json()['result']['name'],
			'phoneNumber' : response.json()['result']['phoneNumber'],
			'email' : response.json()['result']['email'],
			'regCapital' : response.json()['result']['regCapital'],
			'staffNumRange' : response.json()['result']['staffNumRange'],
			'percentileScore' : response.json()['result']['percentileScore'],
			'isMicroEnt' : response.json()['result']['isMicroEnt']
			}])
		print(test[i])
		i=i+1
	except(TypeError):
		pass

*************************************************************
#6.另一种爬虫方法，伪装成浏览器访问网页
#如果访问过快，部分网页会识别出来
#部分复制自CSDN网站博客
#根据情况加入time.sleep()降低访问速度防止被发现
browser = webdriver.Chrome()
#time.sleep(random()+1)
browser.get('https://www.tianyancha.com/login')
#time.sleep(random()+random.randint(2,3))
browser.find_element_by_css_selector('div.title:nth-child(2)').click()
#time.sleep(random.uniform(0.5,1))
phone = browser.find_element_by_css_selector('div.modulein:nth-child(2) > div:nth-child(2) > input:nth-child(1)')
phone.send_keys('***********your username 13660734606')
#time.sleep(random.uniform(0.4,0.9))
password = browser.find_element_by_css_selector('.input-pwd')
password.send_keys('**********your password')
click = browser.find_element_by_css_selector('div.modulein:nth-child(2) > div:nth-child(5)')
click.click()
#time.sleep(random.uniform(0.5,1)+10)

#获取页面数
try:
    pages = soup.find('ul',class_='pagination').find_all('li')[-2].getText().replace('...','')
except:
    pages = 1
finally:
    print('pages:',pages)

def getUid(soup):
    urls = []
    divs = soup.find('div',class_='result-list sv-search-container').find_all('div',class_='search-item sv-search-company')                                                                             
    for div in divs:
        urls.append(div.find('div',class_='header').find('a')['href'])
    return urls

urls = []
for i in range(1,pages+1):
	url = 'https://www.tianyancha.com/search?key=北京杰思汉能资产管理有限公司'
	browser.get(url)
	time.sleep(random.uniform(0.6,1)+2)
	soup = BeautifulSoup(browser.page_source,'lxml')
    urls.extend(getUid(soup))



searchCompanyRet=urllib.request.urlopen(testUrl).read().decode("utf-8", "ignore")	
matchPat='tyc-event-ch="CompanySearch.Company".*?href="(.*?)" target='
nextUrls =  re.compile(matchPat, re.S).findall(searchCompanyRet)
nextUrl = nextUrls[0]
print("企业详细信息可以查看下一个链接：" + str(nextUrl))



import urllib.request
import re
 
#人可以识别的路径，编码类型为utf-8，即汉语
chinaCompany="重庆长安汽车股份有限公司"
testUrl="https://www.qixin.com/search?key=" + chinaCompany + "&page=1&scope[]=1"
print("visit web:"+testUrl)
 
#转化为机器可以识别带中文的网址，编码类型为unicode。只转换汉字部分，不能全部网址进行转换
company=urllib.parse.quote(chinaCompany)
testUrl="https://www.qixin.com/search?key=" + chinaCompany + "&page=1&scope[]=1"
print("visit web:"+testUrl)
 
#浏览器伪装池，将爬虫伪装成浏览器，避免被网站屏蔽
headers=("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0")
opener = urllib.request.build_opener()
opener.addheaders = [headers]
urllib.request.install_opener(opener)
 
#爬取第一个页面，即搜索企业名字，获得访问企业信息的跳转链接
searchCompanyRet=urllib.request.urlopen(testUrl).read().decode("utf-8", "ignore")	
matchPat='tyc-event-ch="CompanySearch.Company".*?href="(.*?)" target='
nextUrls =  re.compile(matchPat, re.S).findall(searchCompanyRet)
nextUrl = nextUrls[0]
print("企业详细信息可以查看下一个链接：" + str(nextUrl))
 
#爬取第二个页面，即查看企业详细信息，获取出官网链接
companyDetail=urllib.request.urlopen(nextUrl).read().decode("utf-8", "ignore")
matchPat = 'class="company-link".*?href="(.*?)".*?rel'
companyUrl = re.compile(matchPat, re.S).findall(companyDetail)
print("企业<" +  chinaCompany + ">的官网地址：" + str(companyUrl[0]))



#爬取天眼查百度源码为例
import time
import sys
import urllib
import requests

def main():
    headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
	'Accept-Encoding': 'gzip, deflate, br',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Cookie': 'aliyungf_tc=AQAAAGSY501ZOwIA7FrmeL8SPf5CFOWM; csrfToken=lvL6-153ZI_pO053n-DfhNuT; jsid=SEM-BAIDU-PP-VIguangzhou-000873; TYCID=df7228d09d8611e9acc585b311011f1e; undefined=df7228d09d8611e9acc585b311011f1e; ssuid=2856053099; bannerFlag=undefined; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1562153822; _ga=GA1.2.250728247.1562153822; _gid=GA1.2.144050866.1562153822; token=5bac079af1eb431ea11ca25f4bd112e9; _utm=d44b7958388442bebe8b26cc6f582a40; tyc-user-info=%257B%2522claimEditPoint%2522%253A%25220%2522%252C%2522myAnswerCount%2522%253A%25220%2522%252C%2522myQuestionCount%2522%253A%25220%2522%252C%2522signUp%2522%253A%25220%2522%252C%2522explainPoint%2522%253A%25220%2522%252C%2522privateMessagePointWeb%2522%253A%25220%2522%252C%2522nickname%2522%253A%2522%25E5%2585%258B%25E9%2587%258C%25E6%2596%25AF%25E8%2592%2582%25E5%25A8%259C%25C2%25B7%25E8%2589%25BE%25E4%25BC%25AF%25E7%259B%2596%25E7%2589%25B9%2522%252C%2522integrity%2522%253A%25220%2525%2522%252C%2522privateMessagePoint%2522%253A%25220%2522%252C%2522state%2522%253A0%252C%2522announcementPoint%2522%253A%25220%2522%252C%2522isClaim%2522%253A%25220%2522%252C%2522vipManager%2522%253A%25220%2522%252C%2522discussCommendCount%2522%253A%25220%2522%252C%2522monitorUnreadCount%2522%253A%25220%2522%252C%2522onum%2522%253A%25220%2522%252C%2522claimPoint%2522%253A%25220%2522%252C%2522token%2522%253A%2522eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzY2MDczNDYwNiIsImlhdCI6MTU2MjE1MzgzOSwiZXhwIjoxNTkzNjg5ODM5fQ.g-_BTjh2qyZ0Ph7m5yKlLgvjpS5_rXJgbvpr0dKRFGRurfH6ZCc-0GqI3zwddaigrC2nEdNXrtPw_7F-gzm3BQ%2522%252C%2522pleaseAnswerCount%2522%253A%25220%2522%252C%2522redPoint%2522%253A%25220%2522%252C%2522bizCardUnread%2522%253A%25220%2522%252C%2522vnum%2522%253A%25220%2522%252C%2522mobile%2522%253A%252213660734606%2522%257D; auth_token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzY2MDczNDYwNiIsImlhdCI6MTU2MjE1MzgzOSwiZXhwIjoxNTkzNjg5ODM5fQ.g-_BTjh2qyZ0Ph7m5yKlLgvjpS5_rXJgbvpr0dKRFGRurfH6ZCc-0GqI3zwddaigrC2nEdNXrtPw_7F-gzm3BQ; RTYCID=a84aba730e4e48c1b669be039834aeae; CT_TYCID=febeb2ad1716480aa2c10fdefc877d65; cloud_token=fbb1ce3ab7e743658d4cf6ed3bb854f4; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1562155687; _gat_gtag_UA_123487620_1=1',
	'Host': 'www.tianyancha.com',
	'Referer': 'https://www.tianyancha.com/company/22822',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36ndows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
               }
 
    cookies = {'aliyungf_tc':'AQAAAInSEClDxQUAftHidO+PzCmdPZot',
               'ssuid':'3986673831',
               'bannerStorageV2':'%22false%22',
               '_pk_ref.1.e431':'%5B%22%22%2C%22%22%2C1498801845%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Do5N6sHrB-gmAwl5M4IyAj3G-5IwlRrODDLv9KztH10ivG8HhNHkgDVgRGREFnnDo%26wd%3D%26eqid%3D857f04a80002baa6000000045955e633%22%5D',
               'token':'0be5e638129c4f31b919a967874008b9',
               '_utm':'d6268574eb574651adf74cccc7544227',
               '_pk_id.1.e431':'c993f4ee7aa80f31.1498532324.2.1498803205.1498801845.' ,
               'paaptp':'ac2b22f83d9dd0dd86d47a0ed395ab25daf20e81e80534fe7315cf7a1f2fb',
               'csrfToken':'mVLfAuO0VxQSUCvQ1Iip_cGu', 
               'TYCID':'8b7b7d5061f411e7bd5589439b03dd9e',
               'uccid':'17cd6a2a4cf16ac20363e1b85bee6b90',
               'tyc-user-info':'eyJuZXciOiIxIiwidG9rZW4iOiJleUpoYkdjaU9pSklVelV4TWlKOS5leUp6ZFdJaU9pSXhNekU0TkRNNU1EazROeUlzSW1saGRDSTZNVFE1T1RNd09EazRNaXdpWlhod0lqb3hOVEUwT0RZd09UZ3lmUS5TSENlRksweGdnd09UcEtDUnlpNXVpTFg4UVBwbXZJNmFOUi1ITjhCbVltNEZaT0hTeDhENDJJQ3E0T295c1ZFSVppRHEya2ZEZElmSGpsaFF5dV9ydyIsInN0YXRlIjoiMCIsInZudW0iOiIwIiwib251bSI6IjAiLCJtb2JpbGUiOiIxMzE4NDM5MDk4NyJ9',
               'bannerFlag':'true',
               'Qs_lvt_117460':'1499308873%2C1499309809%2C1499390608',
               '_csrf':'N/4TCyFkbN17DmLl2qSx+Q==',
               'OA':'F6nGwYzI0K34U50NUXjCQ/RdisJkPVhyuvaz/ULhAdH9wGFBF+oY9SNo41xfg8ChEnKmkDW9KccidaKN4NUM7RY0fvt6ry12S005VjpHV9M=', 
               '_csrf_bk':'ababd67a90e3e88a85e813986cb58d6b', 
               'Hm_lvt_e92c8d65d92d534b0fc290df538b4758':'1498532730,1498801845,1499308866,1499309809', 
               'Hm_lpvt_e92c8d65d92d534b0fc290df538b4758':'1499400842',
               'Qs_pv_117460':'1553841720118954500%2C1189009320365233400%2C4541963271723247600%2C1868246178729382000%2C1343361850682038000'
               }
    keyword = '百度' #要搜索的公司
    startUrl = 'http://www.tianyancha.com/search?key=%s&checkFrom=searchBox' % urllib.quote(keyword)
    resultPage = requests.get(startUrl, headers= headers, cookies = cookies) #在请求中设定头，cookie
    time.sleep(10)
    print(resultPage)

if __name__ == '__main__':
    importlib.reload(sys)

**************************************************************
#7，尝试伪装浏览器爬取天眼查，每200条左右会被封IP，要进行手动验证
browser = webdriver.Chrome()
#time.sleep(random()+1)
browser.get('https://www.tianyancha.com/login')
#time.sleep(random()+random.randint(2,3))
browser.find_element_by_css_selector('div.title:nth-child(2)').click()
time.sleep(random.uniform(0.5,1))
phone = browser.find_element_by_css_selector('div.modulein:nth-child(2) > div:nth-child(2) > input:nth-child(1)')
phone.send_keys('13660734606')
#time.sleep(random.uniform(0.4,0.9))
password = browser.find_element_by_css_selector('.input-pwd')
password.send_keys('051010ckwA')
click = browser.find_element_by_css_selector('div.modulein:nth-child(2) > div:nth-child(5)')
click.click()
#time.sleep(random.uniform(0.5,1)+10)
href = []
test = []
i = 1


for urls in name:
	url = 'https://www.tianyancha.com/search?key='+str(urls)
	browser.get(url)
	time.sleep(random.uniform(0.6,1)+1)
	print("开始处理第"+str(i)+"家公司")
	i +=1
	try:
		soup = BeautifulSoup(browser.page_source,'lxml')
		href.append(getUid(soup)[0])
	except(AttributeError):
		break


i = 1


for url in href:
	browser.get(url)
	time.sleep(random.uniform(0.6,1)+1)
	soup = BeautifulSoup(browser.page_source,'lxml')
	print("开始处理第"+str(i)+"家公司")
	i +=1
	try:
		company = soup.find('div',class_='header').find('h1',class_='name').getText()
		phone = soup.find('div',class_='in-block sup-ie-company-header-child-1').find_all('span')[1].getText()
		email = soup.find('div',class_='in-block sup-ie-company-header-child-2').find_all('span')[1].getText()
		test2.append([{'name' : company,
			'phoneNumber' : phone,
			'email' : email
			}])
	except(AttributeError):
		break

