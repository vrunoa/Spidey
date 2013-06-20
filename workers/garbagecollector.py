from library import WorkerBase
class worker(WorkerBase):
	
	queue       = 'cpe_cola_pendiente'
	queue_retry = 'cre_cola_reintento'
	fec_field   = 'fecha'
	time        = 360 # in seconds

	def run(self):
		query   = "SELECT * FROM %s WHERE time_to_sec(timediff(now(),%s)) > %s" % (self.queue_retry,self.fec_field,self.time)
		garbage = self.seleccionar(query)
		if(len(garbage)==0): return {'flag':True,'message':'Retry queue is empty'} 
		from datetime import datetime
		values = []
		ids = []
		for row in garbage:
			fields = "("
			for col in row:
				if(col == "id"): ids.append(row[col])
				if(col == "fecha"): continue
				fields = "%s '%s'," % (fields,row[col])
			fields = "%s '%s')" % (fields,str(datetime.today().strftime("%y-%m-%d %H:%M:%S")))
			values.append(fields)
		fields = ",".join(row)
		try:
			query = "DELETE FROM %s WHERE id IN (%s)" %(self.queue_retry,",".join(ids))
			result = self.query(query)
			query = "INSERT INTO %s (%s) VALUES %s" % (self.queue_retry,fields,",".join(values))
			result = self.query(query)
		except BaseException as e:
			return {'flag':False,'message':str(e)}
		return {'flag':True,'message':'Garbage collector executed'}

