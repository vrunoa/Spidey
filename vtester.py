import sys,os
sys.path.append('/var/www/vrunoa/webspider/python/workers')
w = {
	'tco_nombre' : 'abcnews',
	'tco_id'     : 22,
	'cat_id'     : 0,
	'pal_id'     : 4021,
	'pal_palabra': 'ferrari',
	'reintento'  : 0,
	'idi_id'     : 1,
	'fecha'      : '2009-07-10 09:37:00',
	'params'     : '{"page" : 0 ,"items_found" : 0}'
}
X = __import__(str(w['tco_nombre']))
worker = X.worker()
result = worker.weave(w)
print result
del worker, X
