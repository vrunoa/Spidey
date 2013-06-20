from library import Database
from library import Config
from datetime import datetime
from time import strftime
import os,sys
class GarbageCollector(Database):
	def run(self):
		try:
			svalues ,ids, ini = [],[],Config()
			tasks = self.seleccionar("SELECT * FROM cre_cola_reintento WHERE TIMEDIFF( NOW() , fecha ) > '%s';" % ini.getConfig('garbagecollector.time') )
			if len(tasks) == 0: 
				self.logger.info('No hay tareas en la cola de reintento')
				return
			for task in tasks:
				values = []
				ids.append("'%d'" % int(task['id']) )
				for field in task:
					if field == 'fecha': task[field] = str( datetime.today().strftime("%Y-%m-%d %H:%M:%S") ) 
					values.append("'%s'" % task[field])
				svalues.append("( %s )" % ','.join(values))
			self.query( "INSERT INTO cpe_cola_pendiente(%s) VALUES % s"   % ( ','.join(task) , ','.join(svalues) ) )
			self.query( "DELETE FROM cre_cola_reintento WHERE id IN (%s)" % ','.join(ids) )
			self.logger.info('Se han movido %d tareas a la cola de pendientes' % len(tasks) )
		except Exception, e:
			self.logger.info('Garbage collector exception: %s' % str(e) )
		sys.exit(1)

	def createLogger(self):
		path = '/var/www/vrunoa/webspider/python/logs/garbagecollector/'
		if not os.path.exists(path): os.makedirs(path)
		from datetime import datetime
		strnow    = str(datetime.today().strftime("%Y-%m-%d"))
		filename  ='%s%s-%s.log' %(path,'garbagecollector',strnow)
		import logging
		logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%y-%m-%d %H:%M:%S',filename=filename,filemode='a+')
		self.logger = logging.getLogger('garbagecollector')

def main():
	collector = GarbageCollector()
	collector.createLogger()
	collector.run()

if __name__ == '__main__':
	main()

