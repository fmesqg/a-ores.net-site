---
title: Auto Updates
layout: default
permalink: /auto-updates
---
# Novidades da [Assembleia Legislativa](https://www.alra.pt/), [Jornal Oficial](https://jo.azores.gov.pt/) e [BASE](https://www.base.gov.pt)

## [RSS feed](/alra-rss.xml)

{% assign full_updates = site.complete_updates | sort: "date" | reverse %}
{% for update in full_updates %}  <p>
  <details>
  <summary>
  <h2>{{ update.date | date: "%Y-%m-%d"  }}</h2>
  </summary>
      {{ update.content }}
  </details>
  </p>
{% endfor %}
