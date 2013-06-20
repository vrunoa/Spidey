from library import WorkerBase,iif,inc
from time import strftime,gmtime
import re,json
class worker(WorkerBase):
	
	def run(self):
		try:
			
			busq = re.sub('\s+','-',self.pal_palabra)
			start = (self.page * 20 ) + 1
			end   = (start - 1) + 20
			url  = 'http://www.elpais.com/buscar/%s/resultados-%d-al-%d' % (busq,start,end)
#			self.addmessage('URL Request: %s' % url)
			
			html = self.readPage(url, 'iso-8859-15')
			html = re.sub('\s+',' ',html)
			html = self.normalizar(html)
#			print html	
			html = re.sub('<\/?strong>','',html)
			html = re.sub('<\/?i>','',html)
			regexp = '<li class="estirar">\s*'
			regexp = '%s(<div class="mod-img">\s*<a href="[\/\w\.\?\&-]+">\s*<img src="[\/\w\.\?\&-]+" alt="[\/\w\.\?\&\s\,\(\)\|\'":-]+"/>\*s</a>\s*</div>)?\s*' % regexp
			regexp = '%s<div class="mod-txt">\s*' % regexp
			regexp = '%s<h3><a href="[\/\w\.\?\&-]+">[\/\w\.\?\&\s\,\(\)\|\'":-]+</a>\s*</h3>\s*' % regexp	
			regexp = '%s<ul>\s*' % regexp
			regexp = '%s(<li>[\/\w\.\?\&\s\,\(\)\|":-]+</li>\s*)+\s*' % regexp
			regexp = '%s</ul>\s*' % regexp	
			regexp = '%s<p>[\/\w\.\?\&\s\,\(\)\|\]\[\'\+":-]*</p>\s*' % regexp
			regexp = '%s</div>\s*' % regexp
			regexp = '%s</li>\s*' % regexp
				
			result = re.finditer(regexp,html)
			if any(result) == False:
				self.addmessage('El Pais search no ha encontrado resultados')
				return False
			
			i = 0
			for m in	result:
				
				if self.items_found == int(self.config['cant_items']): return True
				i = i + 1
				dom = m.group(0)
				try    : dom = self.getSourceAsDOM(dom,False)			
				except :
#					print dom
#					self.addmessage('HTML Source corrupted: %s' % dom)
					continue
				meta = {}
				link = 'http://www.elpais.com%s' % dom.getElementsByTagName('a')[0].getAttribute('href')
				link = self.escapeString(str(re.sub('tes$','Tes',link)))
				meta['titulo'] = self.escapeString(str(dom.getElementsByTagName('a')[0].firstChild.nodeValue))
				info = []
				for li in dom.getElementsByTagName('ul')[0].getElementsByTagName('li'):
					info.append('%s' % li.firstChild.nodeValue)
				meta['info'] = self.escapeString(','.join(info))
				try    : meta['descripcion'] = self.escapeString(str(dom.getElementsByTagName('p')[0].firstChild.nodeValue))
				except : pass

				sql  = "SELECT cep_id FROM cep_contenido_elpais WHERE cep_link = '%s'" % self.escapeString(str(link))
				if len(self.seleccionar(sql)) > 0:
#					self.addmessage('La noticia ya se encuentra en nuestra base de datos: %s' %  link)
					continue
				
				meta['url'] = link
				try:
					data = {
						'cep_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cep_titulo'   : "'%s'" % meta['titulo'],
						'cep_link'     : "'%s'" % link,
						'cep_metadata' : "'%s'" % json.dumps(meta)
					}
					insert_id = self.agregarcontenido('cep_contenido_elpais', data)
					self.items_found = inc(self.items_found)
				except Exception, e:
					self.addmessage('El Pais search error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )

			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception,e:
			self.addmessage('EL Pais error: %s(Palabra:%s)' % ( str(e),self.pal_palabra) )
			return False
