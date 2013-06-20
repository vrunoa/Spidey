from library import WorkerBase, iif, inc
import os,re,json
from time import strftime,gmtime

class worker(WorkerBase):
	
	def run(self):
		try:
			values,items_found,busq = [],0,re.sub('\s+','+',self.pal_palabra)
			url = 'http://api.ustream.tv/json/channel/all/search/title:like:%s?key=%s' % (busq,self.config['api_key'])
#			self.addmessage('URL Request: %s' % url)
			obj = self.readPage(url);
			obj = json.loads(obj)
			
			if obj['results'] is None:
				self.addmessage('Ustream no hay resultados para la url %s' % url  )
				return False

			for data in obj['results']:

				if items_found == int(self.config['cant_items']): return True

				url    = self.escapeString(str(data['url']))
				query  = "SELECT cus_id FROM cus_contenido_ustream WHERE cus_url = '%s'" % url	
				result = self.seleccionar(query)
				if len(result) > 0:
#					self.addmessage('El contenido ya se encuentra en la base de datos: %s' % url)
					continue
				embed = data['embedTag']
				embed = re.sub('"','\\\"', embed)
				embed = re.sub('/','\\\/', embed)
				data['embedTag'] = embed
				metadata = json.dumps(data)
				metadata = re.sub("\'+",'', metadata)	
				title    = self.escapeString(str(data['title']))
				try    : descrip  = self.escapeString(str(data['description']))
				except : pass
#				print metadata
				try :
					data = {
						'cus_fecha'   : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()), 
						'cus_titulo'  : "'%s'" % title, 
						'cus_url'     : "'%s'" % url, 
						'cus_metadata': "'%s'" % metadata,
						'cus_embed'   : "'%s'" % str(data['embedTag'])
					}	
					insert_id = self.agregarcontenido('cus_contenido_ustream', data)
					items_found = inc(items_found)
				except Exception, e:
					self.addmessage('Ustream error: %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )

			return True

		except Exception, e:
			self.addmessage('Ustream error %s(Palabra:%s)' % ( str(e),self.pal_palabra ) )
			return False
