from library import WorkerBase
import re
from time import strftime,gmtime

class worker(WorkerBase):

	def run(self):
		try:
			palabra = self.seleccionar("SELECT * FROM pal_palabra WHERE pal_id = %d" % self.pal_id)
			if len(palabra) == 0:
				self.addmessage('Google related error: La palabra(%s) no esta en pal_palabra' % self.pal_palabra)
				return False
			
			palabra    = palabra[0]
			relaciones = self.seleccionar("SELECT * FROM rel_relaciones WHERE pal_id = %d" % self.pal_id )
			if len(relaciones) == 0:

				self.addmessage('Google Related error: La Palabra(%s) no tiene relaicones asignadas' % palabra['pal_palabra'] )

				self.punish(palabra['pal_id'])
				return False
			
			relaciones = relaciones[0]
			if int(relaciones['rel_nivel_profundidad']) == 3:
				self.addmessage('Google Related: La Palabra(%s) ha alcanzado el nivel de profundidad' % palabra['pal_palabra'])
				return False
			
			if relaciones['rel_plugins'] is None or relaciones['rel_plugins'] == '':
				self.addmessage('Google Related error: La palabra(%s) no tiene plugin asignados' % palabra['pal_palabra'] )
				return False

			lang  = self.getLanguage()
			busq  = re.sub('\s+','+',palabra['pal_palabra'])
			url   = 'http://www.google.com.ar/search?q=%s&hl=%s'	% (busq,lang)
			html = self.readPage(url)
			html = re.sub('\s+',' ',html)
			regexp = '<a href="/search[\/\w\.\?\&-=;]+broad-revision[\/\w\.\?\&-=;]+">\s*'
			regexp = '%s[\w\s<\/?b>]+\s*</a>\s*' % regexp
			result = re.finditer(regexp,html)
			if result is None:
				self.addmessage('Google Related : La Palabra(%s) no tiene palabras relacionadas' % palabra['pal_palabra'])
				return False
			
			plugins = self.seleccionar('SELECT * FROM tco_tipo_contenido WHERE tco_id IN (%s) OR tco_nombre = "googlerelated"' % re.sub(':',',',relaciones['rel_plugins']))
			found = 0

			for pal in result:
				pal = pal.group(0)
				pal = re.search('>[\w\s<\/?b>]+<',pal)
				pal = pal.group(0)
				pal = re.sub('</?b>','',pal)
				pal = re.sub('<','',pal)
				pal = re.sub('>','',pal)
				exists = self.seleccionar("SELECT * FROM pal_palabra WHERE pal_palabra = '%s' and idi_id = %d" % ( self.escapeString(str(pal)), int(palabra['idi_id']) ) )
				if len(exists) > 0 :
					self.addmessage('Google related: La Palabra(%s) relacionada ya se encuentra en nuestra lista' % pal )
					continue

				data = {
					'pal_palabra'  : "'%s'"    % self.escapeString(str(pal)),
					'idi_id'       : "'%s'"    % int(palabra['idi_id']),
					'pal_dominio'  : "'%s'"    % re.sub('/$','',palabra['pal_dominio']),
					'pal_ruta'     : "'%s/%s'" % (re.sub('/$','',palabra['pal_ruta']) , re.sub('\s+','-',self.escapeString(str(pal)))),
					'pal_amigable' : "'%s'"    % re.sub('\s+','-',pal)
				}
#				print data
				id = self.insertar('pal_palabra',data)
				data = {
					'rel_palabra_padre'     : "'%s'" % palabra['pal_id'],
					'pal_id'                : "'%s'" % id,
					'rel_nivel_profundidad' : "'%s'" % str( int( relaciones['rel_nivel_profundidad'] ) + 1 ),
					'rel_plugins'           : "'%s'" % relaciones['rel_plugins']
				}
#				print data
				self.insertar('rel_relaciones',data)
				for plugin in plugins:
					data = {
						'tco_id'      : "'%s'" % plugin['tco_id'],
						'cat_id'      : "'%s'" % palabra['pal_id'],
						'pal_palabra' : "'%s'" % pal,
						'tco_nombre'  : "'%s'" % plugin['tco_nombre'],
						'reintento'   : "'%s'" % '0',
						'fecha'       : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'idi_id'      : "'%s'" % palabra['idi_id'],
						'pal_id'      : "'%s'" % id
					}
					self.insertar('cpe_cola_pendiente',data)
				found = found + 1

			return True

		except Exception, e:
			self.addmessage('Google Related error: %s' % str(e))
			return False

