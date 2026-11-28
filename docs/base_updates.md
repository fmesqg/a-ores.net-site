---
title: Novidades da BASE
layout: default
permalink: /base_updates
---
# Novidades da [BASE](https://www.base.gov.pt)

## [BASE RSS feed](/rss/base.xml)

{% assign full_updates = site.base_updates | sort: "date" | reverse %}
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

