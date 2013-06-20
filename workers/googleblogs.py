# -*- coding: utf-8 -*-
from library import WorkerBase,iif,inc
class worker(WorkerBase):

	def run(self):
		try:
		
			start = int(self.page) * int(self.config['cant_items'])
			
			num = int(self.config['cant_items'])

			import re
			busq = re.sub('\s+','+',self.pal_palabra)

			# BUSCO EL IDIOMA
			lang = self.getLanguage()

			#PARAMETROS QUE TENGO QUE PASAR PARA HACER UNA BUSQUEDA
			url_base = 'http://blogsearch.google.com/blogsearch_feeds'
			url = url_base + "?hl=%s&q=%s&ie=utf-8&num=%s&output=rss&start=%s" % (lang,busq,num,start)

			try:
				dom = self.readPage(url)
			except IOError,e:
				self.addmessage('Googleblogs error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ))
				return False
	
			dom = self.getSourceAsDOM(dom, False)
			
			try    : results = dom.getElementsByTagName('opensearch:totalResults')[0].firstChild.nodeValue;
			except : 
				self.addmessage('Googleblogs DOM corrupted')
				return False

			if int(results) == 0:
				self.addmessage('Googleblogs: No hay resultados para la url %s(Palabra:%s)' % ( url,self.pal_palabra ) )
				return False

			from datetime import datetime
			import json

			#pac_id = self.relacionarConPalabra(self.pal_palabra,'2')
			#pac_id = 0
			
					
			for node in dom.getElementsByTagName('item'):

				if self.items_found == int(self.config['cant_items']): return True
				now    = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")

				titulo = node.getElementsByTagName('title')[0].firstChild.nodeValue
				titulo = re.sub('<b>','',titulo)
				titulo = re.sub('</b>','',titulo)
				link = node.getElementsByTagName('link')[0].firstChild.nodeValue
				descripcion = node.getElementsByTagName('description')[0].firstChild.nodeValue
				descripcion = re.sub('<b>','',descripcion)
				descripcion = re.sub('</b>','',descripcion)
				fecha_blog = node.getElementsByTagName('dc:date')[0].firstChild.nodeValue


				# CHEQUEO QUE EL BLOG NO ESTE YA EN NUESTRA BASE DE DATOS...
				linkDB = ''
				self.rows = self.seleccionar("SELECT cgb_link FROM cgb_contenido_google_blogs WHERE cgb_link = '" + link + "'")
				for row in self.rows:
					linkDB = row['cgb_link']

				# ...SI ESTA, NO LO AGREGA.
				if linkDB <> link:
					# HAGO EL INSERT EN LA DB
					infoMeta = {
						'cgb_titulo'		: "%s" % self.escapeString(titulo),
						'cgb_descripcion'	: "%s" % self.escapeString(descripcion),
						'cgb_date'			: "%s" % self.escapeString(fecha_blog)
					}
					infoMeta = json.dumps(infoMeta)
					infoMeta = self.escapeUnicode(infoMeta)
					try:
						contenido = {
							'cgb_link'			: "'%s'" % link,
							'cgb_fecha'			: "'%s'" % fecha,
							'cgb_metadata'		: "'%s'" % infoMeta
						}
						#self.insertar("cgb_contenido_google_blogs",contenido)
						insert_id = self.agregarcontenido('cgb_contenido_google_blogs', contenido)
						self.items_found = inc(self.items_found)
					except Exception , e:
						self.addmessage('Google Blogs error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )

			# Me voy!
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Googleblogs error %s ' % str(e) )
			return False
