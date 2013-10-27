from handler import *
import random

@handler(CSRFable=True)
def rpc_enqueue(code):
	id = random.randrange(0x10000000)
	Shader.create(id, code, dict(
		iResolution='vec3 resolution', 
		iGlobalTime='float time_seconds', 
		iChannel0='sampler2D texture', 
		iChannel1='sampler2D texture', 
		iChannel2='sampler2D texture', 
		iChannel3='sampler2D texture', 
	))
	return id
