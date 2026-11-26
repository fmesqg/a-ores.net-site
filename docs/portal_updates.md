---
title: Novidades do Portal do Governo
layout: default
permalink: /portal_updates
---
# Novidades do [Portal do Governo](https://portal.azores.gov.pt/)

Desde meados de 2026 o portal bloqueia o acesso automático às suas páginas.
Os boletins de execução orçamental (BEO) continuam a ser seguidos, porque os
PDF estão num endereço previsível, e os seus quadros estão em
[Execução orçamental](/dados/beo/). Os boletins informativos do SIGICA
deixaram de poder ser seguidos.

## [Portal RSS feed](/rss/portal.xml)

{% assign full_updates = site.portal_updates | sort: "date" | reverse %}
{% for update in full_updates %}  <p>
  <details id="{{ update.date | date: "%Y-%m-%d" }}">
  <summary>
  <h2>{{ update.date | date: "%Y-%m-%d"  }}</h2>
  </summary>
      {{ update.content }}
  </details>
  </p>
{% endfor %}
