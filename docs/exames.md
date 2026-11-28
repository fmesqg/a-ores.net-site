---
title: Exames nacionais por escola
layout: default
permalink: /dados/exames/
secao: estatisticas
description: Resultados dos exames nacionais do secundário e das provas finais do 9.º ano em cada escola dos Açores, ao lado da Madeira, do continente e do país, com a posição de cada escola entre todas as do país.
---
{%- assign x = site.data.exames -%}
{% include estatisticas-nav.html %}

# Exames nacionais por escola

<p class="lead">As notas dos exames nacionais do secundário e das provas
finais do 9.º ano em cada escola dos Açores, ao lado da Madeira, do
continente e do país. Os Açores fazem os mesmos exames que o resto do país;
as bases de dados são as do Júri Nacional de Exames para a comunicação
social, publicadas pela DGEEC no
<a href="https://infoescolas.pt/bds.asp">InfoEscolas</a> (o portal
InfoEscolas em si só cobre o continente).</p>

{% if x %}
<div class="numeros">
{%- for n in x.niveis %}
<div class="numero">
  <p class="rotulo">{{ n.nome }}, {{ n.ano }}</p>
  <p class="grande">{{ n.media_az }} <small>/ {{ n.media_pt }}</small></p>
  <p>Média dos Açores e do país ({{ n.escala }}){% if n.id == "basico" %}, Português e Matemática{% else %}, todos os exames{% endif %}.</p>
</div>
{%- endfor %}
</div>

<nav class="indice" aria-label="Nesta página">
{%- for n in x.niveis %}
  <a href="#{{ n.id }}"><span>{{ forloop.index }}</span> {{ n.nome }}</a>
{%- endfor %}
  <a href="#notas"><span>{{ x.niveis.size | plus: 1 }}</span> Notas</a>
</nav>

{% for n in x.niveis %}
<h2 id="{{ n.id }}">{{ forloop.index }}. {{ n.nome }} ({{ n.ano }})</h2>

<h3 id="{{ n.id }}-regioes">Os Açores e o resto do país</h3>
<p class="nota">Média de cada região ({{ n.escala }}){% if n.id == "secundario" %}; só os exames que os Açores fizeram pelo menos 100 vezes{% endif %}.
A diferença é Açores menos o país. «Positivas» é a percentagem de
{% if n.id == "secundario" %}exames com 95 ou mais{% else %}provas com nível 3 ou mais{% endif %}.</p>
<div class="tabela-scroll">
<table class="sper exames">
<thead><tr>
  <th scope="col">{% if n.id == "secundario" %}Exame{% else %}Prova{% endif %}</th>
  <th scope="col" class="n">Provas nos Açores</th>
  <th scope="col" class="n az">Açores</th>
  <th scope="col" class="n">Madeira</th>
  <th scope="col" class="n">Continente</th>
  <th scope="col" class="n">País</th>
  <th scope="col" class="n sep">Diferença</th>
  <th scope="col" class="n">% positivas (Açores)</th>
  <th scope="col" class="n">% positivas (país)</th>
</tr></thead>
<tbody>
{%- for l in n.linhas %}
<tr{% if l.todos %} class="total"{% endif %}><th scope="row">{{ l.exame }}</th>
<td class="n">{{ l.provas_az }}</td>
<td class="n az">{{ l.medias.AZ }}</td>
<td class="n">{{ l.medias.MD | default: "–" }}</td>
<td class="n">{{ l.medias.CO | default: "–" }}</td>
<td class="n">{{ l.medias.PT | default: "–" }}</td>
<td class="n sep">{{ l.dif }}</td>
<td class="n">{{ l.positivas_az }}</td>
<td class="n">{{ l.positivas_pt }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h3 id="{{ n.id }}-escolas">Escolas dos Açores</h3>
<p class="nota">Ordenadas pela média de {% if n.id == "secundario" %}todos os exames{% else %}Português e Matemática{% endif %}
em {{ n.ano }}. Por baixo do nome, o concelho. A posição conta as {{ n.n_escolas }} escolas do país com pelo
menos {{ n.min_provas }} provas (1.ª = média mais alta); as escolas com menos
não têm posição. A média interna é {{ n.interna }} dos mesmos alunos{% if n.anos.size > 1 %}; as
colunas dos anos dão a média de cada ano{% endif %}.</p>
<div class="tabela-scroll">
<table class="sper exames">
<thead><tr>
  <th scope="col">Escola</th>
  <th scope="col" class="n">Provas</th>
  <th scope="col" class="n az">Média</th>
  {%- for p in n.principais %}<th scope="col" class="n">{{ p }}</th>{% endfor %}
  <th scope="col" class="n">Média interna</th>
  <th scope="col" class="n">Posição no país</th>
  {%- if n.anos.size > 1 -%}{%- for a in n.anos %}<th scope="col" class="n{% if forloop.first %} sep{% endif %}">{{ a }}</th>{% endfor -%}{%- endif %}
</tr></thead>
<tbody>
{%- for e in n.escolas %}
<tr><th scope="row">{{ e.nome }}<small class="conc">{{ e.concelho }}{% if e.privada %}, privada{% endif %}</small></th>
<td class="n">{{ e.provas }}</td>
<td class="n az">{{ e.media }}</td>
{%- for p in e.principais %}<td class="n">{{ p | default: "–" }}</td>{% endfor %}
<td class="n">{{ e.interna | default: "–" }}</td>
<td class="n">{% if e.posicao != "" %}{{ e.posicao }}.ª{% else %}–{% endif %}</td>
{%- if n.anos.size > 1 -%}{%- for a in e.anos %}<td class="n{% if forloop.first %} sep{% endif %}">{{ a | default: "–" }}</td>{% endfor -%}{%- endif %}
</tr>
{%- endfor %}
</tbody>
</table>
</div>
{% endfor %}

<h2 id="notas">{{ x.niveis.size | plus: 1 }}. Notas</h2>
<ul class="notas">
  <li><strong>O que se conta.</strong> Como nos rankings da imprensa: 1.ª
  fase e alunos internos; no secundário, só os exames feitos para aprovação
  (não os de melhoria nem os só para ingresso no superior); no 9.º ano, as
  provas de Português e Matemática, na escola que o aluno frequenta.</li>
  <li><strong>Média de todos os exames.</strong> Junta exames diferentes, por
  isso depende também dos exames que os alunos de cada escola fazem. É a
  convenção dos rankings, não uma medida da escola; as colunas por exame
  comparam melhor.</li>
  <li><strong>Escolas pequenas.</strong> Com poucas dezenas de provas, a
  média de uma escola muda muito de um ano para o outro.</li>
  <li><strong>Média interna e exame.</strong> A média interna é a nota dada
  pela escola aos mesmos alunos. Está noutra escala, por isso compara-se
  entre escolas (uma escola com média interna alta e exame baixo), não com
  o exame diretamente.</li>
  <li><strong>Anos.</strong> As regras sobre que exames contam para a
  aprovação no secundário mudaram nos últimos anos: em 2024 contaram para a
  aprovação menos de metade dos exames de 2025, no país e nos Açores.
  Compare médias entre anos com cuidado. A base de 2023 do secundário não
  distingue os alunos internos (todos aparecem como externos) e fica de
  fora.</li>
  <li><strong>Atualização.</strong> As bases saem uma vez por ano (as de
  2025 entre março e outubro de 2026); o InfoEscolas guarda só os três
  últimos anos, o açores.net guarda todos os que leu. São relidas uma vez
  por semana por
  <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/exames.py"><code>bot/exames.py</code></a>.
  Os números estão em <a href="/dados/exames.csv">exames.csv</a> e na tabela
  <code>exames</code> de <a href="/dados/sql/">estatisticas.db</a>.</li>
</ul>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
h2[id], h3[id] { scroll-margin-top: 1em; }
h2[id] { margin-top: 1.4em; }
table.exames { font-size: .88em; }
table.exames th[scope="row"] { font-weight: normal; min-width: 12em; }
table.exames th[scope="row"] small.conc { display: block; color: var(--s01); font-size: .85em; }
table.exames .az { font-weight: bold; background: rgba(37,125,224,.09); }
table.exames .sep { border-left: 1px solid var(--s1); }
table.exames tr.total th, table.exames tr.total td { font-weight: bold; }
</style>
