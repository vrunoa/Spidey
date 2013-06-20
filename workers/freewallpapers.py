from library import WorkerBase,iif,inc
from time import strftime,gmtime
import imghdr, re, md5, random, json, os
class worker(WorkerBase):

	def getXMLWalls(self, page):
		
#		url = "http://www.freewallpapers.cc/spider.xml?page=%d" % page
		url = "http://www.windows7-ultimate.com/spider.xml?page=%d" % page
		xml = self.readPage(url)
		try   : xml = self.getSourceAsDOM(xml, False)
		except: xml =  None
		return xml	

	def run(self):
		
		try:
			path  = '%s/%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):	os.makedirs(path)
		
			page = 1
			xml = self.getXMLWalls(page)
			while xml is not None:
#				print page
				for wallpaper in xml.getElementsByTagName('url'):		
					wall = wallpaper.getElementsByTagName('wall')[0].firstChild.nodeValue
					loc  = wallpaper.getElementsByTagName('loc')[0].firstChild.nodeValue
					try   : cat = wallpaper.getElementsByTagName('category')[0].firstChild.nodeValue
					except: cat = ''
					name = wallpaper.getElementsByTagName('name')[0].firstChild.nodeValue
				
					if re.search(self.pal_palabra, name) is None and re.search(self.pal_palabra, cat) is None:
						continue
			
					# visito la pagina para generar el thumb
					self.readPage(wall)	

					meta = {
						'name'     : "%s" % self.escapeString(str(name)),
						'category' : "%s" % self.escapeString(str(cat)),
						'url'      : "%s" % self.escapeString(str(wall)),
						'url_image': "%s" % self.escapeString(str(loc))
					}

					domain = re.search('http://(\w|\.|\-)+', loc)
					domain = domain.group(0)
					domain = re.sub('http://','',domain)
					imageBIN = self.getRemoteFile( str(domain), loc)
					if imageBIN is None:
						continue

					imageType = imghdr.what(None, imageBIN[0:32])
					imageType = iif( imageType is None, 'png', imageType)

					md5File = md5.new(imageBIN).hexdigest()
					self.rows = self.seleccionar("SELECT cfw_id FROM cfw_contenido_freewallpapers WHERE cfw_md5_file = '%s'" % md5File)
					if len(self.rows) > 0:
#					self.addmessage('La imagen ya se encuentra en la base de datos: %s' % src)
						continue
	
					imageName = "%s" % md5.new(self.pal_palabra+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cfw_contenido_freewallapers").hexdigest()
					imagePath = path+imageName+'.'+imageType
					while os.path.isfile(imagePath) == True:
						imageName = "%s" % md5.new(self.pal_palabra+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cfw_contenido_freewallpapers").hexdigest()
						imagePath = path+imageName+'.'+imageType
		
					try :
						data = {
							'cfw_fecha'        : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
							'cfw_md5_file'     : "'%s'" % md5File,
							'cfw_titulo'       : "'%s'" % name,
							'cfw_imagen_local' : "'%s'" % self.escapeString(str(imageName+'.'+imageType)),
							'cfw_metadata'     : "'%s'" % json.dumps(meta)
						}	
						insert_id = self.agregarcontenido('cfw_contenido_freewallpapers', data)
#						print insert_id
						self.saveFile(imagePath,imageBIN)
						self.items_found = inc(self.items_found)
					except Exception , e:
						print e
						self.addmessage('Freewallpapers error: %s(Palabra:%s)' % ( str(e), self.pal_palabra) )

				if self.items_found == int(self.config['cant_items']):
					xml = None
				else:
					page = inc(page)
					xml = self.getXMLWalls(page)

#			print self.items_found
			return True

		except Exception, e:
			self.addmessage('Freewallpapers error: %s(Palabra:%s)' %  (str(e), self.pal_palabra))
