---
title: Auto Updates
layout: default
permalink: /auto-updates
---
# Novidades da [Assembleia Legislativa](https://www.alra.pt/), [Jornal Oficial](https://jo.azores.gov.pt/) e [BASE](https://www.base.gov.pt)

## [RSS feed](/alra-rss.xml)

{% for post in site.posts %}
  {% if post.categories contains "alra-scrapper" %}
  <p>
  <details>
  <summary>
  <h2>{{ post.date | date: "%Y-%m-%d"  }}</h2>
  </summary>
      {{ post.content }}
  </details>
  </p>
  {% endif %}
{% endfor %}
