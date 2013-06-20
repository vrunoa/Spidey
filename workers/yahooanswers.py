 # coding: utf-8
from library import WorkerBase,iif,inc
class worker(WorkerBase):

	def run(self):
		try:

			start = int(self.page) * int(self.config['cant_items'])

			import re
			busq = re.sub('\s+','+',self.pal_palabra)

			# BUSCO EL IDIOMA
			lang = self.getLanguage()
			if lang == 'en': lang = 'us'

			#PARAMETROS QUE TENGO QUE PASAR PARA HACER UNA BUSQUEDA
			url_base = 'http://answers.yahooapis.com/AnswersService/V1/questionSearch'
			appid = self.config['appid']
			output = self.config['output']
			region = lang
			query = busq
			#self.pal_palabra
			url = url_base + "?appid=%s&output=%s&region=%s&query=%s&start=%s" % (appid,output,region,query,start)
			try:
				htmldoc = self.readPage('%s' % (url))
			except IOError,e:
				self.addmessage('Yahooanswers error %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
				return False

			from datetime import datetime
			import json
			
			try:
				contenido = json.loads(htmldoc)
			except Exception,e:
				self.addmessage('Yahooanswers error %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
				return False

			cantidad = contenido['all']['count']
			if int(cantidad) == 0:
				self.addmessage('Yahooanswers no hay resultados para la url %s' % url  )
				return False

			lista = contenido['all']['questions']


			#pac_id = self.relacionarConPalabra(self.pal_palabra,'2')
			
			for pepe in lista:

				if self.items_found == int(self.config['cant_items']): return True
				now    = datetime.today()
				fecha = now.strftime("%y-%m-%d %H:%M:%S")

				id = pepe['Id']
				asunto = self.normalizar(pepe['Subject'])
				asunto = re.sub('[<>]',' ',asunto)
				asunto = re.sub('[\r\n\t]',' ',asunto)
				asunto = self.escapeString(asunto)
				
				desc = self.normalizar(pepe['Content'])
				desc = re.sub('[<>]',' ',desc)
				desc = re.sub('[\r\n\t]',' ',desc)
				desc = self.escapeString(desc)

				date = self.escapeString(pepe['Date'])
				link = self.escapeString(pepe['Link'])
				respuesta_elegida = self.normalizar(pepe['ChosenAnswer'])
				respuesta_elegida = re.sub('[<>]',' ',respuesta_elegida)
				respuesta_elegida = re.sub('[\r\n\t]',' ',respuesta_elegida)
				respuesta_elegida = self.escapeString(respuesta_elegida)

				# CHEQUEO QUE LA NOTICIA NO ESTE YA EN NUESTRA BASE DE DATOS...
				idDB = ''
				self.rows = self.seleccionar("SELECT cya_pregunta_id FROM cya_contenido_yahoo_answers WHERE cya_pregunta_id = '" + id + "'")
				for row in self.rows:
					idDB = row['cya_pregunta_id']

				# ...SI ESTA, NO LO AGREGA.
				if idDB <> id:
					# HAGO EL INSERT EN LA DB
					infoMeta = {
						'cya_asunto'			: "%s" % asunto,
						'cya_link'				: "%s" % link,
						'cya_descripcion'		: "%s" % desc,
						'cya_date'				: "%s" % date,
						'cya_respuesta_elegida'	: "%s" % respuesta_elegida
					}
					try:
						contenido = {
							'cya_pregunta_id' : "'%s'" % self.escapeString(id),
							'cya_fecha'			: "'%s'" % fecha,
							'cya_metadata'		: "'%s'" % json.dumps(infoMeta)
						}
						#self.insertar("cya_contenido_yahoo_answers",contenido)
						insert_id = self.agregarcontenido('cya_contenido_yahoo_answers', contenido)
						self.items_found = inc(self.items_found)
					except Exception , e:
						self.addmessage('Yahoo Answers error: %s(Palabra:%s)' % ( str(e),self.pal_palabra ))

			# Me voy!
			if self.items_found < int(self.config['cant_items']): self.requeue = True
			return True

		except Exception, e:
			self.addmessage('Yahooanswers error %s(Palabra:%s)' % ( str(e), self.pal_palabra) )
			return False

