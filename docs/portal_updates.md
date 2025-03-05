---
title: JORAA Updates
layout: default
permalink: /portal_updates
---
# Novidades do [Portal do GRA](portal.azores.gov.pt)

## [Portal RSS feed](/rss/portal.xml)

{% assign full_updates = site.portal_updates | sort: "date" | reverse %}
{% for update in full_updates %}  <p>
  <details>
  <summary>
  <h2>{{ update.date | date: "%Y-%m-%d"  }}</h2>
  </summary>
      {{ update.content }}
  </details>
  </p>
{% endfor %}
