from library import WorkerBase
from time import strftime,gmtime
import re,json
class worker(WorkerBase):
	
	def run(self,category = 4, items_found = 0):
		"""
		Categorias RSS
		  * Ultima Hora
				Portada            : 4
				Espania            : 8
				Internacional      : 9
				Economia           : 7
				Cultura            : 6
				Ciencia / Ecologia : 5
				Madrid / 24 horas  : 10
				Barcelona          : 95
				Baleares           : 81
				Castilla y Leon    : 110
				Valencia           : 111
				Solidaridad        : 12
				Comunicacion       : 26
				Television         : 76
		  * Deportes
				Portada            : 14
				Futbol             : 59
				Baloncesto         : 57
				Ciclismo           : 58
				Golf               : 60 
				Tenis              : 63
				Motor              : 62
				Mas deporte        : 61
			* Salud
				Portada            : 16
			* Motor
				Portada            : 17
			* Blogs
				Cronicas desde africa : 109
				Cronicas del cono sur : 112
				Cronicas desde Asia   : 113
				Oriente proximo       : 103
		"""
		try:

			url  = 'http://rss.elmundo.es/rss/descarga.htm?data2=%d' % category
#			self.addmessage('URL Request: %s' % url)
			htmldom = self.readPage(url)
			htmldom = self.getSourceAsDOM(htmldom, False)
			
			for item in htmldom.getElementsByTagName('item'):
						
	 			if items_found == int(self.config['cant_items']): return True 
				try    : titulo = self.escapeString(str(item.getElementsByTagName('title')[0].firstChild.nodeValue))
				except : titulo = ''

				try    : descripcion = self.escapeString(str(item.getElementsByTagName('description')[0].firstChild.nodeValue))
				except : descripcion = ''				

				try    : author = self.escapeString(str(item.getElementsByTagName('author')[0].firstChild.nodeValue))
				except : author = ''

				try    : pubDate = self.escapeString(str(item.getElementsByTagName('pubDate')[0].firstChild.nodeValue))
				except : pubDate = ''

				meta = {
					'titulo'      : titulo,	
					'descripcion' : descripcion,
					'author'      : author,
					'pubDate'     : pubDate
				}
				if re.search(self.pal_palabra,meta['titulo'],re.IGNORECASE) is None:
					if re.search(self.pal_palabra,meta['descripcion'],re.IGNORECASE) is None:
						continue	
			
#				print meta	
				link = item.getElementsByTagName('link')[0].firstChild.nodeValue
				sql  = "SELECT cem_id FROM cem_contenido_elmundo WHERE cem_link = '%s'" % self.escapeString(str(link))
				if len(self.seleccionar(sql)) > 0:
#					self.addmessage('La noticia ya se encuentra en nuestra base de datos: %s' %  link)
					continue
				
				meta['url'] = link
				try :
					media = {}
					media['duration'] = self.escapeString(str(item.getElementsByTagName('itunes:duration')[0].firstChild.nodeValue))
					media['author']   = self.escapeString(str(item.getElementsByTagName('itunes:author')[0].firstChild.nodeValue))
					enclosure         = item.getElementsByTagName('enclosure')[0]
					media['url']      = self.escapeString(str(enclosure.getAttribute('url')))
					media['length']   = self.escapeString(str(enclosure.getAttribute('length')))
					media['type']	   = self.escapeString(str(enclosure.getAttribute('type')))
					meta['media']	   = media
				except: 
					pass
			
				jmeta = json.dumps(meta)
				jmeta = self.escapeUnicode(jmeta)
#				print jmeta	
				try :
					data = {
						'cem_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cem_titulo'   : "'%s'" % meta['titulo'],
						'cem_link'     : "'%s'" % link,
						'cem_metadata' : "'%s'" % jmeta
					}
					insert_id = self.agregarcontenido('cem_contenido_elmundo', data)
					items_found = items_found + 1
				except Exception , e:
					self.addmessage('El Mundo error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
 
			next = self.findNextCategory(category)	
			if next == False: return True
			
			self.run( next, items_found )

		except Exception,e:
			self.addmessage('EL Mundo error: %s(Palabra:%s)' % ( str(e), self.pal_palabra )  )
			return False

		return True

	def findNextCategory(self,current):
		categories = [4,8,9,7,6,5,10,95,81,110,111,12,26,76,14,59,57,58,60,63,62,61,16,17,109,112,113,103]
		for index, item in enumerate(categories):
			if item != current: continue
			if index + 1 == len(categories): return False
			return categories[index+1]
		return False
