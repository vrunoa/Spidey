from library import WorkerBase,iif,inc
import os,md5,re,random,imghdr,json
from time import strftime,gmtime
class worker(WorkerBase):
	
	def run(self):
		
#		try:
			values,items_found = [],0		
			busq    = re.sub('\s+','+',self.pal_palabra)
			path    = '%s/%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):	os.makedirs(path)
			
			url     = 'http://www.metacafe.com/tags/%s/rss.xml'% busq
#			self.addmessage('URL Request: %s' % url)
			htmldom = self.readPage(url)
			htmldom = self.getSourceAsDOM(htmldom, False)
			
			items = htmldom.getElementsByTagName('item')
			if len(items) == 0:
				self.addmessage('Metacafe worker search(%s) has no results' % re.sub('\s+','+',self.pal_palabra))
				return False

			for item in items:
				
				if items_found == int(self.config['cant_items']): return True	
				media = {}
			
				node = item.getElementsByTagName('media:player')[0]
				media['player']  = {
					'url':self.escapeString(str(node.getAttribute('url')))
				}
				node  = item.getElementsByTagName('media:content')[0]
				media['content'] = {
					'url'      : self.escapeString(str(node.getAttribute('url'))),
					'type'     : self.escapeString(str(node.getAttribute('type'))),
					'medium'   : self.escapeString(str(node.getAttribute('medium'))),
					'height'   : self.escapeString(str(node.getAttribute('height'))),
					'width'    : self.escapeString(str(node.getAttribute('width'))),
					'duration' : self.escapeString(str(node.getAttribute('duration'))),
				}
				# valido que el swf no se encuentre en base
				sql = "SELECT * FROM cme_contenido_metacafe WHERE cme_url = '%s'" % media['content']['url']
				if len(self.seleccionar(sql)) > 0:
#					self.addmessage('El canal ya se encuentra en la base de datos: %s' %  media['content']['url'])
					continue
			
				node  = item.getElementsByTagName('media:thumbnail')[0]
				media['thumbnail']  = {
					'url':self.escapeString(str(node.getAttribute('url')))
				}
				
				domain = re.search('http://(\w|\.|\-)+',media['thumbnail']['url'])
				domain = domain.group(0)
				domain = re.sub('http://','',domain)
				imageBIN = self.getRemoteFile(str(domain),media['thumbnail']['url'])
#				if imageBIN is not None:
#					self.addmessage('No se pudo descargar la imagen(thumb): %s' % src)
#					continue

#				imageType = imghdr.what(None,imageBIN[0:32])
#				if imageType is None:
#					self.addmessage('El thumbnail no es una imagen: %s' % src)
#					imageBIN = None					

				if imageBIN is not None:
					imageType = imghdr.what(None,imageBIN[0:32])
					if imageType is None: imageType = 'png'
					imageName = "%s" % md5.new(busq+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cme_contenido_metacafe").hexdigest()
					imagePath = path+imageName+'.'+imageType
					while os.path.isfile(imagePath) == True:
						imageName = "%s" % md5.new(busq+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cme_contenido_metacafe").hexdigest()
						imagePath = path+imageName+'.'+imageType

				node  = item.getElementsByTagName('media:title')[0]
				media['title'] = self.escapeString(str(node.firstChild.nodeValue))
			
				node  = item.getElementsByTagName('media:keywords')[0]
				if node.firstChild is not None: media['keywords'] = self.escapeString(str(node.firstChild.nodeValue.encode('utf-8')))

				node    = item.getElementsByTagName('media:description')[0]
				descrip = node.firstChild.nodeValue
#				descrip = descrip.encode('utf-8')
#				descrip = descrip.decode('utf-8')
#				descrip = self.normalizar(descrip)
				descrip = re.sub('="','=\\"',descrip)
				descrip = re.sub('\n',' ',descrip)
				descrip = self.escapeString(str(descrip))
	
				media['description'] = descrip
				node  = item.getElementsByTagName('media:credit')[0]
				media['credit'] = self.escapeString(str(node.firstChild.nodeValue))

				node  = item.getElementsByTagName('media:rating')[0]
				media['rating'] = self.escapeString(str(node.firstChild.nodeValue))
				
				"""				
				descrip = ''
				for node in item.getElementsByTagName('description')[0].childNodes:
#        	   CDATA_SECTION_NODE int id = 4				
					if node.nodeType==4:
						descrip = descrip + node.nodeValue
				descrip = re.sub("'+",'"',descrip)
				descrip = self.normalizar(descrip)
				descrip = re.sub('(\n|\t|\r)','',descrip)
				descrip = re.sub('"','\\"',descrip)
				descrip = re.sub('\/>','\\/>',descrip)
				list = []
				for f in re.finditer('\/\w+>',descrip):
					if f.group(0) not in list:
						list.append(f.group(0))
				if len(list) > 0:
					for f in list:
						descrip = re.sub(f,'\\%s'% f,descrip)
				"""

				embed = '<object classid=\\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\\" codebase=\\"http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,29,0\\" width=\\"425\\" height=\\"360\\"><param name=\\"movie\\" value=\\"%s\\" \/><param name=\\"quality\\" value=\\"high\\" \/><embed src=\\"%s\\" quality=\\"high\\" pluginspage=\\"http://www.macromedia.com/go/getflashplayer\\" type=\\"application/x-shockwave-flash\\" width=\\"425\\" height=\\"360\\"><\/embed><\/object>' % ( media['content']['url'], media['content']['url'] ) 
 
				info = {
					'embed'       : embed,
					'media'       : media,
					'author'      : self.escapeString(str(item.getElementsByTagName('author')[0].firstChild.nodeValue)),
					'title'       : self.escapeString(str(item.getElementsByTagName('title')[0].firstChild.nodeValue)),
					'link'        : self.escapeString(str(item.getElementsByTagName('link')[0].firstChild.nodeValue)),
					'category'    : self.escapeString(str(item.getElementsByTagName('category')[0].firstChild.nodeValue)),
					'pubDate'     : self.escapeString(str(item.getElementsByTagName('pubDate')[0].firstChild.nodeValue)),
				}
				meta = json.dumps(info)
				meta = self.escapeUnicode(meta)
				try :
					data = {
						'cme_fecha'       : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()), 
						'cme_titulo'      : "'%s'" % info['title'],
						'cme_url'         : "'%s'" % info['link'],
						'cme_metadata'    : "'%s'" % meta,
						'cme_embed'       : "'%s'" % embed,
						'cme_thumb'       : "'%s'" % (imageName+'.'+imageType)
					}
					if imageBIN is not None: data['cme_thumb'] = "'%s'" % (imageName+'.'+imageType)
					insert_id = self.agregarcontenido('cme_contenido_metacafe', data)
					if imageBIN is not None: self.saveFile(imagePath,imageBIN)
					items_found = items_found + 1
				except Exception, e:
					self.addmessage('Metacafe error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
				
				# el rss de metacafe devuelve como maximo 20 resultados
				# si la cantidad solicitada es menor, termino el plugin
			return True

#		except Exception, e:
#			self.addmessage('Metacafe error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )		
#			return False
