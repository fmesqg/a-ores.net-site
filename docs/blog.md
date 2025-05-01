---
title: Opinião
layout: default
permalink: /blog
---

## Opinião

{% assign sorted_items = site.posts | sort: 'date' | reverse %}
{% for post in sorted_items %}
{% if post.op %}

* {{ post.date | date: "%Y-%m-%d" }}: [{{ post.title | xml_escape }}]({{ post.url | strip }}) por {{ post.author }}

{% endif  %}
{% endfor %}
