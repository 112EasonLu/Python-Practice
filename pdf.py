"""
功能：下載指定url內的所有的pdf
語法：將含有pdf的url放到指令碼後面執行就可以了
"""
from bs4 import BeautifulSoup as Soup
import requests
from sys import argv
try:
##用於獲取命令列引數，argv[0]是指令碼的名稱
root_url = 'http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/2018Spring.7z'
except:
print("please input url behind the script!!")
exit()
##獲得含有所有a標籤的一個列表
def getTagA(root_url):
	res = requests.get(root_url)
	soup = Soup(res.text,'html.parser')
	temp = soup.find_all("a")
	return temp
##從所有a標籤中找到含有pdf的，然後下載
def downPdf(root_url,list_a):
	number = 0
##如果網站url是以類似xx/index.php格式結尾，那麼只取最後一個/之前的部分
	if not root_url.endswith("/"):     
		index = root_url.rfind("/")
		root_url = root_url[:index 1]
	for name in list_a:
		name02 = name.get("href")
##篩選出以.pdf結尾的a標籤
	if name02.lower().endswith(".7z"):
		pdf_name = name.string 
		number  = 1
	print("Download the %d 7z immdiately!!!"%number,end='  ')
	print(pdf_name 'downing.....') 
##因為要下載的是二進位制流檔案，將strem引數置為True     
	response = requests.get(root_url pdf_name,stream="TRUE")
	with open(pdf_name,'wb') as file:
	for data in response.iter_content():
		file.write(data)

if __name__ == "__main__":
downPdf(root_url,getTagA(root_url))