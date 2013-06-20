import os,md5,re,random,imghdr,json
from library import WorkerBase,iif,inc
from time import strftime,gmtime
class worker(WorkerBase):

	def run(self):
		try:
			busq  = re.sub('\s+','+',self.pal_palabra)
			path  = '%s/%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):	os.makedirs(path)

			start = iif(self.page == 0, 1, self.page*20)
			url = 'http://picasaweb.google.com/data/feed/api/all?q=%s&start-index=%d&max-results=20' % (busq,start)
#			self.addmessage('URL Request: %s' % url)
			dom = self.readPage(url)
			dom = self.getSourceAsDOM(dom, False)
			results = dom.getElementsByTagName('openSearch:totalResults')[0].firstChild.nodeValue;			
			if int(results) == 0:
				self.addmessage('Picasa no hay resultados para la url %s(Palabra:%s)' % ( url, self.pal_palabra) )
				return False

			nodes = dom.getElementsByTagName('entry')
			if len(nodes) == 0:
				self.addmessage('Picasa no hay resultados para la url %s(Palabra:%s)' % ( url, self.pal_palabra))
				return False

			for node in	nodes:		

				if self.items_found == int(self.config['cant_items']): return True

				content = node.getElementsByTagName('content')[0]
				src    = str(content.getAttribute('src'))
				domain = re.search('http://(\w|\.|\-)+',src)
				domain = domain.group(0)
				domain = re.sub('http://','',domain)
				imageBIN = self.getRemoteFile(str(domain),src)
				if imageBIN is None:
#					self.addmessage('Error al leer la imagen: %s' % src)
					continue

				imageType = imghdr.what(None,imageBIN[0:32])
				if imageType is None: imageType = 'png'
#					self.addmessage('El archivo no es una imagen: %s' % src)

				md5File = md5.new(imageBIN).hexdigest()
				self.rows = self.seleccionar("SELECT cpi_id FROM cpi_contenido_picasa WHERE cpi_md5_file = '%s'" % md5File)
				if len(self.rows):
#					self.addmessage('La imagen ya se encuentra en la base de datos: %s' % src)
					continue		
				
				imageName = "%s" % md5.new(busq+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cpi_contenido_picasa").hexdigest()
				imagePath = path+imageName+'.'+imageType
				while os.path.isfile(imagePath) == True:
					imageName = "%s" % md5.new(busq+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cpi_contenido_picasa").hexdigest()
					imagePath = path+imageName+'.'+imageType
			
							
				authorNode = node.getElementsByTagName('author')[0]
				author = {
					'name'  : self.escapeString(str(authorNode.getElementsByTagName('name')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'uri'   : self.escapeString(str(authorNode.getElementsByTagName('uri')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'email' : self.escapeString(str(authorNode.getElementsByTagName('email')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'thumbnail' : self.escapeString(str(authorNode.getElementsByTagName('gphoto:thumbnail')[0].firstChild.nodeValue.encode('utf-8','ignore')))
				}
				try    :	summary = self.escapeString(str(node.getElementsByTagName('summary')[0].firstChild.nodeValue.encode('utf-8','ignore')))
				except : summary = ''

				try    : geopos =  self.escapeString(str(node.getElementsByTagName('gml:pos')[0].firstChild.nodeValue.encode('utf-8','ignore')))
				except : geopos = '0 0'

				try    :	location = self.escapeString(str(node.getElementsByTagName('gphoto:location')[0].firstChild.nodeValue.encode('utf-8','ignore')))
				except :	location = ''

				contenido = {
					'author'      : author,
					'image_url'   : self.escapeString(str(src)),
					'titulo'      : self.escapeString(str(node.getElementsByTagName('title')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'published'   : self.escapeString(str(node.getElementsByTagName('published')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'summary'     : summary,
				   'access'      : self.escapeString(str(node.getElementsByTagName('gphoto:access')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'width'       : self.escapeString(str(node.getElementsByTagName('gphoto:width')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'height'      : self.escapeString(str(node.getElementsByTagName('gphoto:height')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'size'        : self.escapeString(str(node.getElementsByTagName('gphoto:size')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'geopos'      : geopos,
					'album_title' : self.escapeString(str(node.getElementsByTagName('gphoto:albumtitle')[0].firstChild.nodeValue.encode('utf-8','ignore'))),
					'location'    : location,
					'imagen_local': imageName + '.' + imageType
				}
				jcontenido = json.dumps(contenido)
				jcontenido = self.escapeUnicode(jcontenido)
				try :
					data = {
						'cpi_fecha'        : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cpi_md5_file'     : "'%s'" % md5File,
						'cpi_titulo'       : "'%s'" % contenido['titulo'],
						'cpi_imagen_local' : "'%s'" % self.escapeString(str(imageName+'.'+imageType)),
						'cpi_metadata'     : "'%s'" % jcontenido
					}	
					insert_id = self.agregarcontenido('cpi_contenido_picasa', data)
					self.saveFile(imagePath,imageBIN)
					self.items_found = inc(self.items_found)
				except Exception , e:
					self.addmessage('Picasa error: %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
		
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Picasa error %s(Palabra:%s) ' % ( str(e),self.pal_palabra ) )
			return False
