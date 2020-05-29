from minerva_common import *
from bs4 import BeautifulSoup
import re

def download_stuff(txt,code):
	p = re.compile(r'd2l_content_\_(\d*)')
	doc_ids = re.findall(r"d2l_content_"+code+r"\_(\d*)",txt)
	soup = BeautifulSoup(txt, 'html.parser')
	for link in soup.find_all('a'):
		if (link.get('class')[0] == 'd2l-link' and len(link.get('class')) ==1):
			ttl = link.get('title')
			if ttl:
				ids = link.get('id')
				idi = ids.split("_")
				cid = idi[2]
				did = idi[3]
				url = f"d2l/le/content/{cid}/topics/files/download/{did}/DirectFileTopicDownload"
				fname = "".join(x for x in ttl if x.isalnum() or x == " ")
				r = minerva_get(url, base_url=shib_credentials.lms_url)
				open(fname +".pdf", 'wb').write(r.content)
	return url


