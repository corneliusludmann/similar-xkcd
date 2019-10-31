var ids = [];
var maxid = 0;
var usedIds = [];

$.get("info.json", function(data, status) {
	maxid = data["maxid"];
	ids = data["ids"];
	var nextId = getStartId(maxid);
	load(nextId);
	document.getElementById('loader').style.display = "none";
});

function getStartId(maxid) {
	var query = window.location.search.substring(1);
	var vars = query.split("&");
	for (var i = 0; i < vars.length; i++) {
		var pair = vars[i].split("=");
		if (pair[0] == "start") {
			if (pair[1] == "random") {
				var randomStartId = ids[Math.floor(Math.random() * ids.length)];
				console.log("random start id:	" + randomStartId);
				window.history.replaceState("", "", "?start=" + (randomStartId));
				return randomStartId;
			} else {
				return parseInt(pair[1]);
			}
		}
	}

	// no start parameter, use latest id:
	window.history.replaceState("", "", "?start=" + maxid);
	return maxid;
}

function load(id) {
	$.get(id + ".json", function(data, status) {
		var entry = data;
		var div = document.createElement("section");
		div.className = "main special";

		div.innerHTML = `
				<header class="major">
					<h2>${entry["id"]}: ${entry["title"]}</h2>
				</header>
				<p class="special"><img src="${entry["img_url"]}" title="${entry["img_title_text"]}" style="max-width: 100%; height: auto;" /></p>
				<p class="special">${entry["img_title_text"]}</p>
				<p class="special" style="font-size: 80%; font-style: italic;"><a href="${entry["xkcd_url"]}">xkcd</a> – <a href="${entry["explain_xkcd_url"]}">explanation</a> – <a href="?start=${entry["id"]}">restart with this comic on top</a></p>
			`
		var main = document.getElementById('main');
		var moresection = document.getElementById('moresection');
		main.insertBefore(div, moresection);

		usedIds.push(parseInt(entry.id));

		if (hasMore()) {
			for (var i = 0; i < entry["similar"].length; i++) {
				var next = parseInt(entry["similar"][i][0]);
				if (usedIds.indexOf(next) == -1) {
					nextId = next;
					break;
				}
			}
		} else {
			nextId = -1;
		}

		if (usedIds.length < 10 && hasMore()) {
			load(nextId);
		} else {
			waypoint.context.refresh();
			waypoint.enable();
		}
		if (hasMore()) {
			document.getElementById('morebutton').style.display = "block";
			document.getElementById('done').style.display = "none";
		} else {
			document.getElementById('morebutton').style.display = "none";
			document.getElementById('done').style.display = "block";
		}
	});
}

function more() {
	if (hasMore() && nextId > 0) {
		load(nextId);
		document.getElementById('morebutton').style.display = "block";
		document.getElementById('done').style.display = "none";
	} else {
		document.getElementById('morebutton').style.display = "none";
		document.getElementById('done').style.display = "block";
	}
}

function hasMore() {
	return usedIds.length < ids.length;
}

var waypoint = new Waypoint({
	element: document.getElementById('morebutton'),
	handler: function() {
		waypoint.disable();
		more();
	},
	offset: 'bottom-in-view',
	enabled: false
})
