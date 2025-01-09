---
title: Açores
layout: default
permalink: /
---
(página em desenvolvimento — ajuda bem-vinda! (email: f [arroba] mesquita [ponto] xyz))

# Viva

Este _site_ pretende promover uma cidadania ativa, através da disponibilização de informação acessível e fidedigna.

# Retrato dos Açores (PORDATA)

* [pdf](/assets/pdf/RetratoAçores2023.pdf)
* [site](https://www.pordata.pt/retratos/2023/retrato+dos+acores-91)

# Análises/Documentos

<ul>
  {% for post in site.posts %}
    {% if post.link  %}
    <li>
      <a href="{{ post.page }}">{{ post.date | date: "%Y-%m-%d" }} - {{ post.title }}</a>
    </li>
    {% else %}
    <li>
      <a href="{{ post.url }}">{{ post.date | date: "%Y-%m-%d" }} - {{ post.title }}</a>
    </li>
    {% endif %}

  {% endfor %}
</ul>

# Atualizações automáicas

## [ALRA](/alra_updates)

<ul>
{% assign full_updates = site.alra_updates | sort: "date" | reverse %}
{% for update in full_updates limit:20 %}

    <li>
      <a href="{{ update.url }}">{{ update.date | date: "%Y-%m-%d" }}</a>
    </li>
  {% endfor %}
</ul>

## [JORAA](/joraa_updates)

<ul>
{% assign full_updates = site.joraa_updates | sort: "date" | reverse %}
{% for update in full_updates limit:20 %}

    <li>
      <a href="{{ update.url }}">{{ update.date | date: "%Y-%m-%d" }}</a>
    </li>
  {% endfor %}
</ul>

## [BASE (Açores)](/base_updates)

<ul>
{% assign full_updates = site.base_updates | sort: "date" | reverse %}
{% for update in full_updates limit:20 %}

    <li>
      <a href="{{ update.url }}">{{ update.date | date: "%Y-%m-%d" }}</a>
    </li>
  {% endfor %}
</ul>
