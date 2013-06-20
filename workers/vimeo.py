# -*- coding: utf-8 -*-
from library import WorkerBase,iif,inc
from time import strftime,gmtime
class worker(WorkerBase):

	def run(self):
		try:

			self.page = iif( self.page == 0, 1, self.page)
			
			import re
			busq = re.sub('\s+','+',self.pal_palabra)

			# BUSCO EL IDIOMA
			lang = self.getLanguage()

			import md5

			#PARAMETROS QUE TENGO QUE PASAR PARA HACER UNA BUSQUEDA (ME DEVUELVE SOLO LOS IDs DE LOS VIDEOS)
			url_base = 'http://vimeo.com/api/rest'
			secret = self.config['secret']
			api_key = self.config['api_key']
			method = self.config['method']
			query = self.pal_palabra
			format = self.config['format']
			cadena_signature = "%sapi_key%sformat%smethod%snojsoncallbacktruepage%squery%s" % (secret,api_key,format,method,self.page,query)
			signature = "%s" % md5.new(cadena_signature).hexdigest()
			url = url_base + "?api_key=%s&format=%s&method=%s&nojsoncallback=true&page=%s&query=%s&api_sig=%s" % (api_key,format,method,self.page,busq,signature)

			# Hay algunas palabras como "radio" que devuelven una pagina en blanco y por ende sale por esta excepcion.
			try:
				htmldoc = self.readPage('%s' % (url))
			except IOError,e:
				self.addmessage('Vimeo error %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
				return False

			from datetime import datetime
			import json,os
			path   = '%s%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):
				os.makedirs(path)

			contenido = json.loads(htmldoc)
			try: lista = contenido['videos']['video']
			except:
				self.addmessage('Vimeo no hay resultados para la url %s' % url  )
				return False

			import sys
			print sys.getdefaultencoding()
		#pac_id = self.relacionarConPalabra(self.pal_palabra,'2')
			
			for pepe in lista:

				if self.items_found == int(self.config['cant_items']): return True
				now    = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")

				#A esto lo pongo asi porque cuando viene solo 1 registro en json, el FOR lo hace mal.
				try: id = pepe['id']
				except: id = lista['id']

#				print id

				#BUSCO LA INFO DE LOS VIDEOS SEGUN LOS IDs DE LA BUSQUEDA
				method = 'vimeo.videos.getInfo'
				cadena_signature = "%sapi_key%sformat%smethod%snojsoncallbacktruevideo_id%s" % (secret,api_key,format,method,id)
				signature = "%s" % md5.new(cadena_signature).hexdigest()
				url = url_base + "?api_key=%s&format=%s&method=%s&nojsoncallback=true&video_id=%s&api_sig=%s" % (api_key,format,method,id,signature)

				try:
					htmldoc = self.readPage('%s' % (url))
				except IOError,e:
					self.addmessage('Vimeo error %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
					return False

				
				infoVideo = json.loads(htmldoc)
				if infoVideo['stat']=='ok':
					desc = self.escapeString(str(infoVideo['video']['caption']))
					titulo = self.escapeString(str(infoVideo['video']['title']))
					upload_date = infoVideo['video']['upload_date']
					width = infoVideo['video']['width']
					height = infoVideo['video']['height']
					duration = infoVideo['video']['duration']
					link = 'http://vimeo.com/%s' % (id)
					thumb = infoVideo['video']['thumbnails']['thumbnail'][0]['_content']
	
					embeded = '<object width=\\"425\\" height=\\"360\\"><param name=\\"allowfullscreen\\" value=\\"true\\" \/><param name=\\"allowscriptaccess\\" value=\\"always\\" /><param name=\\"movie\\" value=\\"http://vimeo.com/moogaloop.swf?clip_id=%s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1\\" \/><embed src=\\"http://vimeo.com/moogaloop.swf?clip_id=%s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1\\" type=\\"application/x-shockwave-flash\\" allowfullscreen=\\"true\\" allowscriptaccess=\\"always\\" width=\\"425\\" height=\\"360\\"><\/embed></object>' % (id,id)

					sql = "SELECT cvi_id FROM cvi_contenido_vimeo WHERE cvi_url = '%s'" % link

					# CHEQUEO QUE LA NOTICIA NO ESTE YA EN NUESTRA BASE DE DATOS...
					idDB = ''
					rows = self.seleccionar(sql)
					if len(rows) > 0:
#					print 'El video ya se encuentra en la base de datos: %s' % a_href
						continue
					"""
					self.rows = self.seleccionar("SELECT cvi_id FROM cvi_contenido_vimeo WHERE  cvi_embed = '" + id + "'")
					for row in self.rows:
						idDB = row['cvi_video_id']

					# ...SI ESTA, NO LO AGREGA.
#					print "%s = %s ?" % (idDB,id)
					if str(idDB) <> str(id):
					"""
					domain    = re.sub('http://','',thumb)
					domain    = re.split('\/',domain)[0]

					imageBIN = self.getRemoteFile(str(domain),thumb)
					if imageBIN is not None:
						md5File = md5.new(imageBIN).hexdigest()
						import imghdr
						imageType = imghdr.what(None,imageBIN[0:32])
						if imageType is None: imageType = 'png'
						imageName = "%s" % md5.new(md5File + strftime('%Y%m%d%H%M%S',gmtime())).hexdigest()
						imagePath = path+imageName+'.'+imageType
						thumb = imageName + '.' + imageType

						# HAGO EL INSERT EN LA DB
					infoMeta = {
						'cvi_embeded'		: "%s" % embeded,
						'cvi_titulo'		: "%s" % self.escapeString(titulo),
						'cvi_link'			: "%s" % self.escapeString(link),
						'cvi_descripcion'	: "%s" % self.escapeString(desc),
						'cvi_upload_date'	: "%s" % self.escapeString(upload_date),
						'cvi_width'			: "%d" % int(width),
						'cvi_height'		: "%d" % int(height),
						'cvi_duration'		: "%s" % self.escapeString(duration),
						'cvi_thumb'			: "%s" % self.escapeString(thumb)
					}
#					print titulo
#					Retocar plugin para q se decargue el thumb					
					try:
						contenido = {
							'cvi_titulo'		: "'%s'" % titulo,
							'cvi_fecha'			: "'%s'" % fecha,
							'cvi_url'         : "'%s'" % link,
							'cvi_embed'       : "'%s'" % embeded,
							'cvi_thumb'       : "'%s'" % thumb,
							'cvi_metadata'		: "'%s'" % json.dumps(infoMeta)
						}
						insert_id = self.agregarcontenido('cvi_contenido_vimeo', contenido)
						if imageBIN is not None: self.saveFile(imagePath,imageBIN)
						self.items_found = inc(self.items_found)
					except Exception , e:
						self.addmessage('Vimeo error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )
			# Me voy!
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Vimeo error %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
			return False

