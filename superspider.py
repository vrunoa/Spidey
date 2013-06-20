import twisted,sys,os,time,IPython
from twisted.internet.error import ConnectionRefusedError
from library import Dispatcher

def gospidey(w):
	import sys
	sys.path.append('/var/www/vrunoa/webspider/python')
	sys.path.append('/var/www/vrunoa/webspider/python/workers')
	try:
		X = __import__(str(w['tco_nombre']))
		worker = X.worker()
		result = worker.weave(w)
		del worker, X
	except Exception, error:
		result = {'flag':False,'messages':'Engine error: %s' % str(error)}
	return result

class DistributedSpider(Dispatcher):
	
	pendingResults, logfiles = [], []

	def init(self):
		from IPython.kernel.client import MultiEngineClient
		try:
			self.multiEngine = MultiEngineClient()
			self.multiEngine.reset()
			self.multiEngine.push_function(dict(f=gospidey))
			return True
		except twisted.internet.error.ConnectionRefusedError, e:
			print 'Waiting ipcontroller'
			return False
		except IPython.kernel.error.NoEnginesRegistered, e:
			print 'Waiting ipengines'
			return False
		except Exception, e:
			print str(e)
			self.logmessage('Superspider init except: type(%s) message(%s)' % (str(type(e)),str(e)))
			sys.exit(1)

	def run(self):
		try :
			target = self.getFreeEngine()
			if target is None: return True
			task   = self.gettask()
			if task == False: return True
			self.logmessage('new task: %s' % str(task))
			self.multiEngine.execute('y = f('+str(task)+')',targets=target,block=False)
#			print str(target) + '<--- target'
			pr = self.multiEngine.pull('y',targets=target,block=False)
			self.pendingResults.append({'pr':pr,'target':target,'task':task})
			self.getResults()
			return True
		except KeyboardInterrupt, e:
			self.logmessage('Superspider init except: type(%s) message(%s)' % (str(type(e)),str(e)))
			result = self.multiEngine.kill(controller=True)
			return False
		except IPython.kernel.error.CompositeError, e:
			print '\nCompositeError: %s\n\n' % str(e)
			return True
		except Exception, e:
			print str(e)
			return False

	def getResults(self):
		for pending in self.pendingResults:
			result = pending['pr'].get_result(block=False)
			if result is not None:
				print str(result) + '<--- result'
#				print pending
				self.pendingResults.remove(pending)
#				print str(len(self.pendingResults)) + '<--- pending results\n'
				try: self.logmessage(result[0]['messages'],pending['task']['tco_nombre'])
				except Exception, e: print e
				if result[0]['flag'] == False: self.taskfail(pending['task'])

	def logmessage(self, messages, plugin= 'superspider'):
		path = '/var/www/Ecomm/webspider/python/logs/%s/' % plugin
		if not os.path.exists(path): os.makedirs(path)
	
		from datetime import datetime
		strnow    = str(datetime.today().strftime("%Y-%m-%d"))
		filename  ='%s%s-%s.log' %(path,plugin,strnow)

		import logging
		logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s',filename = filename, datefmt='%y-%m-%d %H:%M:%S')
		logobj = None
		for logfile in self.logfiles:
			if logfile['filename'] == filename:
				logobj = logfile

		if logobj is None:
			logger  = logging.getLogger(plugin)
			logger.addHandler(logging.FileHandler(filename))
			logobj  = {
				'logger'   : logger,
				'filename' : filename				
			}
			self.logfiles.append(logobj)
#		print '%s <--- log files ' % str(len(self.logfiles))
		if isinstance(messages,list): 
			for msg in messages:	logobj['logger'].info(msg)
		else: logobj['logger'].info(messages)

	def getFreeEngine(self):
		for engine in self.multiEngine.queue_status():
			if engine[1]['pending'] == 'None':
				if len(engine[1]['queue']) == 0:
					return engine[0]
		return None


def main():
	spiderman = DistributedSpider()
	while spiderman.init() == False: 
		time.sleep(10)
	while spiderman.run() == True: 
		time.sleep(5)
	sys.exit()

if __name__ == '__main__':
	main()

