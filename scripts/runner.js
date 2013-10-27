function status(message, color) {
	color = color === undefined ? 'black' : color;

	$('#status').text(message).css('color', color);

	return false;
}

function initGL() {
	$('#runner').children().remove();

	$('#runner').append('<canvas id="cvs" width="320" height="240">');

	var cvs = $('#cvs')[0];
	var ctx = cvs.getContext('webgl') || cvs.getContext('experimental-webgl');

	return ctx;
}

var gl;

function glInfo() {
	gl = initGL();
	if(gl === null)
		return false;
	var info = {
		ua: navigator.userAgent, 
		extensions: gl.getSupportedExtensions(), 
		renderer: $.cookie('gpu')
	};
	return JSON.stringify(info);
}

function saveInfo() {
	var renderer = $('#renderer').val();
	if(renderer == '')
		return alert('Must enter a renderer string.');
	$.cookie('gpu', renderer, { expires: 365 * 10 });
	$('#gpuInfo').hide();
	sendInfo();
}

function pollServer() {
	$rpc.runner.check(function(ret) {
		console.log()
		if(ret === false)
			return location.reload();

		if(ret !== null && currentShader != ret.id)
			runShader(ret);
	})
}

var vsSource = [
	"attribute vec2 pos;",
	"void main()",
	"{",
	"gl_Position = vec4(pos.x,pos.y,0.0,1.0);",
	"}"
].join("\n");

function errorShader(shader, error) {
	completeShader(shader, false, error)
	return false;
}

function compile(shader) {
	var header = 'precision highp float;\n';
	for(var name in shader.uniforms) {
		var arr = shader.uniforms[name].split(' ');
		header += 'uniform ' + arr[0] + ' ' + name + ';\n';
	}

	var vs = gl.createShader(gl.VERTEX_SHADER);
	var fs = gl.createShader(gl.FRAGMENT_SHADER);


	gl.shaderSource(vs, vsSource);
	gl.shaderSource(fs, header + shader.code);

	gl.compileShader(vs);
	if(!gl.getShaderParameter(vs, gl.COMPILE_STATUS))
		return status('Internal error', 'red');
	gl.compileShader(fs);
	if(!gl.getShaderParameter(fs, gl.COMPILE_STATUS))
		return errorShader(shader, gl.getShaderInfoLog(fs), 1);
	var program = gl.createProgram();

	gl.attachShader(program, vs);
	gl.attachShader(program, fs);

	gl.linkProgram(program);
	if(!gl.getProgramParameter(program, gl.LINK_STATUS))
		return errorShader(shader, gl.getProgramInfoLog(program), 2);

	return program;
}

function completeShader(shader, success, error) {
	$rpc.runner.feedback(shader.id, success, error);
	status('Done!  Waiting for more shaders...');
	pollServer();
}

var currentShader = null;

function runShader(shader) {
	currentShader = shader.id;
	status('Compiling shader...');
	var program = compile(shader);
	if(program === false || program === null)
		return;

	completeShader(shader, true, '');
}

function sendInfo() {
	if($.cookie('gpu') === undefined) {
		$('#gpuInfo').show();
		status('Waiting on your GPU information...')
		return;
	}

	var info = glInfo();
	if(info !== false) {
		status('WebGL found.  Connecting to server...');
		$rpc.runner.init(info, function() {
			status('Initialization complete. Waiting on shaders...');
			pollServer();
			setInterval(pollServer, 10*1000)
		})
	} else {
		status('WebGL not found!', 'red');
	}
}

$(document).ready(function() {
	status('Initializing...');

	$('#submit-info').click(saveInfo);

	sendInfo();
})