---
title: BASE Updates
layout: default
permalink: /base_updates
---
# Novidades da [BASE](https://www.base.gov.pt)

## [BASE RSS feed](/rss/base.xml)

{% assign full_updates = site.base_updates | sort: "date" | reverse %}
{% for update in full_updates %}  <p>
  <details>
  <summary>
  <h2>{{ update.date | date: "%Y-%m-%d"  }}</h2>
  </summary>
      {{ update.content }}
  </details>
  </p>
{% endfor %}
