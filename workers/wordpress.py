# -*- coding: utf-8 -*-
from library import WorkerBase,iif,inc
class worker(WorkerBase):

	def run(self):
		try:
			self.page = iif(self.page == 0, 1, self.page)
			
			import re
			busq = re.sub('\s+','+',self.pal_palabra)

			# BUSCO EL IDIOMA
			lang = self.getLanguage()
			
			url = 'http://%s.search.wordpress.com/?q=%s&page=%s&f=json' %(lang,busq,self.page)
			try:
				htmldoc = self.readPage(url)
			except IOError,e:
				self.addmessage('Wordpress error %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
				return False
			from datetime import datetime
			import json
		
			try: contenido = json.loads(htmldoc)
			except:
				self.addmessage('Wordpress Search fuera de servicio temporalemnte(URL:%s)' % url )
				return False

			#pac_id = self.relacionarConPalabra(self.pal_palabra,'2')
#			pac_id = 0
			
			if(contenido is None): return False
			
			for pepe in contenido:

				if self.items_found == int(self.config['cant_items']): return True
				now    = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")

				# TITULO
				titulo = pepe['title']
				titulo = self.escapeString(str(titulo))

				# LINK
				link = pepe['link']

				# DESCRIPCION
				desc = pepe['content']
				desc = self.escapeString(str(desc))
				
				# AUTOR
				autor = pepe['author']
				
				# EPOCH TIME (FECHA DEL BLOG)
				epoch_time = pepe['epoch_time']


				# CHEQUEO QUE LA NOTICIA NO ESTE YA EN NUESTRA BASE DE DATOS...
				linkDB = ''
				self.rows = self.seleccionar("SELECT cwp_link FROM cwp_contenido_wordpress WHERE cwp_link = '" + link + "'")
				for row in self.rows:
					linkDB = row['cwp_link']

				# ...SI ESTA, NO LO AGREGA.
				if linkDB <> link:
					# HAGO EL INSERT EN LA DB
					infoMeta = {
						'cwp_titulo'		: "%s" % self.escapeString(titulo),
						'cwp_link'			: "%s" % self.escapeString(link),
						'cwp_descripcion'	: "%s" % self.escapeString(desc),
						'cwp_autor'			: "%s" % self.escapeString(autor),
						'cwp_epoch_time'	: "%s" % self.escapeString(epoch_time)
					}
					try :
						contenido = {
							'cwp_link'			: "'%s'" % link,
							'cwp_fecha'			: "'%s'" % fecha,
							'cwp_metadata'		: "'%s'" % json.dumps(infoMeta)
						}
						#self.insertar("cwp_contenido_wordpress",contenido)
						insert_id = self.agregarcontenido('cwp_contenido_wordpress', contenido)
						self.items_found = inc(self.items_found)
					except Exception , e:
						self.addmessage('Wordpress error: %s(palabra:%s)' %  ( str(e),self.pal_palabra ))

			# Me voy!
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmesssage('Wordpress error %s(Palabra:%s)' % ( str(e),slef.pal_palabra) )
			return False
