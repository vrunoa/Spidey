# -*- coding: utf-8 -*-
import os,json,re,imghdr,md5,random,urllib
from time import strftime,gmtime
from library import WorkerBase
class worker(WorkerBase):

	def run(self):
		try:
			from library import iif, inc
			self.page = iif(self.page == 0, 1, self.page)

			import re
			busq = re.sub('\s+','+',self.pal_palabra)
			# BUSCO EL IDIOMA
			lang = self.getLanguage()

#			url = 'http://www.panoramio.com/map/?tag=%s' %(busq)
			url = 'http://www.panoramio.com/map/get_panoramas?order=popularity&set=tag-%s&size=thumbnail&from=0&to=4&minx=155.390625&miny=65.36683689226321&maxx=138.515625&maxy=79.03843742487174' % busq
			try:
				htmldoc = self.readPage(url)
			except IOError,e:
				self.addmessage('Panoramio error %s(Palabra:%s) ' % ( str(e), self.pal_palabra ) )
				return False

			from datetime import datetime
			import json
			_json = json.loads(htmldoc)
			
			if _json['count'] == 0:
				self.addmessage('Panoramio: no hay resultados para la url %s(Palabra: %s)' % (url, self.pal_palabra))
				return True

			path = re.sub('\/$', '',self.config['images_path'])
			path = '%s/%s/' % (path, strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):	os.makedirs(path)
	
			for photo in _json['photos']:
				
				if self.items_found == int(self.config['cant_items']): return True
				
				meta      = photo
				thumb_url = 'http://static.panoramio.com/photos/original/%d.jpg' % int(photo['photo_id'])
				domain    = re.sub('http://','',thumb_url)
				domain    = re.split('\/',domain)[0]
				imageBIN  = self.getRemoteFile(str(domain),thumb_url)
				imageName = ''
				if imageBIN is None: 
					self.addmessage('El archivo no es una imagen: %s' % thumb_url)
					continue
				
				imageType = imghdr.what(None,imageBIN[0:32])
				if imageType is None: imageType = 'png'

				md5File  = md5.new(imageBIN).hexdigest()
				self.rows = self.seleccionar("SELECT cpa_md5_file FROM cpa_contenido_panoramio WHERE cpa_md5_file = '%s'" % md5File)
				if self.cursor.rowcount > 0:
					self.addmessage('La imagen ya se encuentra en la base de datos: %s' % thumb_url)
					continue

				imageName = md5File
				imagePath = str(imageName + '.' + imageType)

				try   : titulo = str(meta['photo_title'])
				except: titulo = ''

				try:
					contenido = {
						'cpa_imagen_local': "'%s'" % self.escapeString(imagePath),
						'cpa_md5_file'		: "'%s'" % md5File,
						'cpa_titulo'      : "'%s'" % self.escapeString(titulo),
						'cpa_fecha'			: "'%s'" % strftime("%Y/%m/%d",gmtime()),
						'cpa_metadata'		: "'%s'" % re.sub("\'+",'', json.dumps(meta))
					}
					insert_id = self.agregarcontenido('cpa_contenido_panoramio', contenido)
					self.saveFile(path + imagePath,imageBIN)
					self.items_found = inc(self.items_found)
				except Exception , e:
					self.addmessage('Panoramio error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ))

			if self.items_found < int(self.config['cant_items']) and bool(_json['has_more']) == True : self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Panoramio error %s(Palabra:%s)' %  ( str(e), self.pal_palabra ) )
			return False
