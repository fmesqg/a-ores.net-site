---
title: Auto Updates
layout: default
permalink: /auto-updates
---
# Novidades da política açoriana

[RSS feed](/alra-rss.xml)
<ul>
  {% for post in site.posts %}
    {% if post.categories contains "alra-scrapper" %}
    <li><h1>{{ post.date | date: "%Y-%m-%d"  }}</h1>
       {{ post.content }}
    </li>
    {% endif %}
  {% endfor %}
</ul>
