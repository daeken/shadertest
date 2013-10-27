from handler import *
import random

@handler('runner')
def get_index():
	pass

@handler
def rpc_init(information):
	info = json.loads(information)

	if not 'id' in session:
		session['id'] = random.randrange(0x10000000)
		session['seen'] = []

	session['info'] = info

	if not Node.exists(session['id']):
		Node.create(session['id'], info)

@handler
def rpc_check():
	if not 'id' in session:
		return False

	Node.refresh(session['id'], session['info'])

	for shader in Shader.getAll(seen=session['seen']):
		return dict(id=shader.id, code=shader.code, uniforms=shader.uniforms)

	return None

@handler
def rpc_feedback(id, success, errors):
	session['seen'].append(id)
	Shader.addFeedback(int(id), session['info'], success == 'true', errors)
	session.modified = True
