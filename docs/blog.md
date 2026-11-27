---
title: Opinião e análises
nav_title: Opinião
layout: default
permalink: /blog
---

## Artigos de opinião

{% assign sorted_items = site.posts | sort: 'date' | reverse %}
{% for post in sorted_items %}
{% if post.op %}
  {% assign author = site.authors | where: "short_name", post.author | first %}
  {% assign post_date = post.date | date: "%Y-%m-%d" %}
  {% if author %}

* {{ post_date }}: [{{ post.title | xml_escape }}]({{ post.url | strip }}) por [{{ author.name }}]({{ author.url }})
  {% else %}
* {{ post_date }}: [{{ post.title | xml_escape }}]({{ post.url | strip }}) por {{ post.author }}
  {% endif %}
  
{% endif %}
{% endfor %}

## Análises e documentos {#analises}

{% for post in sorted_items %}{% unless post.op %}
* {{ post.date | date: "%Y-%m-%d" }}: [{{ post.title | xml_escape }}]({% if post.link %}{{ post.page }}{% else %}{{ post.url }}{% endif %})
{% endunless %}{% endfor %}
* Retrato dos Açores 2023 (PORDATA): [pdf](/assets/pdf/RetratoAçores2023.pdf), [site](https://www.pordata.pt/retratos/2023/retrato+dos+acores-91)

## Autores

{% assign sorted_items = site.authors | sort: 'short_name' %}
{% for author in sorted_items %}
  {% assign post_count = site.posts | where: 'author', author.short_name | size %}

* [{{ author.name | xml_escape }}]({{ author.url }}) ({{ post_count }} posts)
{% endfor %}
