$(document).ready(function() {
	$('#test').click(function() {
		var code = $('#code').val()
		$rpc.api.enqueue(code, function(ret) {
			if(ret === false || ret === null)
				return alert('An error occured.  Please try again.');
			window.location = '/progress/' + ret;
		});
	})
})