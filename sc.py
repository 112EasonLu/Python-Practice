
from urllib.request import urlopen
from urllib.request import urlretrieve


downloadurl = urlopen('http://www.lib.nsysu.edu.tw/exam/master/liter/eng/eng_105.pdf')
zipcontent= downloadurl.read()
with open('tttttt.pdf', 'wb') as f:
    f.write(zipcontent)

