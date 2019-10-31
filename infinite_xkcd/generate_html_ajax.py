#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import json
import sys
import os
import operator
import itertools

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from scipy.sparse import find

import nltk
from nltk.stem.porter import PorterStemmer
import string

from builtins import str

if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " <infile> <outdir>")
    sys.exit(1)

print("read file:  " + sys.argv[1])
print("write in dir: " + sys.argv[2])


def tokenize(text):
    punctuations = string.punctuation + '»«„“–…—×→←↓↑↺'
    translatetable = {ord(c): str(" ") for c in punctuations}
    #translatetable[ord("\xad")] = None
    #print(translatetable)
    tokens = nltk.word_tokenize(text.translate(translatetable))
    #stemmer = GermanStemmer()
    stemmer = stemmer = PorterStemmer()
    stems = []
    for item in tokens:
        if not item.isdigit():
            stems.append(stemmer.stem(item))
    return stems


corpus = []
maxid = 0

with open(sys.argv[1]) as infile:
    for line in infile:
        j = json.loads(line)
        #		text = j["explanation"] + " " + j["transcript"] + " " + j["trivia"] + " " + j["title"] + " " + j["titletext"]
        text = j["explanation"] + " " + j["transcript"] + " " + j[
            "title"] + " " + j["titletext"]
        corpus.append({"id": j["id"], "text": text})
        maxid = max(maxid, j["id"])

corpus = sorted(corpus, key=lambda k: k["id"])

tfidf_vect = TfidfVectorizer(tokenizer=tokenize, stop_words="english")
tfidf = tfidf_vect.fit_transform([x["text"] for x in corpus])

docsim = linear_kernel(tfidf, tfidf)

outfilename = sys.argv[2]
if not outfilename.endswith(os.sep):
    outfilename += os.sep

with open(outfilename + "index.html", "w") as outfile:
    outfile.write("""
<html>

<head>
<title>infinite xkcd</title>
<script src="https://code.jquery.com/jquery-2.2.4.min.js" type="text/javascript" ></script>
<script src="http://rawgit.com/imakewebthings/waypoints/master/lib/jquery.waypoints.min.js" type="text/javascript" ></script>
<script src="http://rawgit.com/imakewebthings/waypoints/master/lib/shortcuts/infinite.min.js" type="text/javascript" ></script>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>


<body>
<h1>Infinite xkcd</h1>

<div>
	<p><a href="?">Restart with newest on top.</a> - <a href="?start=random">Restart with random on top.</a></p>
</div>

<div id="contents">


</div>

<button id="morebutton" class="infinite-more-link" type="button" onClick="more();">more ...</button>
<p id="done" style="display:none; font-size: xx-large;">That's all. :-(</p>



</body>

<script>

	var usedIds = [];

	function getStartId() {
		var query = window.location.search.substring(1);
		var vars = query.split("&");
		for (var i=0;i<vars.length;i++) {
			var pair = vars[i].split("=");
			if (pair[0] == "start") {
				if(pair[1] == "random") {
					var randomStartId = Math.floor(Math.random() * """ + str(maxid) + """);
					console.log("random start id:    " + randomStartId);
					window.history.replaceState("", "", "?start=" + (randomStartId+1));
					return randomStartId + 1;
				} else {
					return parseInt(pair[1]);
				}
			}
		}

		// no start parameter, use latest id:
		window.history.replaceState("", "", "?start=" + """ + str(maxid) + """);
		return """ + str(maxid) + """;
	}


	var nextId = getStartId();


	load(nextId);



	function load(id) {
		$.get(id + ".json", function(data, status){
        	var entry = data;
        	var div = document.createElement("div");
			div.className = "item";

			div.innerHTML = `
				<h2><a href="${entry["url"]}">${entry["id"]}: ${entry["title"]}</a></h2>
				<p><img src="${entry["imgurl"]}" title="${entry["titletext"]}" style="max-width: 100%; height: auto;" /></p>
				<p>${entry["titletext"]}</p>
				<p><a href="${entry["explanationurl"]}">Explanation.</a> - <a href="?start=${entry["id"]}">Restart with this comic on top.</a> - <a href="similar.html?start=${entry["id"]}">Show similar comics.</a></p>
			`
			document.getElementById('contents').appendChild(div);

			usedIds.push(entry.id);

			for(var i = 0; i < entry["similar"].length; i++) {
				var next = entry["similar"][i];
				if($.inArray(next, usedIds) == -1){
					nextId = next;
					break;
				}
			}
			if(usedIds.length < 10) {
				more();
			} else {
				waypoint.context.refresh();
				waypoint.enable();
			}
    	});

	}



	function more() {
		console.log("loading " + (usedIds.length+1) + "th item with id: " + nextId);
		load(nextId);
		if(usedIds.length == """ + str(maxid) + """) {
			document.getElementById('morebutton').style.display = "none";
			document.getElementById('done').style.display = "block";
		}
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





</script>
</html>

	""")
with open(sys.argv[1]) as infile:
    for line in infile:
        j = json.loads(line)
        out = {}
        out["id"] = j["id"]
        out["title"] = j["title"]
        out["url"] = j["link"]
        out["imgurl"] = j["imgurl"]
        out["titletext"] = j["titletext"]
        out["explanationurl"] = j["url"]
        simitems = dict(enumerate(docsim[j["id"] - 1]))
        simitems = sorted(simitems.items(),
                          key=operator.itemgetter(1),
                          reverse=True)
        simitems = [item[0] + 1 for item in simitems]
        out["similar"] = simitems

        with open(outfilename + str(j["id"]) + ".json", "w") as outfile:
            json.dump(out, outfile)

# http://imakewebthings.com/waypoints/shortcuts/infinite-scroll/
