from library import WorkerBase
from time import strftime,gmtime
import re,json
class worker(WorkerBase):
	
	def run(self,category = 'abcPortada',items_found = 0):
		try:
			url  = 'http://www.abc.es/rss/feeds/%s.xml' % category
			htmldom = self.readPage(url, False)
			htmldom = self.getSourceAsDOM(htmldom, False)

			for item in htmldom.getElementsByTagName('item'):
						
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
				sql  = "SELECT cab_id FROM cab_contenido_abc WHERE cab_link = '%s'" % self.escapeString(str(link))
				if len(self.seleccionar(sql)) > 0:
					# self.addmessage('La noticia ya se encuentra en nuestra base de datos: %s' %  link)
					continue
				
				meta['url'] = link
				
				jmeta = json.dumps(meta)
				jmeta = self.escapeUnicode(jmeta)

				try :
					data = {
						'cab_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cab_titulo'   : "'%s'" % meta['titulo'],
						'cab_link'     : "'%s'" % link,
						'cab_metadata' : "'%s'" % jmeta
					}
					insert_id = self.agregarcontenido('cab_contenido_abc', data)
					items_found = items_found + 1
				except Exception , e:
					self.addmessage('ABC news error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )

				if items_found == int(self.config['cant_items']): return True 
	
		except Exception,e:
			self.addmessage('ABC error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )
			return False
		
		next = self.findNextCategory(category)	
		if next == False: return True
			
		self.run( next , items_found )
		return True
	
	def findNextCategory(self,current):
		categories = ['abcPortada','abc_Automovilismo','abc_Baloncesto','abc_Ciclismo','abc_Futbol','abc_Motociclismo','abc_Tenis','abc_Deportes','abc_EspanaEspana','abc_Nacional','abc_Politica','abc_Sociedad','abc_Sucesos','abc_Terrorismo','ABC_Toros','abc_Tribunales','abc_Banca','abc_Bolsa','abc_EconomiaEconomia','abc_Empresas','abc_Laboral','abc_DeLujo','abc_ModaBelleza','abc_Ocio','abc_ViajesGourmet','abc_CasasReales','abc_Celebrities','abc_Famosos','abc_Rock_tops','abc_Arqueologia','abc_Arte','abc_CulturaCultura','abc_Libros','abc_Patrimonio','abc_Cine','abc_Espectaculos','abc_Musica','abc_Teatro','abc_Educacion','abc_Religion','abc_SociedadSociedad','abc_Contraportada','ABC_Medios%20Digitales','ABC_Medios_Redes_Medios_Redes','ABC_Prensa','ABC_Publicidad','ABC_Radio%20y%20Tv','ABC_Redes','abc_USA','abc_Europa','abc_Iberoamerica']
		for index, item in enumerate(categories):
			if item != current: continue
			if index + 1 == len(categories): return False
			return categories[index+1]
		return False
