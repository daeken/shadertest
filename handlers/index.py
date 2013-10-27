from handler import *

@handler('index')
def get_index():
	return dict(nodes=Node.count())

@handler('progress')
def get_progress(id):
	return dict(feedback=Shader.getFeedback(id))
