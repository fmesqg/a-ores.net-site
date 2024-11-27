---
title: JORAA Updates
layout: default
permalink: /joraa_updates
---
# Novidades do [Jornal Oficial](https://jo.azores.gov.pt/)

## [JORAA RSS feed](/rss/joraa.xml)

{% assign full_updates = site.joraa_updates | sort: "date" | reverse %}
{% for update in full_updates %}  <p>
  <details>
  <summary>
  <h2>{{ update.date | date: "%Y-%m-%d"  }}</h2>
  </summary>
      {{ update.content }}
  </details>
  </p>
{% endfor %}
