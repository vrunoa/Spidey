# -*- coding: utf-8 -*-
import library
from library import WorkerBase,iif,inc
from BeautifulSoup import BeautifulSoup
class worker(WorkerBase):

	def run(self):
		try:
			start = self.page * int(self.config['cant_items'])

			import re
			busq = re.sub('\s+','+',self.pal_palabra)

			# BUSCO EL IDIOMA
			lang = self.getLanguage()

			url = 'http://news.google.com/news?pz=1&ned=us&hl=%s&q=%s&start=%s' %(lang,busq,start)
			try:
				htmldoc = self.readPage(url)
			except IOError,e:
				self.addmessage('Googlenews error %s(Palabra:%s)' %  ( str(e), self.pal_palabra ) )
				return False

			from datetime import datetime
			import json

#			htmldoc = self.normalizar(htmldoc)
		
			soup = BeautifulSoup(htmldoc)
			bloque = soup.findAll("div",{"class":re.compile('story cid[\s\S]')})

			if len(bloque) == 0:
				self.addmessage('Googlews no hay mas resultado para la url %s(Palabra:%s)' % ( url, self.pal_palabra ) )
				return False

			i = 0
			for valor in bloque:
				
				i = i + 1
				
				if self.items_found == int(self.config['cant_items']): return True

				now   = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")

				# TITULO
				val = valor.find("h2",{"class":"title"})		

				tit = val.find("a").contents
				titulo = ''
				for txt in tit:
					try    : titulo = titulo + str(txt)
					except : pass
				
#				titulo = re.sub('\[',	'', titulo)
#				titulo = re.sub('\]',	'', titulo)
#				titulo = re.sub('<b>',	'', titulo)
#				titulo = re.sub('</b>,','', titulo)
#				titulo = re.sub('</b>',	'', titulo)
#				titulo = re.sub('u\'',	'', titulo)
#				titulo = re.sub('\',',	'', titulo)
#				titulo = re.sub('\'',	'', titulo)
#				titulo = self.normalizar(titulo)
				
				#desc   = titulo
				
				# LINK
				link = val.find("a")['href']
				# DESCRIPCION
				desc = ''
				try    : dsc = valor.find("div",{"class":"snippet"}).contents
				except : dsc = None
				if dsc is not None:
					for txt in dsc:
						try    : desc = desc + str(txt)
						except : pass

#				desc = re.sub('<b>', '', desc)
#				desc = re.sub('</b>', '', desc)
#				desc = re.sub('u\'', '', desc)
#				desc = re.sub('\'', '', desc)
#				desc = re.sub('\[', '', desc)
#				desc = re.sub('\]', '', desc)
#				desc = re.sub('u\'\Sxfa\'', '', desc)
##				desc = self.decode_htmlentities(desc)
#				desc = self.normalizar(desc)
			
				#desc = self.escapeString(desc.encode('utf-8','ignore'))

				# CHEQUEO QUE LA NOTICIA NO ESTE YA EN NUESTRA BASE DE DATOS...
				linkDB = ''
				self.rows = self.seleccionar("SELECT cgn_link FROM cgn_contenido_google_news WHERE cgn_link = '" + link + "'")
				for row in self.rows:
					linkDB = row['cgn_link']

				# ...SI ESTA, NO LO AGREGA.
				if linkDB <> link:
					# HAGO EL INSERT EN LA DB
					infoMeta = {
						'cgn_titulo'		: "%s" % self.escapeString(str(titulo)),
						'cgn_link'			: "%s" % link,
						'cgn_descripcion'	: "%s" % self.escapeString(str(desc))
					}
					infoMeta = json.dumps(infoMeta)
					infoMeta = self.escapeUnicode(infoMeta)
					try :
						contenido = {
							'cgn_link'		: "'%s'" % link,
							'cgn_fecha'		: "'%s'" % fecha,
							'cgn_metadata'	: "'%s'" % infoMeta
						}
						#self.insertar("cgn_contenido_google_news",contenido)
						insert_id = self.agregarcontenido('cgn_contenido_google_news', contenido)
						self.items_found = inc(self.items_found)	
					except Exception , e:
						self.addmessage('Google News error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ))


			if(len(bloque)< self.config['cant_items']): return True

			# Me voy!
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Googlenews error %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
			return False


