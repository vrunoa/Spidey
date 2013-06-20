# -*- coding: utf-8 -*-
import os,json,re,imghdr,md5,random,urllib
from time import strftime,gmtime
from library import WorkerBase,iif,inc
class worker(WorkerBase):

	def run(self):
		try:
			start = iif(self.page == 0, 1, int(self.page) * int(self.config['cant_items']))
			import re
			busq = re.sub('\s+','+',self.pal_palabra)

			# BUSCO EL IDIOMA
			lang = self.getLanguage()

			#PARAMETROS QUE TENGO QUE PASAR PARA HACER UNA BUSQUEDA
			url_base = 'http://gdata.youtube.com/feeds/api/videos/'
			q = busq
			url = url_base + "?start-index=%s&racy=include&orderby=viewCount&q=%s&restriction=%s&lr=%s" % (start, q, lang.upper(), lang)
			try:
				dom = self.readPage('%s' % (url))
			except IOError,e:
				self.addmessage('Youtube error %s ' % str(e) )
				return False
		
			dom = self.getSourceAsDOM(dom, False)

			results = dom.getElementsByTagName('openSearch:totalResults')[0].firstChild.nodeValue;
			if int(results) == 0:
				self.addmessage('Youtube no hay resultados para la url %s' % url )
				return False

			path   = '%s%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):
				os.makedirs(path)
			
			from datetime import datetime
			import json

			#pac_id = self.relacionarConPalabra(self.pal_palabra,'2')
			paths  = []
			
			entry = dom.getElementsByTagName('entry')
			if len(entry) == 0:
				self.addmessage('Youtube no hay resultados para la url %s' % url )
				return False

			i=1
			for node in entry:
				
				i = i + 1

				if self.items_found == int(self.config['cant_items']): return True

				now    = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")

				fecha_publicado = node.getElementsByTagName('published')[0].firstChild.nodeValue
				media = node.getElementsByTagName('media:group')[0]
				try: titulo = media.getElementsByTagName('media:title')[0].firstChild.nodeValue
				except : titulo = ''

				try: desc = media.getElementsByTagName('media:description')[0].firstChild.nodeValue
				except : desc = ''

				try: keywords = media.getElementsByTagName('media:keywords')[0].firstChild.nodeValue
				except : keywords= ''

				try: url = media.getElementsByTagName('media:player')[0].getAttribute('url')
				except : url = ''
				try: thumbnail = media.getElementsByTagName('media:thumbnail')[0].getAttribute('url')
				except : thumbnail = None
				# Comento esta linea porque me cambia todo a minuscula y la imagen se rompe
				if thumbnail is not None:
					domain    = re.sub('http://','',thumbnail)
					domain    = re.split('\/',domain)[0]
					imageBIN = self.getRemoteFile(str(domain),thumbnail)
					if imageBIN is not None:
						md5File = md5.new(imageBIN).hexdigest()
						imageType = imghdr.what(None,imageBIN[0:32])
						if imageType is None: imageType = 'png'
						imageName = "%s" % md5.new(md5File + strftime('%Y%m%d%H%M%S',gmtime())).hexdigest()
						imagePath = path+imageName+'.'+imageType

				else: thumbnail = ''

				try: thumbnail_height = media.getElementsByTagName('media:thumbnail')[0].getAttribute('height')
				except : thumbnail_height = ''
#				thumbnail_height = self.normalizar(thumbnail_height)

				try: thumbnail_width = media.getElementsByTagName('media:thumbnail')[0].getAttribute('width')
				except : thumbnail_width = ''
#				thumbnail_width = self.normalizar(thumbnail_width)
				
				try: duration = media.getElementsByTagName('yt:duration')[0].getAttribute('seconds')
				except : duration = ''
#				duration = self.normalizar(duration)

				# CHEQUEO QUE LA NOTICIA NO ESTE YA EN NUESTRA BASE DE DATOS...
				urlDB = ''
				self.rows = self.seleccionar("SELECT cyo_url FROM cyo_contenido_youtube WHERE cyo_url = '" + url + "'")
				for row in self.rows:
					urlDB = row['cyo_url']

				# ...SI ESTA, NO LO AGREGA.
				if urlDB <> url:

					embedUrl = '%s&hl=%s&fs=1&' % ( re.sub('&feature=youtube_gdata','',url), lang )
					embedUrl = re.sub('watch\?v=','v/',embedUrl)
					
					embed = '<object width=\\"425\\" height=\\"344\\"><param name=\\"movie\\" value=\\"%s\\"><\/param><param name=\\"allowFullScreen\\" value=\\"true\\"><\/param><param name=\\"allowscriptaccess\\" value=\\"always\\"><\/param><embed src=\\"%s\\" type=\\"application/x-shockwave-flash\\" allowscriptaccess=\\"always\\" allowfullscreen=\\"true\\" width=\\"425\\" height=\\"344\\"><\/embed><\/object>' %(embedUrl,embedUrl)

					# valido que la url sea un archivo de tipo imagen
					imageDomain = re.search('http://(\w|\.|\-)+',thumbnail)
					imageDomain = imageDomain.group(0)
					imageDomain = re.sub('http://','',imageDomain)
					imageBIN = self.getRemoteFile(imageDomain,thumbnail)
					if imageBIN is not None:
#						self.addmessage('Error al leer la imagen: %s' % thumbnail)
#						fails = fails + 1
#						continue

						imageType = imghdr.what(None,imageBIN[0:32])
						if imageType is None: imageType = 'png'
#						self.addmessage('El archivo no es una imagen: %s' % thumbnail)
#						fails = fails + 1
#						continue

						imageName = "%s" % md5.new(busq+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cyo_contenido_youtube").hexdigest()
						imagePath = path+imageName+'.'+imageType
						while os.path.isfile(imagePath) == True:
							imageName = "%s" % md5.new(busq+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cyo_contenido_youtube").hexdigest()
							imagePath = path+imageName+'.'+imageType


					# HAGO EL INSERT EN LA DB
					infoMeta = {
						'cyo_titulo'			: self.escapeString(titulo),
#						'cyo_embed'				: embed,
						'cyo_descripcion'		: self.escapeString(desc),
						'cyo_keywords'			: self.escapeString(keywords),
						'cyo_date'				: self.escapeString(fecha_publicado),
#						'cyo_thumbnail'			: thumbnail,
						'cyo_thumbnail_height'	: int(thumbnail_height),
						'cyo_thumbnail_width'	: int(thumbnail_width),
						'cyo_duration'			: self.escapeString(duration),
						'cyo_date'				: self.escapeString(fecha_publicado)
					}
					thumb_local = ''
					if imageBIN is not None: 
						infoMeta['cyo_thumbnail_local'] = imageName + '.' + imageType
						thumb_local = infoMeta['cyo_thumbnail_local']

					jmeta = json.dumps(infoMeta)
					jmeta = self.escapeUnicode(jmeta)
#										
#					print infoMeta['cyo_titulo']
					try:
						contenido = {
							'cyo_url'				: "'%s'" % url,
							'cyo_fecha'				: "'%s'" % fecha,
							'cyo_metadata'			: "'%s'" % jmeta,
							'cyo_titulo'         : "'%s'" % infoMeta['cyo_titulo'],
							'cyo_embed'          : "'%s'" % embed,
							'cyo_thumb'		      : "'%s'" % thumb_local
						}
						insert_id = self.agregarcontenido('cyo_contenido_youtube', contenido)
						if imageBIN is not None: self.saveFile(imagePath,imageBIN)
						self.items_found = inc(self.items_found)
					except Exception , e:
						self.addmessage('Youtube error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ))

			# Me voy!
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Youtube error %s(Palabra:%s)' % ( str(e), self.pal_palabra ))
			return False
