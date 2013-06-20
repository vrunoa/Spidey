from library import WorkerBase
import os,json,re,imghdr,md5,random
from time import strftime,gmtime

class worker(WorkerBase):

	def run(self):
		try:
			values,items_found = [],0
			url = 'http://api.justin.tv/api/stream/list.json' 
			print url
#			print url
#			self.addmessage('URL Request: %s' % url)
			
			_json  = self.readPage('http://api.justin.tv/api/stream/list.json')
			_json  = json.loads(_json)
			path  = '%s/%s/' % (self.config['images_path'],strftime("%Y/%m/%d",gmtime()))
			if not os.path.exists(path):	os.makedirs(path)
			
			for stream in _json:

				if items_found == int(self.config['cant_items']): return True
				
				if self.matchs(stream,re.sub('\s+','+',self.pal_palabra)) == False: continue
				rows = self.seleccionar("SELECT cjv_id FROM cjv_contenido_justintv WHERE cjv_url = '%s'" % self.escapeString(str(stream['channel']['channel_url'])))
				if len(rows) > 0:
#					self.addmessage('El Stream ya se encuentra en la base de datos')
					continue

				try   : lang = stream['language']
				except: continue

				if lang != self.getLanguage(): continue
	
				channel = {}
				try    : channel['subcategory_title'] = stream['channel']['subcategory_title']
				except : pass
				try    : channel['tags'] = stream['channel']['tags']
				except : pass
				try    : channel['channel_url'] = stream['channel']['channel_url']
				except : pass
				try    : channel['login'] = stream['channel']['login']
				except : pass
				try    : channel['languaje'] = stream['channel']['languaje']
				except : pass
				try    : channel['title'] = stream['channel']['title']
				except : pass
				
				meta = {}
				try    : meta['name'] = stream['name']		
				except : pass
				try    :	meta['category'] = stream['category']		
				except : pass
				try    : meta['subcategory'] = stream['subctegory']
				except :	pass
				try    :	meta['title'] = stream['title']
				except : meta['title'] = ''

				try    : meta['stream_type'] = stream['stream_type']
				except : pass
				try    : meta['video_width'] = stream['video_width']
				except : pass
				try    : meta['video_height'] = stream['video_height']
				except : pass
				try    : meta['channel'] = channel	
				except : pass
			 
				src       = stream['channel']['screen_cap_url_large']
				domain    = re.search('http://(\w|\.|\-)+',src)
				domain    = domain.group(0)
				domain    = re.sub('http://','',domain)
				imageBIN  = self.getRemoteFile(str(domain),src)

				imageName = ''
				if imageBIN is not None:
					imageType = imghdr.what(None,imageBIN[0:32])
					if imageType is None: imageType = 'png'
#						self.addmessage('El thumbnail del canal no es una imagen: %s' % src)
#						imageBIN = False
#					else:
					md5File = md5.new(imageBIN).hexdigest()
					imageName = "%s" % md5.new(self.pal_palabra+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cjv_contenido_justintv").hexdigest()
					imagePath = path+imageName+'.'+imageType
					while os.path.isfile(imagePath) == True:
						imageName = "%s" % md5.new(self.pal_palabra+strftime('%Y%m%d%H%M%S',gmtime())+str(random.random())+"cjv_contenido_justintv").hexdigest()
						imagePath = path+imageName+'.'+imageType
							
				meta['image_path'] = imageName + '.' + imageType
				try :
					data = {
						'cjv_fecha'       : "'%s'" % strftime('%Y-%m-%d %H:%M:%S',gmtime()),
						'cjv_url'         : "'%s'" % self.escapeString(str(channel['channel_url'])),
						'cjv_thumb'       : "'%s'" % imageName,
						'cjv_titulo'      : "'%s'" % meta['title'], 
						'cjv_metadata'    : "'%s'" % re.sub("\'",'',json.dumps(meta))),
						'cjv_embed'       : "''"
					}
#					print data
					insert_id = self.agregarcontenido('cjv_contenido_justintv', data)
					if imageBIN is not None: self.saveFile(imagePath,imageBIN)
					items_found = items_found + 1
				except Exception , e:
					self.addmessage('Justintv error: %s(Palabra:%s)' %  ( str(e), self.pal_palabra) )

			return True

		except Exception,e:
			self.addmessage('Justin error %s(Palabra:%s)' % ( str(e), self.pal_palabra ) )
			return False

	def matchs(self,stream,busq):
		word = re.sub('\+',' ', busq)
#		for word in re.split('[\s\+]+', busq):
		try    : match = re.search(word,stream['title'],re.IGNORECASE)
		except : match = None
		if match is not None: return True
		try    : match = re.search(word,stream['channel']['title'],re.IGNORECASE)
		except : match = None
		if match is not None: return True
		try    : match = re.search(word,stream['channel']['login'],re.IGNORECASE)
		except : match = None
		if match is not None: return True
		try    : match = re.search(word,stream['channel']['tags'],re.IGNORECASE)
		except : match = None
		if match is not None: return True
		try    : match = re.search(word,stream['category'],re.IGNORECASE)
		except : match = None
		if match is not None: return True
		try    : match = re.search(word,stream['subcategory'],re.IGNORECASE)
		except : match = None
		if match is not None: return True
		return False
	
