---
title: A trabalhar
layout: default
permalink: /trabalhar
---
# Assuntos interessantes a trabalhar

{% assign x = site.trabalhar | sort: "date" | reverse %}
{% for post in x %}
    {% capture x %}
      {% if post.link %}
        {{ post.link }}
      {% else %}
        {{ post.url }}
      {% endif %}
    {% endcapture %}

* {{ post.date | date: "%Y-%m-%d" }}: [{{ post.title | xml_escape }}]({{ x | strip }})
{% endfor %}
