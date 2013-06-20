from library import WorkerBase,iif,inc
from time import strftime,gmtime
import re,json
class worker(WorkerBase):
	
	def run(self):
		try :

			self.page = iif(self.page == 0, 1, self.page)
			try    : self.params['page_visit'] = inc(self.params['page_visit'])
			except : self.params['page_visit'] = 0
			if self.params['page_visit'] > 25: 
				self.addmessage('ABCNews search recursividad superada')
				return False

			url  = 'http://www.abc.es/hemeroteca/resultados-busqueda-avanzada/1/50/%d/01012002/%s/RANK,+,%s,+,+,+.html' % (self.page,strftime('%d%m%Y',gmtime()),self.pal_palabra)
#			self.addmessage('URL Request: %s' % url)

			html = self.readPage(url, 'iso-8859-1')
			html = re.sub('\s+',' ',html)
			html = self.normalizar(html)
			regexp = '<div class="resultado-busqueda">\s*'
			regexp = '%s<h3><a href="[\/\w\.\?\&-]+">[\/\w\.\?\&\s\,\(\)\|":-]+</a>\s*</h3>\s*' % regexp	
			regexp = '%s<h4>[\/\w\.\?\&\s\,\(\)\|":-]+</h4>\s*' % regexp
			regexp = '%s(<span class="separador">\|</span>)?\s*' % regexp
			regexp = '%s<div class="date">[\d\s:-]+</div>\s*' % regexp
			regexp = '%s<div class="byline">[\/\w\.\?\&\s\,\(\)\|":-]+</div>\s*' % regexp
			regexp = '%s<div class="subhead">[\/\w\.\?\&\s\,\(\)\|":-]+</div>\s*' % regexp
			regexp = '%s<div class="clear">\s*</div>\s*' % regexp
			regexp = '%s</div>\s*' % regexp
			result = re.finditer(regexp,html)
		
			if result is None or any(result) == False:
				self.addmessage('ABCNews search no ha encontrado resultados')
				return False

			for m in	result:
				if self.items_found == int(self.config['cant_items']): return True
				
				dom = m.group(0)
				dom = self.getSourceAsDOM(dom,False)			
				meta = {}
				link    = 'http://www.abc.es%s' % dom.getElementsByTagName('a')[0].getAttribute('href')
				meta['titulo'] = dom.getElementsByTagName('a')[0].firstChild.nodeValue
				for node in dom.getElementsByTagName('div'):
					className = node.getAttribute('class')
					if className=='date':
						meta['pubDate'] = str(node.firstChild.nodeValue)
					elif className=='subhead':
						meta['descripcion'] = str(node.firstChild.nodeValue)

				sql  = "SELECT cab_id FROM cab_contenido_abc WHERE cab_link = '%s'" % self.escapeString(str(link))
				if len(self.seleccionar(sql)) > 0:
#					self.addmessage('La noticia ya se encuentra en nuestra base de datos: %s' %  link)
					continue
				meta['url'] = link

				try:
					data = {
						'cab_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cab_titulo'   : "'%s'" % meta['titulo'],
						'cab_link'     : "'%s'" % link,
						'cab_metadata' : "'%s'" % json.dumps(meta)
					}
					insert_id = self.agregarcontenido('cab_contenido_abc', data)
					self.items_found = inc(self.items_found)
				except Exception, e:
					self.addmessage('ABC error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )


			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('ABC News Search error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
			return False

