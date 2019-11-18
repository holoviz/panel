function expand(e) {
	if (e.target.parentNode.tagName.toLowerCase() != "dl") {
		var p = e.target.parentNode.parentNode;
	} else {
		var p = e.target.parentNode;
	}

	if (p.className == "class rm_collapsed")
		p.className = "class rm_expanded";
	else if (p.className == "class rm_expanded")
		p.className = "class rm_collapsed";
}

function expand_ref(ref) {
	if (ref == null) {
		return
	}
	while (ref.className !== 'class rm_collapsed' &&
		   ref.parentNode !== undefined) {
		ref = ref.parentNode;
		if (ref == null) {
			return
		}
	}
	if (ref.className == 'class rm_collapsed') {
		ref.className = "class rm_expanded";
	}
}

function expand_loc() {
	var loc = location.hash;
	if (loc[0] === '#') {
		var ref = $(loc.split('.').join('\\.'));
		if (ref.length) {
			expand_ref(ref[0]);
			if (ref[0].position == null) {
				return
			}
			var top = ref[0].position().top;
			$(window).scrollTop(top);
		}
	}
}

function hook_classes() {
	window.onhashchange = expand_loc;
	$("dl.class dt").click(expand);
	$('body').find('dl.class').addClass("rm_collapsed");
	$.each($('code'), function(index, code) {
		code.textContent = code.textContent.trim()
	});
	$.each($('.output_subarea').find('pre'), function(index, pre) {
		pre.textContent = pre.textContent.split('&apos;').join("'");
	});
	expand_loc();
}


delete require;
$(document).ready(hook_classes);
