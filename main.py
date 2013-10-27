import os
from flask import Flask, request
import handler
import handlers
from handlers import *

app = Flask(__name__)
app.debug = True
if os.path.exists('secret_key'):
	app.secret_key = file('secret_key', 'r').read()
else:
	import random
	app.secret_key = ''.join('%02x' % random.randrange(256) for i in xrange(16))
	with file('secret_key', 'w') as fp:
		fp.write(app.secret_key)

def reroute(noId, withId):
	def sub(id=None, *args, **kwargs):
		try:
			if id == None:
				return noId(*args, **kwargs)
			else:
				return withId(id, *args, **kwargs)
		except:
			import traceback
			traceback.print_exc()
	sub.func_name = '__reroute_' + noId.func_name
	return sub

for module, sub in handler.all.items():
	for name, (method, args, rpc, (noId, withId)) in sub.items():
		if module == 'index':
			route = '/'
			trailing = True
		else:
			route = '/%s' % module
			trailing = False
		if name != 'index':
			if not trailing:
				route += '/'
			route += '%s' % name
			trailing = False

		if noId != None and withId != None:
			func = reroute(noId, withId)
		elif noId != None:
			func = noId
		else:
			func = withId

		if withId != None:
			iroute = route
			if not trailing:
				iroute += '/'
			iroute += '<int:id>'
			app.route(iroute, methods=[method])(func)

		if noId != None:
			app.route(route, methods=[method])(func)

@app.route('/favicon.ico')
def favicon():
	return file('static/favicon.png', 'rb').read()

rpcStubTemplate = '''%s: function(%scallback) {
	$.ajax(%r, 
		{
			success: function(data) {
				if(callback !== undefined)
					callback(data)
			}, 
			error: function() {
				if(callback !== undefined)
					callback()
			}, 
			dataType: 'json', 
			data: {csrf: $csrf%s}, 
			type: 'POST'
		}
	)
}'''
cachedRpc = None
@app.route('/rpc.js')
def rpc():
	global cachedRpc
	if cachedRpc:
		return cachedRpc

	modules = []
	for module, sub in handler.all.items():
		module = [module]
		for name, (method, args, rpc, funcs) in sub.items():
			if not rpc:
				continue
			func = funcs[0] if funcs[0] else funcs[1]
			name = name[4:]
			method = rpcStubTemplate % (
					name, (', '.join(args) + ', ') if len(args) > 0 else '', 
					func.url(), 
					(', ' + ', '.join('%s: %s' % (arg, arg) for arg in args)) if len(args) > 0 else ''
				)
			module.append(method)
		if len(module) > 1:
			modules.append(module)

	cachedRpc = 'var $rpc = {%s};' % (', '.join('%s: {%s}' % (module[0], ', '.join(module[1:])) for module in modules))
	return cachedRpc

@app.route('/scripts/<fn>')
def script(fn):
	try:
		if not fn.endswith('.js'):
			return ''

		fn = 'scripts/' + fn[:-3]
		if os.path.exists(fn + '.js'):
			return file(fn + '.js', 'rb').read()
		return ''
	except:
		import traceback
		traceback.print_exc()

if __name__=='__main__':
	app.run(host='')
