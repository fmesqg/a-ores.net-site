---
title: Novidades do Jornal Oficial
layout: default
permalink: /joraa_updates
---
# Novidades do [Jornal Oficial](https://jo.azores.gov.pt/)

## [JORAA RSS feed](/rss/joraa.xml)

{% include joraa-atraso.html %}

{% assign full_updates = site.joraa_updates | sort: "date" | reverse %}
{% for update in full_updates limit: 30 %}  <p>
  <details id="{{ update.date | date: "%Y-%m-%d" }}">
  <summary>
  <h2>{{ update.date | date: "%Y-%m-%d"  }}</h2>
  </summary>
      {{ update.content }}
  </details>
  </p>
{% endfor %}

## Dias anteriores

Cada dia tem a sua página. Para procurar em tudo o que foi recolhido, use os [dados abertos](/dados/).

<ul class="dias">
{% for update in full_updates offset: 30 %}<li><a href="{{ update.url }}">{{ update.date | date: "%Y-%m-%d" }}</a></li>
{% endfor %}</ul>

<style>.dias { columns: 9em; list-style: none; margin-left: 0; } .dias li { margin: 0 0 .2em; }</style>
