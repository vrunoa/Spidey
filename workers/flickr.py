# -*- coding: utf-8 -*-
from library import WorkerBase,iif,inc
from time import strftime,gmtime
import os,random,imghdr
class worker(WorkerBase):

	def run(self):
		try:
			perpage = int(self.config['cant_items'])

			self.page = iif(self.page == 0, 1, self.page)
			import re
			busq = re.sub('\s+','+',self.pal_palabra)
			tags = re.sub('\s+',',',self.pal_palabra)

			fails = 0
			imageType = 'jpg'
			paths  = []

			# BUSCO EL IDIOMA
			lang = self.getLanguage()

			import md5 

			#PARAMETROS QUE TENGO QUE PASAR PARA HACER UNA BUSQUEDA (ME DEVUELVE SOLO LOS IDs DE LOS VIDEOS)
			url_base = 'http://www.flickr.com/services/rest/'
			api_key = self.config['api_key']
			method = self.config['method']
			query = busq
			format = self.config['format']
			url = url_base + "?api_key=%s&format=%s&method=%s&nojsoncallback=1&per_page=%s&page=%s&text=%s&tags=%s&has_geo=1" % (api_key,format,method,perpage,self.page,query,tags)
			try:
				htmldoc = self.readPage('%s' % (url))
			except IOError,e:
				self.addmessage('Flickr error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
				return False
			from datetime import datetime
			import json
			
			contenido = json.loads(htmldoc)
	
			if self.page > int(contenido['photos']['pages']):
				self.addmessage('No hay mas resultados para la url %s(Palabra:%s)' % ( url,self.pal_palabra ) )
				return False
			
			stat = contenido['stat']
			if stat != 'ok':
				self.addmessage('No hay resultados para la url %s(Palabra:%s)' % ( url,self.pal_palabra ) )
				return False

			lista = contenido['photos']['photo']

			if len(lista) == 0:
				self.addmessage('No hay resultados para la url %s(Palabra:%s)' % ( url, self.pal_palabra ) )
				return False
			
			#pac_id = self.relacionarConPalabra(self.pal_palabra,'2')
			#pac_id = 0

			for pepe in lista:
				
				if self.items_found == int(self.config['cant_items']): return True
				yaExiste = 0
				
				now    = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")

				id = pepe['id']

				#BUSCO LA INFO DE LAS FOTOS SEGUN LOS IDs DE LA BUSQUEDA
				method = 'flickr.photos.getInfo'
				url = url_base + "?api_key=%s&format=%s&method=%s&nojsoncallback=1&photo_id=%s" % (api_key,format,method,id)

				try:
					htmldoc = self.readPage('%s' % (url))
				except IOError,e:
					self.addmessage('Flickr error: %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
					return False

				infoFoto = json.loads(htmldoc)
				#print infoFoto['photo']['id']
				if infoFoto['photo']['id'] != '':
					id = infoFoto['photo']['id']
					server = infoFoto['photo']['server']
					secret = infoFoto['photo']['secret']
					imagen = 'http://farm4.static.flickr.com/%s/%s_%s.jpg' % (server,id,secret)
			
					titulo = infoFoto['photo']['title']['_content']
					descripcion = infoFoto['photo']['description']['_content']
					link = infoFoto['photo']['urls']['url'][0]['_content']
					taken = infoFoto['photo']['dates']['taken']

					path   = '%s%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
					if not os.path.exists(path):
						os.makedirs(path)

					# valido que la url sea un archivo de tipo imagen
					farm = infoFoto['photo']['farm']
					imageDomain = 'farm%s.static.flickr.com' % (farm)
					imageURL = 'http://'+imageDomain+'/%s/%s_%s.jpg' % (server,id,secret)
					imageBIN = self.getRemoteFile(imageDomain,imageURL)

					if imageBIN is None:
						self.addmessage('Error al leer la imagen: %s (Palabra:%s)' % (imageURL,self.pal_palabra))
						fails = fails + 1
						continue
					
					imageType = imghdr.what(None,imageBIN[0:32])
					if imageType is None: imageType = 'jpg'
#						self.addmessage('El archivo no es una imagen: %s' % imageURL)
#						fails = fails + 1
#						continue
					
					# valido que la imagen no se encuentre en la base de datos
					md5File  = md5.new(imageBIN).hexdigest()
#					print md5File
					self.rows = self.seleccionar("SELECT cfl_md5_file FROM cfl_contenido_flickr WHERE cfl_md5_file = '%s'" % md5File)
					if self.cursor.rowcount > 0:
						self.addmessage('La imagen ya se encuentra en la base de datos: %s' % imageURL)
						fails = fails + 1
						yaExiste = 1
						continue

					imageName = "%s" % md5.new(busq+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cfl_contenido_flickr").hexdigest()
					imagePath = path+imageName+'.'+imageType
					while os.path.isfile(imagePath) == True:
						imageName = "%s" % md5.new(busq+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cfl_contenido_flickr").hexdigest()
						imagePath = path+imageName+'.'+imageType

					now    = datetime.today()
					fecha = now.strftime("%y-%m-%d %H:%M:%S")

					# CHEQUEO QUE LA FOTO NO ESTE YA EN NUESTRA BASE DE DATOS...
#					idDB = ''
#					self.rows = self.seleccionar("SELECT cfl_foto_id FROM cfl_contenido_flickr WHERE cfl_foto_id = '" + id + "'")
#					for row in self.rows:
#						idDB = row['cfl_foto_id']

					# ...SI ESTA, NO LO AGREGA.<html>
#					if idDB <> id:
						# HAGO EL INSERT EN LA DB
					infoMeta = {
						'imagen_local'     : self.escapeString(str(imageName + '.' + imageType)),
						'imagen_original'  : self.escapeString(str(imageURL.encode('utf-8','ignore'))),
						'link'			    : self.escapeString(str(link.encode('utf-8','ignore'))),
						'titulo'           : self.escapeString(str(titulo.encode('utf-8','ignore'))),
						'descripcion'      : self.escapeString(str(descripcion.encode('utf-8','ignore'))),
						'fecha_foto'       : self.escapeString(str(taken)),
						'foto_id'          : id
					}
					try:
						contenido = {
							'cfl_titulo'		: "'%s'" % infoMeta['titulo'],
							'cfl_md5_file'		: "'%s'" % md5File,
							'cfl_fecha'			: "'%s'" % fecha,
							'cfl_imagen_local': "'%s'" % infoMeta['imagen_local'],
							'cfl_metadata'		: "'%s'" % json.dumps(infoMeta)
						}
						insert_id = self.agregarcontenido('cfl_contenido_flickr', contenido)
						self.saveFile(imagePath,imageBIN)
						self.items_found = inc(self.items_found)
					except Exception , e:
						self.addmessage('Flickr error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
						continue

#			print self.items_found
			# Me voy!
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Flickr error: %s(Palabra:%s)' % (str(e),self.pal_palabra))
			return False

