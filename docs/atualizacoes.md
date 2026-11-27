---
title: Atualizações diárias
nav_title: Atualizações
layout: default
permalink: /atualizacoes/
---
# Atualizações diárias

Todos os dias, o açores.net verifica o que entrou de novo em três fontes
oficiais e publica uma página por dia com as novidades, cada uma com a
ligação para o documento original. Pode lê-las aqui, segui-las por
[RSS](/rsss) ou pesquisar em tudo o que já foi recolhido nos
[dados abertos](/dados/).

{% assign fontes = "alra|joraa|base" | split: "|" %}
{% for f in fontes %}
{%- case f -%}
{%- when "alra" -%}{%- assign docs = site.alra_updates -%}{%- assign nome = "Assembleia Legislativa (ALRA)" -%}{%- assign todas = "/alra_updates" -%}
{%- when "joraa" -%}{%- assign docs = site.joraa_updates -%}{%- assign nome = "Jornal Oficial (JORAA)" -%}{%- assign todas = "/joraa_updates" -%}
{%- when "base" -%}{%- assign docs = site.base_updates -%}{%- assign nome = "Contratos públicos (BASE)" -%}{%- assign todas = "/base_updates" -%}
{%- endcase -%}
{%- assign dias = docs | sort: "date" | reverse %}
<section class="fonte">
<h2 id="{{ f }}">{{ nome }}</h2>
{%- case f -%}
{%- when "alra" %}
<p>O parlamento regional. Requerimentos (perguntas dos deputados ao Governo,
e se já foram respondidas), propostas e projetos, votos, petições,
audições, diários das sessões e notas de imprensa dos grupos parlamentares.
Fonte: <a href="https://www.alra.pt/">alra.pt</a>.</p>
{%- when "joraa" %}
<p>O Jornal Oficial da Região, onde saem os decretos, portarias, despachos e
resoluções do Governo Regional. O açores.net destaca os atos com montantes:
apoios, subsídios, contratos-programa e outras despesas.
Fonte: <a href="https://jo.azores.gov.pt/">jo.azores.gov.pt</a>.</p>
{% include joraa-atraso.html %}
{%- when "base" %}
<p>Os contratos públicos assinados por entidades dos Açores (Governo,
câmaras, hospitais, empresas públicas): quem contratou, com quem, o quê, por
que procedimento e por quanto. Fonte: <a href="https://www.base.gov.pt/">base.gov.pt</a>.</p>
{%- endcase %}
<p class="dias-recentes"><strong>Últimos dias:</strong>
{%- for d in dias limit: 7 %} <a href="{{ d.url }}">{{ d.date | date: "%d/%m" }}</a>{% unless forloop.last %} ·{% endunless %}{% endfor %}</p>
<p><a href="{{ todas }}">Todos os dias</a> · <a href="/rss/{{ f }}.xml">RSS</a> ·
<a href="/dados/#fonte={{ f }}">Pesquisar</a></p>
</section>
{% endfor %}

<section class="fonte">
<h2 id="portal">Portal do Governo</h2>
<p>Desde meados de 2026 o portal do Governo Regional bloqueia o acesso
automático, por isso as notícias e os boletins do SIGICA deixaram de ser
seguidos. Os boletins de execução orçamental continuam, em
<a href="/dados/beo/">Contas do Governo Regional</a>.
<a href="/portal_updates">Arquivo do portal</a>.</p>
</section>

<style>
.fonte { margin-bottom: 1.5em; max-width: 46em; }
.fonte h2 { font-size: 1.3em; margin-bottom: .3em; }
.fonte p { margin-bottom: .4em; }
.dias-recentes a { white-space: nowrap; }
</style>
