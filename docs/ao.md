---
title: Açoriano Oriental (Edição Impressa)
layout: default
permalink: /ao/
noindex: true
---
# Açoriano Oriental — Edição Impressa

## [Feed RSS](/rss/ao.xml)

Uma entrada por dia, com as ligações para os artigos dessa edição.

<ul>
  {% assign editions = site.ao | where: "kind", "day" | sort: "date" | reverse %}
  {% for edition in editions %}
  <li>
    <a href="{{ edition.url | relative_url }}">{{ edition.edition }}</a>
    <span class="post-meta">({{ edition.article_count }} artigos)</span>
  </li>
  {% endfor %}
</ul>
