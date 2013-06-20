from library import WorkerBase
from time import strftime,gmtime
import re,json
class worker(WorkerBase):
	
	def run(self,category = 1001, items_found = 0):
		"""
		Categorias RSS
		  * Secciones
				Internacional  : 1001
				America Latina : 17041
				Mexico         : 17042
				Europa         : 17043
				Estados Unidos : 17044
				Oriente proximo: 17045
				Espania        : 1002
				Andalucia      : 17057
				Catalunia      : 17059
				Com.Valenciana : 17061
				Madrid         : 1016
				Pais Vasco     : 17062
				Galicia        : 17063
				Deportes       : 1007
				Futbol         : 17047
				Motor          : 17040
				Baloncesto     : 17048
				Ciclismo       : 17049
				Tenis          : 17050
				Cultura        : 1008
				Arte           : 17060
				Musica         : 17051
				Cine           : 17052
				Literatura     : 17053
				Moda           : 17054
				Tecnologia     : 1005
				Economia       : 1006
				Trabajo        : 17066
				Sociedad       : 1004
				Educacion      : 17064
				Religion       : 17065
				Gente y TV     : 1009
				Ciencia        : 17068
				Justicia y leyes     : 17069
				Guerras y conflictos : 17070
				Medio ambiente       : 17071
				Politica             : 17073
				Salud                : 17074
				Ocio                 : 17075
		"""
		try:

			url  = 'http://www.elpais.com/rss/feed.html?feedId=%d' % category
			print url
#			self.addmessage('URL Request: %s' % url)
#			try: htmldom = self.getSourceAsDOM(url)
			try: htmldom = self.readPage(url, 'iso-8859-1')
			except:
				self.addmessage('El Pais RSS format error(Palabra:%s, URL:%s'%(self.pal_palabra,url))
				return False

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
			
				link = item.getElementsByTagName('link')[0].firstChild.nodeValue	
 				sql  = "SELECT cep_id FROM cep_contenido_elpais WHERE cep_link = '%s'" % self.escapeString(str(link))
				if len(self.seleccionar(sql)) > 0:
#					self.addmessage('La noticia ya se encuentra en nuestra base de datos: %s' %  link)
					continue
			
				meta['url'] = link
				jmeta = json.dumps(meta)
				try :
					data = {
						'cep_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cep_titulo'   : "'%s'" % meta['titulo'],
						'cep_link'     : "'%s'" % link,
						'cep_metadata' : "'%s'" % jmeta
					}
					insert_id = self.agregarcontenido('cep_contenido_elpais', data)
					items_found = items_found + 1
				except Exception , e:
					self.addmessage('El Pais error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )

			next = self.findNextCategory(category)	
			if next == False: return True
				
			self.run( next , items_found )

		except Exception,e:
			self.addmessage('EL Pais error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )
			return False

		return True
	
	def findNextCategory(self,current):
		categories = [1001,17041,17042,17043,17044,17045,1002,17057,17059,17061,1016,17062,17063,1007,17047,17040,17048,17049,17050,1008,17060,17051,17052,17053,17054,1005,1006,17066,1004,17064,17065,1009,17068,17069,17070,17071,17073,17074,17075]
		for index, item in enumerate(categories):
			if item != current: continue
			if index + 1 == len(categories): return False
			return categories[index+1]
		return False
