import os,json,re,imghdr,md5,random,urllib
from library import WorkerBase,iif,inc
from time import strftime,gmtime

class worker(WorkerBase):

	def run(self):
		try:
			start = self.page * int(self.config['cant_items'])
			busq = re.sub('\s+','+',self.pal_palabra)
#			pac_id = self.relacionarConPalabra(self.pal_palabra,'1')

			# BUSCO EL IDIOMA
			lang = self.getLanguage()
			url  = 'http://images.google.com/images?hl=%s&q=%s&start=%d&ndsp=21&safe=off' % (lang,busq,start)
#			print items_found
#			self.addmessage('URL Request: %s' % url)
			try:
				htmldoc = self.readPage(url)
			except IOError,e:
				self.addmessage('Googleimages error: %s(Palabra:%s)' % ( str(e),self.pal_palabra  ))
				return False
			
			htmldoc = htmldoc.decode('utf-8')
			
			path   = '%s%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):
				os.makedirs(path)

			resultado = re.findall('dyn\.setResults\(\[[\S\s]+\]\);',htmldoc)

			if len(resultado) == 0:
				self.addmessage('Googleimages no tiene resultados para la url %s(Palabra:%s)' % ( url, self.pal_palabra ) )
				return False

			for resultado in resultado:
				#Borro lo que no me sirve
				if self.items_found == int(self.config['cant_items']): return True
				resultado = re.sub('dyn\.setResults\(\[', '', resultado)
				resultado = re.sub('\]\);', '', resultado)
				coco = eval(resultado)

				for coco_array in coco:
					for imageURL in re.findall('imgurl\\x3dhttp://[a-zA-Z0-9./%_-]+',coco_array[0]):
						imageURL = re.sub('imgurl\\x3d', '', imageURL)
#						imageURL = self.normalizar(imageURL)	

					for imageHref in re.findall('imgrefurl\\x3dhttp://[a-zA-Z0-9./%_-]+',coco_array[0]):
						imageHref = re.sub('imgrefurl\\x3d', '', imageHref)
#						imageHref = self.normalizar(imageHref)	

					for imageTitle in re.findall('.+',coco_array[6]):
						imageTitle = re.sub('\\x3c[/]?b\\x3e', '', imageTitle)
						imageTitle = imageTitle.decode('utf-8')
#						imageTitle = self.normalizar(imageTitle)	

					for imageDomain in re.findall('.+',coco_array[11]):
						imageDomain = imageDomain
						
					for imageType in re.findall('.+',coco_array[10]):
						imageType = imageType

					for imageInfo in re.findall('.+',coco_array[9]):
						imageAncho = re.findall('[\d]+\sx', imageInfo)
						imageAncho = re.sub('\sx', '', imageAncho[0])
#						imageAncho = self.normalizar(imageAncho)
						imageAlto = re.findall('x\s[\d]+', imageInfo)
						imageAlto = re.sub('x\s', '', imageAlto[0])
#						imageAlto = self.normalizar(imageAlto)
						imageTamano = re.findall('-\s[\S]+', imageInfo)
						imageTamano = re.sub('-\s', '', imageTamano[0])
#						imageTamano = self.normalizar(imageTamano)
					
					# valido que la url sea un archivo de tipo imagen
					imageBIN = self.getRemoteFile(imageDomain,imageURL)
					if imageBIN is None:
#						self.addmessage('Error al leer la imagen: %s' % imageURL)
						continue
					
					imageType = imghdr.what(None,imageBIN[0:32])
					if imageType is None: imageType = 'png'
#						self.addmessage('El archivo no es una imagen: %s' % imageURL)
#						continue
					

					# valido que la imagen no se encuentre en la base de datos
					md5File  = md5.new(imageBIN).hexdigest()
					self.rows = self.seleccionar("SELECT cgi_md5_file FROM cgi_contenido_google_images WHERE cgi_md5_file = '%s'" % md5File)
					if self.cursor.rowcount > 0:
#						self.addmessage('La imagen ya se encuentra en la base de datos: %s' % imageURL)
						continue		
					
					imageName = "%s" % md5.new(md5File+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())).hexdigest()
					imagePath = path+imageName+'.'+imageType

					contenido = {
						'imagen_local'     : self.escapeString(str(imageName + '.' + imageType )),
						'imagen_original'  : self.escapeString(str(imageURL)),
						'imagen_href'      : self.escapeString(str(urllib.url2pathname(imageHref))),
						'titulo'           : self.escapeString(str(imageTitle)),
						'dominio'          : self.escapeString(str(imageDomain)),
						'tipo'             : self.escapeString(str(imageType)),
						'alto'             : self.escapeString(str(imageAlto)),
						'ancho'            : self.escapeString(str(imageAncho)),
						'tamano'           : self.escapeString(str(imageTamano))
					}
					jcontenido = json.dumps(contenido)
					jcontenido = self.escapeUnicode(jcontenido)
					try :
						data = {
							'cgi_fecha'			: "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
							'cgi_imagen_local': "'%s'" % (imageName+'.'+imageType),
							'cgi_md5_file'		: "'%s'" % md5File,
							'cgi_titulo'      : "'%s'" % contenido['titulo'],
							'cgi_metadata'		: "'%s'" % jcontenido
						}
						insert_id = self.agregarcontenido('cgi_contenido_google_images', data)
						self.saveFile(imagePath,imageBIN)
						self.items_found = inc(self.items_found)
					except Exception , e:
						print 'Googleimages error: %s' % e
						self.addmessage('Google Images error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )

			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Googleimages error %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )
			return False
