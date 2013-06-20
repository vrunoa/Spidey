import re,os,md5,json,random,imghdr,library
from library import WorkerBase,iif,inc
from BeautifulSoup import BeautifulSoup
from time import strftime,gmtime
class worker(WorkerBase):

	def run(self):
		try:
			self.page = iif(self.page == 0, 1, self.page)				
				
			busq = re.sub('\s+','+',self.pal_palabra)
			url  = 'http://searchservice.myspace.com/index.cfm?fuseaction=sitesearch.results&type=MySpaceTV&qry=%s&pg=%d' % (busq,self.page)
			print url
#			self.addmessage('URL Request: %s' % url)
			html = self.readPage(url)
			html = re.sub('\s+',' ',html)
#			html = self.normalizar(html)

			soup = BeautifulSoup(html)
			videos = soup.findAll("div",{'class':'videoYDiv clearfix'})
			print len(videos)
			if len(videos)==0:
				self.addmessage('Myspace: no hay resultados para la url %s(Palabra:%s)' % ( url, self.pal_palabra) )
				return False
			
			path  = '%s/%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):	os.makedirs(path)

			for video in videos:
				if self.items_found == int(self.config['cant_items']): return True

				thumb  = video.findAll("div",{'class':'videoThumb'})[0]
				a_href = re.sub('&amp;','&',str(thumb.findAll('a')[0]))
				a_href = re.search('http://(\w|\-|\/|\.|\?|\&|\=)+',a_href).group(0)
				a_href = re.sub('&searchid=[a-zA-Z0-9\-]+','',a_href)
				sql = "SELECT cmy_id FROM cmy_contenido_myspace WHERE cmy_url = '%s'" % a_href
				rows = self.seleccionar(sql)
				if len(rows) > 0:
#					print 'El video ya se encuentra en la base de datos: %s' % a_href
					continue
				thumb_src = re.sub('&amp;','&',str(thumb.findAll('img')[0]))
				thumb_src = re.search('http://(\w|\-|\/|\.|\?|\&|\=)+',thumb_src).group(0)
	
				videoid   = re.search('videoid=[0-9]+',a_href).group(0)
				videoid   = int(re.sub('videoid=','',videoid))

				embed = '<object width=\\"250px\\" height=\\"250px\\"><param name=\\"allowFullScreen\\" value=\\"true\\" \\/><param name=\\"wmode\\" value=\\"transparent\\" \\/><param name=\\"movie\\" value=\\"http://mediaservices.myspace.com/services/media/embed.aspx/m=%d,t=1,mt=video\\" \\/><embed src=\\"http://mediaservices.myspace.com/services/media/embed.aspx/m=%d,t=1,mt=video\\" width=\\"425\\" height=\\"360\\" allowFullScreen=\\"true\\" type=\\"application/x-shockwave-flash\\" wmode=\\"transparent\\"><\\/embed><\\/object>' % (videoid,videoid)

				domain    = re.sub('http://','',thumb_src)
				domain    = re.split('\/',domain)[0]
				imageBIN = self.getRemoteFile(str(domain),thumb_src)
				imageName = ''
				if imageBIN is not None:
					imageType = imghdr.what(None,imageBIN[0:32])
					if imageType is None: imageType = 'png'
#						self.addmessage('El thumbnail del video no es una imagen: %s' % thumb_src)
#						imageBIN = False
#					else:
					md5File = md5.new(imageBIN).hexdigest()
					imageName = "%s" % md5.new(self.pal_palabra+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cmy_contenido_myspace").hexdigest()
					imagePath = path+imageName+'.'+imageType
					while os.path.isfile(imagePath) == True:
						imageName = "%s" % md5.new(self.pal_palabra+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cmy_contenido_myspace").hexdigest()
						imagePath = path+imageName+'.'+imageType
				
				info  = video.findAll('div',{'class':'videoCenterDiv'})[0]
				title = ''	
				try:
					title_node = info.findAll('div',{'id':'videoTitle'})[0].findAll('a')[0].contents
					for item in title_node:
						item = re.sub('(<b>|</b>)+','',str(item))
						item = self.escapeHTML(item)
						title = title + self.escapeString(str(item))
				except:
					pass
				
				author = ''
				try:
					author_node = info.findAll('div',{'id':'videoAuthorContainer'})[0].findAll('a')[0].contents
					for item in author_node:
						item = re.sub('(<b>|</b>)+','',str(item))
						item = self.escapeHTML(item)
						author = author + self.escapeString(str(item))
				except:
					pass

				desc = ''
				try:
					desc_node = info.findAll('div',{'id':'videoDesc'})[0].contents
					for item in desc_node:
						item = re.sub('(<b>|</b>)+','',str(item))
						item = self.escapeHTML(item)
						desc = desc + self.escapeString(str(item))
				except:
					pass
				
				categ = ''
				try:
					categ_node = info.findAll('div',{'id':'videoCategories'})[0].findAll('a')[0].contents
					for item in categ_node:
						item = re.sub('(<b>|</b>)+','',str(item))
						item = self.escapeHTML(item)
						categ = categ + self.escapeString(str(item))
				except:
					pass
				
				tags, i = [],0
				try:
 					for tag in info.findAll('div',{'id':'videoTags'})[0].findAll('a'):
						try    :	tag = tag.findAll('b')[0].contents[0]
						except : tag = tag.contents[0]
#						tag = self.normalizar(tag)
#						tag = tag.encode('utf-8')
						tag = self.escapeString(str(tag))
						tags.append(tag)
				except: pass
				tags = iif( len(tags)>0, ','.join(tags), '')
				
				data = video.findAll('div',{'class':'videoRightDiv'})[0]
				info,i = {},0
				for li in data.findAll('li'):
					if(i==0)   : info['duration'] = str(li.contents[2])
					elif(i==1) : info['rate']     = str(li.contents[2])
					elif(i==2) : info['views']    = str(li.contents[2])
					i = i + 1

				info['desc']   = desc
				info['categ']  = categ
				info['author'] = author

				meta = {
					'video_url' : a_href,
					'titulo'    : title,
					'embed'     : embed,
					'tags'      : tags,
					'info'      : info
				}
				meta['image_url'] = ''
				if imageBIN is not None: 
					meta['image_url'] = imageName + '.' + imageType
				else:
					meta['image_url'] = ''

				jmeta = json.dumps(meta)
				jmeta = self.escapeUnicode(jmeta)

				try :
					data = {
						'cmy_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cmy_url'      : "'%s'" % meta['video_url'],
						'cmy_titulo'   : "'%s'" % title,
						'cmy_embed'    : "'%s'" % embed,
						'cmy_metadata' : "'%s'" % jmeta,
						'cmy_thumb'    : "'%s'" % meta['image_url']
					}
					insert_id = self.agregarcontenido('cmy_contenido_myspace', data)
					if imageBIN is not None: self.saveFile(imagePath,imageBIN)
					self.items_found = inc(self.items_found)
				except Exception , e:
					self.addmessage('Myspace error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )

			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Myspace error: %s(Palabra:%s)' %  (str(e), self.pal_palabra))
			return False
	
