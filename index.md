---
title: Açores
layout: default
permalink: /
---
(página em desenvolvimento — ajuda bem-vinda! (email: f [arroba] mesquita [ponto] xyz))
# Viva!

Este _site_ pretende promover uma cidadania ativa, através da disponibilização de informação acessível e fidedigna.


# Retrato dos Açores (PORDATA)
* [pdf](/assets/pdf/RetratoAçores2023.pdf)
* [site](https://www.pordata.pt/retratos/2023/retrato+dos+acores-91)

# Notícias
<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.date | date: "%Y-%m-%d" }} - {{ post.title }}</a>
    </li>
  {% endfor %}
</ul>