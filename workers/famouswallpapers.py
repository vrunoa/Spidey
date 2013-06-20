from library import WorkerBase,iif,inc
from time import strftime,gmtime
import imghdr, re, md5, random, json, os
from BeautifulSoup import BeautifulSoup
class worker(WorkerBase):

	def run(self):

		url = 'http://famous-wallpapers.com'

		print url

		html = self.readPage(url)
		html = re.sub('\s+',' ',html)
		html = html.decode('utf-8')
                html = self.normalizar(html)
		
                soup = BeautifulSoup(html)
                categ = soup.findAll("li", {'class':'cat-item cat-item-210'})
                print categ
                for category in categ:
                    print category

		import sys
		sys.exit(1)
