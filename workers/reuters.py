from library import WorkerBase
from time import strftime,gmtime
import re,json
class worker(WorkerBase):
	
	def run(self,category = 'topNews',items_found = 0):
		try:
			if self.getLanguage() != 'en':
				self.addmessage('Reuters error: Plugin para idioma ingles unicamente')
				return False

			url  = 'http://feeds.reuters.com/reuters/%s?format=xml' % category
#			self.addmessage('URL Request: %s' % url)
			htmldom = self.getSourceAsDOM(url)
				
			for item in htmldom.getElementsByTagName('item'):
						
				if items_found == int(self.config['cant_items']): return True
 
				try    : titulo = self.escapeString(str(item.getElementsByTagName('title')[0].firstChild.nodeValue.encode('utf-8')))
				except : titulo = ''

				try    :
#					 descripcion = self.escapeString(item.getElementsByTagName('description')[0].firstChild.nodeValue.encode('utf-8'))
					descripcion = item.getElementsByTagName('description')[0].firstChild.nodeValue
					descripcion = re.sub('\<.+','',descripcion)
					descripcion = descripcion.decode('utf-8')
	
				except : descripcion = ''				

				try    : author = self.escapeString(str(item.getElementsByTagName('author')[0].firstChild.nodeValue.encode('utf-8')))
				except : author = ''

				try    : pubDate = self.escapeString(str(item.getElementsByTagName('pubDate')[0].firstChild.nodeValue.encode('utf-8'))) 
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
			
				link = item.getElementsByTagName('link')[0].firstChild.nodeValue.encode('utf-8')
				sql  = "SELECT cre_id FROM cre_contenido_reuters WHERE cre_link = '%s'" % self.escapeString(str(link))
				if len(self.seleccionar(sql)) > 0:
#					self.addmessage('La noticia ya se encuentra en nuestra base de datos: %s' %  link)
					continue
				
				meta['url'] = link
				jmeta = json.dumps(meta)
				jmeta = self.escapeUnicode(jmeta)
				try :
					data = {
						'cre_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cre_titulo'   : "'%s'" % meta['titulo'],
						'cre_link'     : "'%s'" % link,
						'cre_metadata' : "'%s'" % jmeta
					}
					insert_id = self.agregarcontenido('cre_contenido_reuters', data)
					items_found = items_found + 1
				except Exception , e:
					self.addmessage('Reuters error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )

			next = self.findNextCategory(category)	
			if next == False: return True
				
			self.run( next , items_found )
			return True

		except Exception,e:
			self.addmessage('Reuters error %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )
			return False
	
	def findNextCategory(self,current):
		categories = ['topNews','domesticNews','politicsNews','worldNews','businessNews','dealsNews','mergersNews','privateequityNews','entertainment','environment','scienceNews','healthNews','technologyNews','internetNews','sportsNews','oddlyEnoughNews','inDepthNews','lifestyle']
		for index, item in enumerate(categories):
			if item != current: continue
			if index + 1 == len(categories): return False
			return categories[index+1]
		return False
