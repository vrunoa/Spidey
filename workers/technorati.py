from library import WorkerBase,iif,inc
class worker(WorkerBase):

	def run(self):
#		try:
			
			start = iif( self.page == 0, 1, self.page * int(self.config['cant_items']))
			#ACOMODO EL start SINO ME TIRA ERROR
			start = iif( start == 0, 1, start)
			
			import re
			busq = re.sub('\s+','+',self.pal_palabra)

			# BUSCO EL IDIOMA
			lang = self.getLanguage()
			if start > 500:
				self.addmessage('Technorati start index overflow')
				return False
			url = 'http://api.technorati.com/search?key=9224718b604bcf29cca87d03fc16efb9&query=%s&language=%s&start=%s&limit=21' % (busq,lang,start)
			print url
			return
			try:
				xmldoc = self.getSourceAsDOM('%s' % (url))
			except IOError,e:
				self.addmessage('Technorati error %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
				return False
		
#			xmldoc = xmldoc.getElementsByTagName('document')[0]
			
			cantidad = xmldoc.getElementsByTagName('querycount')[0].firstChild.nodeValue;
			if int(cantidad) == 0:
				self.addmessage('Technorati no hay resultados para la url %s' % url  )
				return False

			itemList = xmldoc.getElementsByTagName("item")

			from datetime import datetime
			import json

			items = xmldoc.getElementsByTagName('item')

			for item in items :
				
				if self.items_found == int(self.config['cant_items']): return True
				meta = {}	
				try: 
					meta['cte_titulo'] = "'%s'" % self.escapeString(str(item.getElementsByTagName('title')[0].firstChild.data))
				except: pass
				try: 
					meta['cte_descripcion'] = "'%s'" % self.escapeString(str(item.getElementsByTagName('excerpt')[0].firstChild.data))
				except: pass
				try: 
					link = item.getElementsByTagName('url')[0].firstChild.data
					meta['cte_link'] = "'%s'" % link
				except: pass
				try:
					meta['cte_nombre'] = "'%s'" % self.escapeString(str(item.getElementsByTagName('name')[0].firstChild.data))
				except: pass

				now    = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")
				
				# CHEQUEO QUE EL POST NO ESTE YA EN NUESTRA BASE DE DATOS...
				linkDB = ''
				self.rows = self.seleccionar("SELECT cte_link FROM cte_contenido_technorati WHERE cte_link = '" + link + "'")
				for row in self.rows: linkDB = row['cte_link']

				# ...SI ESTA, NO LO AGREGA.
				if linkDB <> link:
					# HAGO EL INSERT EN LA DB
					# Le agrego las comillas a los strings
					try :
						contenido = {
							'cte_link'			: "'%s'" % link,
							'cte_fecha'			: "'%s'" % fecha,
							'cte_metadata'		: "'%s'" % json.dumps(meta)
						}
						insert_id = self.agregarcontenido('cte_contenido_technorati', contenido)
						self.items_found = inc(self.items_found)
					except Exception , e:
						print e
						self.addmessage('Technorati error: %s(Palabra:%s)' % ( str(e), self.pal_palabra) )

			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True
			
#		except Exception, e:
#			self.addmessage('Technorati error %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
#			return False
	
