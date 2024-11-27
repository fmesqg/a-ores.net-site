---
title: ALRA Updates
layout: default
permalink: /alra_updates
---
# Novidades da [Assembleia Legislativa](https://www.alra.pt/)

## [ALRA RSS feed](/rss/alra.xml)

{% assign full_updates = site.alra_updates | sort: "date" | reverse %}
{% for update in full_updates %}  <p>
  <details>
  <summary>
  <h2>{{ update.date | date: "%Y-%m-%d"  }}</h2>
  </summary>
      {{ update.content }}
  </details>
  </p>
{% endfor %}
