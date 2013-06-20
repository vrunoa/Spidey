from library import WorkerBase,iif,inc
from time import strftime,gmtime
from BeautifulSoup import BeautifulSoup
import re,json
class worker(WorkerBase):
	
	def run(self):
		try:
			if self.getLanguage() != 'en':
				self.addmessage('Reuters error: Plugin para idioma ingles unicamente')
				return False

			busq = re.sub('\s+','+',self.pal_palabra)
			url = 'http://search.us.reuters.com/query/?q=%s&s=US&st=%d' % (busq,self.page*10)
#			self.addmessage('URL Request: %s' % url)
			
			html = self.readPage(url)
#			print url
			html = re.sub('\s+',' ',html)
			html = self.normalizar(html)
			# html fix
			html = re.sub('<\/scr" \+ "ipt>"','</script>',html) 
			soup = BeautifulSoup(html)
#			print html				
			modHeader = soup.findAll('div',{'class':'moduleheader'})
			if modHeader is None or len(modHeader) == 0:
				self.addmessage('Reuters: No hay mas resultados!')
				return False

			newsAll = soup.findAll('div',{'class':'modulebody'})		
			if newsAll is None:			
				self.addmesage('Reuters no ha encontrado resultados para la url %s' % url )
				return False
				
			hasResults = False
			for news in newsAll:

				if self.items_found == int(self.config['cant_items']): return True
				results = soup.findAll('div',{'class':'searchresult'})
				if len(results) == 0: continue

				hasResults = True
				for result in results:
					
					meta = {}
					try    : meta['pubDate'] = result.findAll('div',{'class':'timestamp'})[0].contents[0]
					except : continue
				
					a = result.findAll('h2')[0].findAll('a')[0]
					meta['link'] = str(a['href'])
				
					sql  = "SELECT cre_id FROM cre_contenido_reuters WHERE cre_link = '%s'" % self.escapeString(str(meta['link']))
					if len(self.seleccionar(sql)) > 0:
#						self.addmessage('La noticia ya se encuentra en nuestra base de datos: %s' %  meta['link'])
						continue
				
					titulo = ''
					for txt in a.contents: titulo = titulo + str(txt)
					meta['titulo'] = self.escapeString(str(titulo))
						
					descrip = ''
					for txt in result.findAll('p')[0].contents: descrip = descrip + str(txt)
					meta['descripcion'] = self.escapeString(str(descrip))

					jmeta = json.dumps(meta)
					jmeta = self.escapeUnicode(jmeta)
					try:
						data = {
							'cre_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
							'cre_titulo'   : "'%s'" % meta['titulo'],
							'cre_link'     : "'%s'" % meta['link'],
							'cre_metadata' : "'%s'" % jmeta
						}
						insert_id = self.agregarcontenido('cre_contenido_reuters', data)
						self.items_found = inc(self.items_found)
					except Exception, e:
						self.addmessage('Reuerts error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ))
			
			if hasResults == False:	
				self.addmesage('Reuters no ha encontrado resultados para la url %s' % url )
				return False

			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Reuters error %s(Palabra:%s) ' % ( str(e),self.pal_palabra ) )
			return False

