import redis

connection = redis.StrictRedis(host='localhost', port=6379, db=0)

class Node(object):
	def __init__(self, id, info):
		self.id, self.info = id, info

	@staticmethod
	def exists(id):
		return connection.hget('node:%i' % id, 'info') != None

	@staticmethod
	def create(id, info):
		connection.hset('node:%i' % id, 'info', info)
		connection.expire('node:%i' % id, 5*60)

	@staticmethod
	def get(id):
		hash = connection.hgetall('node:%i' % id)
		return Node(id=id, info=eval(hash['info']))

	@staticmethod
	def count():
		return len(connection.keys('node:*'))

	@staticmethod
	def refresh(id, info):
		if Node.exists(id):
			connection.expire('node:%i' % id, 5*60)
		else:
			Node.create(id, info)

class Shader(object):
	def __init__(self, id, code, uniforms):
		self.id, self.code, self.uniforms = id, code, uniforms

	@staticmethod
	def create(id, code, uniforms):
		connection.hset('shader:%i' % id, 'code', code)
		connection.hset('shader:%i' % id, 'uniforms', uniforms)
		connection.expire('shader:%i' % id, 120*60)

	@staticmethod
	def getAll(seen=[]):
		shaders = []
		for key in connection.keys('shader:*'):
			id = key.split(':')[1]
			if id not in seen:
				hash = connection.hgetall(key)
				shaders.append(Shader(id, hash['code'], eval(hash['uniforms'])))
		return shaders

	@staticmethod
	def addFeedback(id, info, success, errors):
		connection.rpush('feedback:%i' % id, (info, success, errors))
		connection.expire('feedback:%i' % id, 120*60)

	@staticmethod
	def getFeedback(id):
		return map(eval, connection.lrange('feedback:%i' % id, 0, -1))