---
title: A trabalhar
layout: default
permalink: /trabalhar
---
# Assuntos interessantes a trabalhar

{% assign x = site.trabalhar | sort: "date" | reverse %}
{% for post in x %}

* {{ post.date | date: "%Y-%m-%d" }}: [{{ post.title | xml_escape }}]({{ post.link | strip }})
{% endfor %}
