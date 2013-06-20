from library import WorkerBase,iif,inc
from time import strftime,gmtime
from BeautifulSoup import BeautifulSoup
import re,json
class worker(WorkerBase):
	
	def run(self):
		try:
			busq = re.sub('\s+','+',self.pal_palabra)
			start = iif(self.page == 0, 1, (self.page*50)+1)
			
			url   = 'http://ariadna.elmundo.es/buscador/archivo.html?q=%s&t=1&i=%d&n=50&w=45' % (busq,start)
			print url
#			self.addmessage('URL Request: %s' % url)
			
			html = self.readPage(url, 'iso-8859-1')
			html = re.sub('\s+',' ',html)
			html = self.normalizar(html)
#			html = html.decode('iso-8859-1')

			regexp = '<table border=0 cellspacing="0" cellpadding="3">\s*<tr>\s*'
			regexp = '%s<td valign="top" rowspan=2 class=titulopagina>\s*<b>\s*[0-9]+\.?</b>\s*</td>\s*' % regexp
			regexp = '%s<td>\s*<a class=titulopagina href="[\/\w\.\?\&:-]+">\s*[\/\w\.\?\&\s\,\(\)\|\'":-]+</a>\s*</td>\s*' % regexp
			regexp = '%s</tr>\s*<tr>\s*' % regexp
			regexp = '%s<td>\s*([\/\w\.\?\&\s\,\(\)\|\]\[\'\+"%%:;-]+<br>\s*)+' % regexp
			regexp = '%s<a class="url" href="[\/\w\.\?\&:-]+" title="[\/\w\.\?\&:-]+">[\/\w\.\?\&:-]+</a>\s*' % regexp
			regexp = '%s\s*-\s*<a class="nuevaventana" target="_blank" href="[\/\w\.\?\&:-]+">\s*[\/\w\.\?\&\s\,\(\)\|\]\[\'\+":-]+</a>\s*<br>\s*' % regexp
			regexp = '%s<a class="relacionadas" href="[\/\w\.\?\&:-=]+">[\/\w\.\?\&\s\,\(\)\|\]\[\'\+"%%:;-]+</a>\s*' % regexp
			regexp = '%s</td>\s*</tr>\s*</table>\s*' % regexp

			result = re.finditer(regexp,html)
			if result is None:
				self.addmessage('El Mundo no ha encontrado resultados')
				return False

			if any(result) == False:
				self.addmessage('El Mundo no ha encontrado resultados')
				return False
			for m in	result:
				if self.items_found == int(self.config['cant_items']): return True 
				dom = m.group(0)
				soup = BeautifulSoup(dom)
				link = soup.findAll('a',{'class':'url'})[0]['href'];
				sql  = "SELECT cem_id FROM cem_contenido_elmundo WHERE cem_link = '%s'" % self.escapeString(str(link))
				if len(self.seleccionar(sql)) > 0:
#					self.addmessage('La noticia ya se encuentra en nuestra base de datos: %s' %  link)
					continue

				meta = {}
				meta['titulo']      = self.escapeString(str(soup.findAll('a',{'class':'titulopagina'})[0].contents[0]))
				desc = soup.findAll('tr')[1].findAll('td')[0].contents
				meta['descripcion'] = str(desc[0]) + str(desc[1]) + str(desc[2])
				meta['descripcion'] = self.escapeString( str(meta['descripcion']) )

				meta['url']         = link				
				
				info = self.escapeString(str(soup.findAll('tr')[1].findAll('td')[0].contents[0]))
				try    :	meta['pubDate'] = re.search('\d{2}\/\d{2}\/\d{2,4}',info).group(0)
				except : pass
				try    : meta['coincidence'] = re.search('\d+(\.\d+)?%',info).group(0)
				except : pass
				
				try:
					data = {
						'cem_fecha'    : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cem_titulo'   : "'%s'" % meta['titulo'],
						'cem_link'     : "'%s'" % link,
						'cem_metadata' : "'%s'" % json.dumps(meta)
					}
					insert_id = self.agregarcontenido('cem_contenido_elmundo', data)
					self.items_found = inc(self.items_found)
				except Exception, e:
					self.addmessage('El Mundo error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )

			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception,e:
			self.addmessage('EL Mundo Search error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
			return False

