from library import WorkerBase,iif,inc
class worker(WorkerBase):

	def run(self):
		try:
			self.page = iif(self.page == 0, 1, self.page)
			import re
			busq = re.sub('\s+','+',self.pal_palabra)

			# BUSCO EL IDIOMA
			lang = self.getLanguage()

			#PARAMETROS QUE TENGO QUE PASAR PARA HACER UNA BUSQUEDA
			url_base = 'http://search.twitter.com/search.json'
			query = busq
			url = url_base + "?lang=%s&page=%d&q=%s" % (lang,self.page,query)
#			self.addmessage('URL Request: %s' % url)

			try:
				htmldoc = self.readPage('%s' % (url))
			except IOError,e:
				self.addmessage('Twitter error: %s(Palabra:%s)' % str(e))
				return False

			from datetime import datetime
			import json
			
			contenido = json.loads(htmldoc)
			try: naranja = contenido['results'][0]['text']
			except:
				self.addmessage('Twitter: No hay mas resultados!')
				return False

			lista = contenido['results']

			#pac_id = self.relacionarConPalabra(self.pal_palabra,'2')
			
			for pepe in lista:

				if self.items_found == int(self.config['cant_items']): return True
				now    = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")

				mensaje = pepe['text']
				from_user = pepe['from_user']
				id = str(pepe['id'])
				created_at = pepe['created_at']
				link = 'http://twitter.com/%s/statuses/%s' % (from_user,id)


				# CHEQUEO QUE LA NOTICIA NO ESTE YA EN NUESTRA BASE DE DATOS...
				idDB = ''
				self.rows = self.seleccionar("SELECT ctw_mensaje_id FROM ctw_contenido_twitter WHERE ctw_mensaje_id = '" + id + "'")
				for row in self.rows:
					idDB = row['ctw_mensaje_id']

				# ...SI ESTA, NO LO AGREGA.
				if idDB <> id:
					# HAGO EL INSERT EN LA DB
					infoMeta = {
						'ctw_mensaje'			: "%s" % self.escapeString(mensaje),
						'ctw_usuario'			: "%s" % self.escapeString(from_user),
						'ctw_link'				: "%s" % self.escapeString(link),
						'ctw_date'				: "%s" % self.escapeString(created_at)
					}
					try:
						contenido = {
							'ctw_mensaje_id'		: "'%s'" % id,
							'ctw_fecha'				: "'%s'" % fecha,
							'ctw_metadata'			: "'%s'" % json.dumps(infoMeta)
						}
						#self.insertar("ctw_contenido_twitter",contenido)
						insert_id = self.agregarcontenido('ctw_contenido_twitter', contenido)
						self.items_found = inc(self.items_found)
					except Exception , e:
						self.addmessage('Twitter error: %s(Palabra:%s))' % ( str(e),self.pal_palabra ))

			# Me voy!
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Twitter error %s ' % str(e) )
			return False
