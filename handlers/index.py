from handler import *

@handler('index')
def get_index(error=None):
	return dict(error=error, nodes=Node.count())

@handler('progress')
def get_progress(id):
	if not Shader.exists(id):
		redirect(get_index.url(error='Shader expired'))
	return dict(feedback=Shader.getFeedback(id))

@handler('nodes')
def get_nodes():
	return dict(nodes=Node.getAll())
