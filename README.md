## scratching-website
Aiming to summarize some useful techniques in scratching some useful data. By using several cases to help you better grasp the scratching skills. The data on some websites is stactic while the other may be dynamic loading through javascript. Acquiring static data is much simpler cause you only need to copy their label from the websites' source code, while having access to the dynamic data will be kind of tricky. Hope this article could help you have a better command in scratching!


### case1 Static.[CITIC SECURITY PRODUCTS](http://www.cs.ecitic.com/newsite/cpzx/jrcpxxgs/zgcp/index.html)
```
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
for i in range(1,56): #scratch 56 pages information in loop
	url = str('http://www.cs.ecitic.com/newsite/cpzx/jrcpxxgs/zgcp/index_'+str(i)+'.html')
	a = get_info(url)
	x.append(info2(a))

b=[]
for i in range(55):
	for j in range(len(x[i])):
		b.append(x[i][j])

result = [b[i:i+4] for i in range(0,len(b),4)]
result = pd.DataFrame(result)

result.to_csv("citic.csv",index = False, sep = ',', encoding = "gb18030")
```
### case2 Dynamic.[Asset Management Association of China](http://gs.amac.org.cn/amac-infodisc/res/pof/manager/managerList.html)
```
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
```
### case3 Use API [Interface](https://open.tianyancha.com)
```
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
```
