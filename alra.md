---
title: ALRA
layout: default
permalink: /alra
---
# ALRA - Novidades

[RSS feed](/alra-rss.xml)
<ul>
  {% for post in site.posts %}
    {% if post.categories contains "alra-scrapper" %}
    <li><h2>{{ post.date | date: "%Y-%m-%d"  }}</h2>
       {{ post.content }}
    </li>
    {% endif %}
  {% endfor %}
</ul>
