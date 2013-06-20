# inlineif implementation ---
def iif(condition, resulttrue, resultfalse):
	if condition: return resulttrue
	else        : return resultfalse

# --- inlineif implementation

# incr implementation ---
def inc(value, step = 1):
	return value + step

# --- incr implementation

class Config():

	def __init__(self, nivel='production'):
		from ConfigParser import ConfigParser
		import sys
		try:
			self.cp = ConfigParser()
			self.nivel	= nivel
			self.cp.read('/var/www/vrunoa/webspider/python/application.ini')
		except Exception, e:
			print "\n\nError: %s" % str(e)
			sys.exit (1)

	def getConfig(self, llave):
		try:
			return self.cp.get(self.nivel, llave)
		except ConfigParser.Error, e:
			print "\n\nError: %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)


# email implementation ---
class MailSender():

	_from, _to, _subject, _msg, _smtp = '', [], '', None, None

	def clear(self):
		self._from = ''
		self._to = []
		self._subject = ''
		self._msg = None
	
	def validateMail(self, mail):
		import re
		from library import iif
		regex_mail = re.compile(r"(?:^|\s)[-a-z0-9_.\+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
		return iif(re.match(regex_mail, mail), True, None)	

	def setBody(self, body):
		from email.mime.text import MIMEText
		self._msg = MIMEText(body)

	def setFrom(self, _from):
		if(self.validateMail(_from) is None): raise Exception('MailSender.setFrom: _from param is not a valid email --> %s' % _from)
		self._from = _from

	def setTo(self, _to):
		if(self.validateMail(_to) is None): raise Exception('MailSender.setTo: _to param is not a valid email --> %s' % _to)
		self._to.append(_to)

	def setSubject(self, _subject):
		self._subject = _subject

	def opensmtp(self):
		import smtplib
		self._smtp = smtplib.SMTP('localhost')

	def send(self):
		if self._msg is None: raise Exception('MailSender.send: mail body not set')
		if self._smtp is None: self.opensmtp()
		self._msg['Subject'] = self._subject
		self._msg['From']    = self._from
		self._msg['To']      = ', '.join(self._to)
		self._smtp.sendmail(self._from, self._to, self._msg.as_string())
		
	def __del__(self):
		self._smtp.quit()

# --- email implementation

# database connection ---
import MySQLdb
class Database():

	def __init__(self):
#		self.config = Config()
#		host	 = self.config.getConfig('resources.db.params.host')
#		user	 = self.config.getConfig('resources.db.params.username')
#		passwd = self.config.getConfig('resources.db.params.password')
#		db		 = self.config.getConfig('resources.db.params.dbname')
		host, user, passwd, db = "localhost", "root", "password", "dbname"
		self.conn = MySQLdb.connect (host = host, user = user, passwd = passwd, db = db)

	def __del__(self):
		self.conn.close()

	def seleccionar(self, query):
		self.cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
		self.cursor.execute (query)
		return self.cursor.fetchall()

	def insertar(self, tabla, query_param):
		self.cursor = self.conn.cursor()
		self.items  = query_param.items()
		self.keys   = [item[0] for item in self.items]
		self.values = [item[1] for item in self.items]
		self.sql = "INSERT INTO %s (%s) values (%s)" % (tabla, ", ".join(self.keys), ", ".join(self.values))
#		print self.sql
		self.cursor.execute(self.sql)
		return self.conn.insert_id()
	
	def query(self,query):
		self.cursor = self.conn.cursor()
		self.cursor.execute(query)

	def escapeHTML(self, fuente):
		from BeautifulSoup import BeautifulStoneSoup
		fuente = unicode( BeautifulStoneSoup( fuente, convertEntities= BeautifulStoneSoup.HTML_ENTITIES) )
		return fuente 

	def escapeUnicode(self, cadena):
		vec = {
			'0421' : '&#1057;',
			'00a0' : '&nbsp;', 
			'00A1' : '&iexcl;',	
			'00A2' : '&cent;', '00A3' : '&pound;',	'00A4' : '&curren;',	'00A5' : '&yen;',	
			'00A7' : '&sect;',
			'00A8' : '&uml;',
			'00A9' : '&copy;',
			'00AA' : '&ordf;',
			'00AB' : '&laquo;',
			'00AC' : '&not;',
			'00AE' : '&reg;',
			'00AF' : '&macr;',
			'00B0' : '&deg;',	
			'00B1' : '&plusmn;',
			'00B4' : '&acute;',
			'00B5' : '&micro;',
			'00B6' : '&para;', 
			'00B7' : '&middot;',
			'00B8' : '&bedil;', 
			'00BA' : '&ordm;', 
			'00BB' : '&raquo;',	
			'00BF' : '&iquest;',
			'00C0' : '&Agrave;',	'00C1' : '&Aacute;',	'00C2' : '&Acirc;','00C3' : '&Atilde;', '00C4' : '&Auml;','00C5' : '&Aring;','00C6' : '&AElig;',	
			'00C7' : '&Ccedil;',
			'00C8' : '&Egrave;',	'00C9' : '&Eacute;',	'00CA' : '&Ecirc;','00CB' : '&Euml;',
			'00CC' : '&Igrave;',	'00CD' : '&Iacute;',	'00CE' : '&Icirc;','00CF' : '&Iuml;',
			'00D1' : '&Ntilde;',	
			'00D2' : '&Ograve;',	'00D3' : '&Oacute;', '00D4' : '&Ocirc;', '00D5' : '&Otilde;', '00D6' : '&Ouml;', '00D8' : '&Oslash;',
			'00D9' : '&Ugrave;',	'00DA' : '&Uacute;',	'00DB' : '&Ucirc;','00DC' : '&Uuml;',
			'00DF' : '&szlig;',
			'00E0' : '&agrave;',	'00E1' : '&aacute;',	'00E2' : '&acirc;','00E3' : '&atilde;', '00E4' : '&auml;','00E5' : '&aring;','00E6' : '&aElig;',	
			'00E7' : '&ccedil;',
			'00E8' : '&egrave;',	'00E9' : '&eacute;',	'00EA' : '&ecirc;','00EB' : '&euml;',
			'00EC' : '&igrave;',	'00ED' : '&iacute;',	'00EE' : '&icirc;','00EF' : '&iuml;',
			'00F1' : '&ntilde;',	
			'00F2' : '&ograve;',	'00F3' : '&oacute;', '00F4' : '&ocirc;', '00F5' : '&otilde;', '00F6' : '&ouml;', '00F8' : '&oslash;',
			'00F7' : '&divide;',
			'00F9' : '&ugrave;',	'00FA' : '&uacute;',	'00FB' : '&ucirc;','00FC' : '&uuml;',
			'00FF' : '&yuml;',
			'20AB' : '&dong;'
		}	
		import re
		regex  = re.compile(r"\\r\\n", re.IGNORECASE)
		fuente = re.sub(regex, '&nbsp;', cadena)
		for code in vec:
			regex  = re.compile(r"\\\u%s" % code, re.IGNORECASE)
			fuente = re.sub(regex, vec[code], fuente)
		return fuente	

	
	def escapeUnicodeX(self, cadena):
		fuente = cadena
		vec = {
			'\xbb' : '&raquo;'
		}		
		import re		
		for code in vec:
			regex  = re.compile(r"%s" % code, re.IGNORECASE)
			fuente = re.sub(regex, vec[code], fuente)

		return fuente	

	def escapeString(self, data, noescape = [] ):
		import re

		if isinstance(data, dict):
			for key in data:
				val = str(data[key])
				val = re.sub("'+",'',val)
				val = re.sub('"+','',val)
				if key not in noescape: val = MySQLdb.escape_string(val)
				data[key] = "'%s'" % val
			return data

		try:
			data = str(data)
			data = re.sub("'+",'',data)
			data = re.sub('"+','',data)
			return MySQLdb.escape_string(data)
		except Exception ,e:
			print e
			return ''

# --- database connection

# dispatcher ---
class Dispatcher(Database):
	
	tries = 5
	tasksWorking = []
	
	def getReadyQueue(self):
		sql = "SELECT queue_wait('cpe_cola_pendiente', 'cac_cola_actualizacion', 10) as queue_key;"
		row = self.seleccionar(sql)
		queue = row[0]['queue_key']
		if queue == 1: return 'cpe_cola_pendiente'
		elif queue == 2: return 'cac_cola_actualizacion'
		return None		
		

	def gettask(self):
		queue = self.getReadyQueue()
		if queue is None: return False
		#sql = "SELECT * FROM cpe_cola_pendiente WHERE queue_wait('%s');" % queue
		sql = "SELECT * FROM %s LIMIT 1;" % queue
		row = self.seleccionar(sql)
		try    : 
			task = row[0]
			task['fecha'] = str(task['fecha'])
		except : task = False
		self.deltask()
		return task
	
	def deltask(self):
		sql = "SELECT queue_end();"		
		self.seleccionar(sql)

	def taskfail(self,task):
		from datetime import datetime
		from time import strftime
		try    : del task['fecha']
		except : pass
		sql = " INSERT INTO "
		if(int(task['reintento']) <= 5):
			task['reintento'] = int(task['reintento']) + 1
			cola = 'cre_cola_reintento'
		else:
			del task['reintento']
			cola = 'cfa_cola_fallida'
		sql = "%s %s SET " % ( sql , cola )
		for field in task:
			if(field=="id"): continue
			sql = "%s %s = '%s'," % (sql,field,task[field])
		sql = "%s fecha = '%s';" % (sql,str(datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
		self.query(sql)

	def findworkingtask(self,client):
		i = 0
		while i < len(self.tasksWorking):
			if(self.tasksWorking[i]['client'] == client):
				return i
			i = i + 1
		return -1

# --- dispatcher

# worker base ---
class WorkerBase(Database):
	
	def addmessage(self,message):
		import re,os
		from datetime import datetime
		log_id  = "%s" %(re.sub('\s+','+',self.pal_palabra))
		strnow  = str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
		message = "[%s][%s][%s] %s" %(os.getpid(),strnow,str(log_id),str(message))
		self.messages.append(message)
		
		"""
		-------> arreglar para que logueo a travez de una conexion al server <-------
		try    : self.logger.info(message)
		except : 
			import logging
#			esta linea la modifico (Elias)
#			logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%y-%m-%d %H:%M:%S',filename=filename,filemode='w')
			logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%y-%m-%d %H:%M:%S')
			self.logger = logging.getLogger(self.tco_nombre)

#			Estas dos [aniado el file handler al logger] (Elias)
#			handlers = self.handlers.Keys()
			##if not self.tco_nombre in handlers:
				##hand = loggin.FileHandler(filename, 'a')
				##self.handlers[self.tco_nombre] = hand

			self.handlerArchivo = logging.FileHandler(filename, 'a')
			##self.handlerArchivo = self.handlers[self.tco_nombre]
			self.logger.addHandler(self.handlerArchivo)
			self.logger.info(message)

#		logger.removeHandler(handlerArchivo);
#		logging.shutdown()
#		del logging
#		del logger	
		"""

	def weave(self, data):
		if self.init(data) == True: self.success = self.run()
		return self.rest()
	
	def init(self, data):
		self.messages, self.params, self.success, self.data, self.requeue = [], {}, False, data, False
		self.cat_id       = int(data['cat_id'])
		self.pal_palabra  = str(data['pal_palabra']) 
		self.pal_id       = int(data['pal_id'])
		self.idi_id       = int(data['idi_id'])
		self.tco_id       = int(data['tco_id'])
		self.tco_nombre   = str(data['tco_nombre'])
		self.reintento    = int(data['reintento'])
		self.fecha        = str(data['fecha'])
		self.params       = str(data['params'])
		self.mailsender   = None
		import json
		try    :	self.params = json.loads(self.params)
		except : self.params = {}
		try    : self.page   = int(self.params['page'])
		except : self.page   = 0
		try    : self.items_found = int(self.params['items_found'])
		except : self.items_found = 0

		if self.page >= 25:
			self.highPaggingMail()
			self.addmessage('High Pagging level: %s' % self.tco_nombre)
			return False
	
		config = self.getConfig()
		if config == False:
			self.addmessage('No config file found: %s' % self.tco_nombre)
			return False
	
		if config['habilitado'] != 1:
			self.addmessage('Plugin deshabilitado: %s' % self.tco_nombre)
			return False
		
		self.config = config
		return True

	def sendDebugMail(self, body, subject):
		if self.mailsender is None: self.mailsender = MailSender()
		self.mailsender.setBody(body)
		self.mailsender.setSubject(subject)
		self.mailsender.setFrom('debug@webspider.com')
		self.mailsender.setTo('brunotrs+spider@gmail.com')
		self.mailsender.setTo('iamnotspiderman@gmail.com')
		self.mailsender.setTo('ebadenes+spider@e-commfactory.com')
		self.mailsender.send()
		self.mailsender.clear()


	def highPaggingMail(self):
		from datetime import datetime
		from time import strftime
		import json
		date = str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
		body = "Plugin: %s\r\nFecha: %s\r\nPalabra: %s\r\n" %(self.tco_nombre, date, self.pal_palabra)
		self.sendDebugMail(body, 'High pagging debug level')
			
	def punish(self, pal_id):
		sql = "UPDATE pal_palabra SET pal_estado = 0 WHERE pal_id = %d" % int(pal_id)
#		print sql
		self.query(sql)
		sql = "DELETE FROM cpe_cola_pendiente WHERE pal_id = %d" % int(pal_id)
#		print sql
		sql.query(sql)
		from datetime import datetime
		from time import strftime
		date = str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
		body = "Plugin: %s\r\nFecha: %s\r\nPalabra: %s\r\n" %(self.tco_nombre, date, self.pal_palabra)
		self.sendDebugMail(body, 'Palabra sin relacionados')
	
	def rest(self):
		self.success  = iif(self.success == True, True, False)
		self.messages = iif(isinstance(self.messages,list), self.messages, [])
		if self.requeue == True: self.queue()
		return {'flag': self.success, 'messages': self.messages}

	def queue(self):
		import json
		self.params['page'] = self.page + 1
		self.params['items_found'] = self.items_found
		self.data['params'] = json.dumps(self.params)
#		print self.data
		self.data = self.escapeString(self.data, noescape = ['params'])
		self.insertar('cpe_cola_pendiente', self.data)


	def setEncoding(self, type = None):
		if type is None: type = 'utf8'	
		import sys
		if sys.getdefaultencoding == type: return
		reload(sys)
		sys.setdefaultencoding	
		sys.setdefaultencoding(type)	


	def readPage(self, url, code = 'utf8'):
		import urllib
		opener = PickPocketOpener()
		page   = opener.open(str(url))

		fuente = page.read()
#		fuente = self.escapeHTML(fuente)
		if code != False:
			fuente =	self.escapeUnicode(fuente)
			self.setEncoding(code)
			fuente = fuente.decode(code)

		return fuente

	def getSourceAsDOM(self,source,isURL = True):
		import urllib
		from xml.dom import minidom
		if isURL == True:
			self.xmlfile = urllib.urlopen(source)
			self.dom = minidom.parse(self.xmlfile)
		else:
			self.dom = minidom.parseString(source)
		return self.dom

	def normalizar(self,cadena):
		cadena = unicode(cadena,'utf-8')
		return normalize('NFKD',cadena).encode('ASCII', 'ignore').lower()


	def getConfig(self):
		import json
		sql = "SELECT tco_habilitado,tco_configuracion FROM tco_tipo_contenido WHERE tco_id = %d " % int(self.tco_id)
		row = self.seleccionar(sql)
		try : 
			config = row[0]['tco_configuracion']
			if config != '': config = json.loads(config)
			else: config = {}
			config['habilitado'] = row[0]['tco_habilitado']
			return config
		except Exception, e: 
			self.addmessage('%s Plugin config error: %s' % (self.tco_nombre,str(e)))
		
		sql = "SELECT cde_configuracion FROM cde_configuracion_default"
		row = self.seleccionar(sql)
		try : return json.loads(row[0]['cde_configuracion'])
		except Exception, e: 
			self.addmessage('Exception while getting plugin default configuration: %s' % str(e))
			return False

	def getRemoteFile(self, dominio, path, isImage = True):
		import httplib,re
		try:
			conn = httplib.HTTPConnection(dominio)
			conn.request ("GET", path)
			resp = conn.getresponse()
			file = resp.read()
			if isImage != True: return	file
			import imghdr
			if imghdr.what('',file[0:32]) is not None: return file
			if re.match('image',resp.getheader('content-type')) is not None: return File
			return None
		except Exception, e: return None

	def saveFile(self,path,bin):
		try:
			fichero = file(path,'wb')
			fichero.write(bin)
			fichero.close()
		except Exception, error:
			return None

	def getLanguage(self):
		self.lang = 'en'
		self.row = self.seleccionar("select idi_iso from idi_idioma where idi_id = '%d'" % self.idi_id)
		if self.cursor.rowcount > 0:
			self.lang = self.row[0]['idi_iso']
		return self.lang

	def relacionarConPalabra(self,idcontenido):
		sql = "INSERT INTO pac_palabra_contenido (pac_fecha,pac_idcontenido,pal_id,tco_id) VAlUES (NOW(),'%s','%s','%s') " % (int(idcontenido),self.pal_id,self.tco_id)
		self.query(sql)

	def agregarcontenido(self, table, data):
		data['pal_id'] = " %d " % int(self.pal_id)
		insert_id      = self.insertar(table, data)
		self.relacionarConPalabra(insert_id)
		return insert_id

# --- worker base 

# url opener ---
from urllib import FancyURLopener
class PickPocketOpener(FancyURLopener):
	user_agent = []
	user_agent.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; es-ES; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11')
	user_agent.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; es-ES; rv:1.8.1.20) Gecko/20081217 Firefox/2.0.0.20')
	user_agent.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; es-ES; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')
	user_agent.append('Opera/9.80 (Windows NT 5.1; U; es-ES) Presto/2.2.15 Version/10.00')
	user_agent.append('Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; es-es) AppleWebKit/531.9 (KHTML, like Gecko) Version/4.0.3 Safari/531.9')
	user_agent.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.21 Safari/532.0')
	user_agent.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; es-ES) AppleWebKit/528.16 (KHTML, like Gecko) version/4.0 Safari/528.16')
	user_agent.append('Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)')
	user_agent.append('Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')
	user_agent.append('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; yie8)')
	user_agent.append('Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.204.0 Safari/532.0')
	user_agent.append('Mozilla/5.0 (X11; U; Linux i686; es-AR; rv:1.9.0.14) Gecko/2009090216 Ubuntu/9.04 (jaunty) Firefox/3.0.14')
	user_agent.append('Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.2 Safari/532.0')
	import random
	version = str(random.sample(user_agent,1)[0]) 

# --- url opener
