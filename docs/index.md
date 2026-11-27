---
title: Açores
layout: default
permalink: /
---
{%- assign alra = site.alra_updates | sort: "date" | last -%}
{%- assign joraa = site.joraa_updates | sort: "date" | last -%}
{%- assign base = site.base_updates | sort: "date" | last -%}
<p class="lead">Dados públicos sobre os Açores, num só sítio e explicados:
estatísticas por concelho e freguesia, as contas do Governo Regional,
contratos públicos e o trabalho da Assembleia Legislativa. Cada número tem
ligação para a fonte oficial. Primeira vez por aqui? Comece pelo
<a href="/acores-101/"><strong>Açores 101</strong></a>.</p>

<div class="portas">

<section class="porta">
  <h2><a href="/dados/ine/">Estatísticas por concelho e freguesia</a></h2>
  <p>Rendimentos e IRS, rendas e preço das casas, população, turismo,
  câmaras municipais. Compare o seu concelho ou freguesia com os outros, com
  a Madeira e com o país. Cada indicador vem com a definição do INE.</p>
  <ul>
    <li><a href="/dados/ine/#ind=0012757&nivel=Freguesia">Quanto se ganha em cada freguesia?</a></li>
    <li><a href="/dados/ine/#ind=0012759">Como se distribui o rendimento (quintis)?</a></li>
    <li><a href="/dados/ine/#ind=0014698">Quanto custa arrendar casa?</a></li>
    <li><a href="/dados/ine/#ind=0013210">Onde há mais turistas por habitante?</a></li>
  </ul>
</section>

<section class="porta">
  <h2><a href="/dados/beo/">Contas do Governo Regional</a></h2>
  <p>Quanto a Região cobra e quanto gasta, mês a mês, a partir dos boletins
  de execução orçamental, com um glossário dos termos.{% if site.data.beo_ultimo.periodo %}
  Último boletim: <a href="{{ site.data.beo_ultimo.url }}">{{ site.data.beo_ultimo.periodo }}</a>.{% endif %}</p>
  <ul>
    <li><a href="/dados/beo/#quadro=sintese-global">Há défice ou excedente?</a></li>
    <li><a href="/dados/beo/#quadro=receita-fiscal-do-gra">Quanto rendem o IRS e o IVA?</a></li>
    <li><a href="/dados/beo/#quadro=despesa-do-gra-por-departamento">Quanto gasta cada secretaria?</a></li>
  </ul>
</section>

<section class="porta">
  <h2><a href="/dados/">Contratos, Assembleia e Jornal Oficial</a></h2>
  <p>Pesquise os contratos públicos (quem contratou o quê, a quem e por
  quanto), as perguntas dos deputados ao Governo e os atos do Jornal Oficial
  com montantes. Desde agosto de 2024, em tabela e em CSV.</p>
  <ul>
    <li><a href="/dados/#fonte=base&min=1000000">Contratos acima de um milhão de euros</a></li>
    <li><a href="/dados/#fonte=alra&tipo=Requerimentos">Perguntas dos deputados ao Governo</a></li>
    <li><a href="/dados/#fonte=joraa">Apoios e despesas publicados no Jornal Oficial</a></li>
  </ul>
</section>

<section class="porta">
  <h2><a href="/atualizacoes/">Acompanhar o dia a dia</a></h2>
  <p>O que entrou de novo, todos os dias, na Assembleia Legislativa, no
  Jornal Oficial e no portal dos contratos públicos. Pode seguir pelo site ou
  por <a href="/rsss">RSS</a>. Última recolha:</p>
  <ul>
    {%- if alra %}<li><a href="{{ alra.url }}">Assembleia</a>: {{ alra.date | date: "%d/%m/%Y" }}</li>{% endif %}
    {%- if joraa %}<li><a href="{{ joraa.url }}">Jornal Oficial</a>: {{ joraa.date | date: "%d/%m/%Y" }}</li>{% endif %}
    {%- if base %}<li><a href="{{ base.url }}">Contratos</a>: {{ base.date | date: "%d/%m/%Y" }}</li>{% endif %}
  </ul>
</section>

</div>

{% if site.data.ine_novidades %}
## Novos dados do INE

<ul>
{%- for n in site.data.ine_novidades limit:5 %}
  <li>{{ n.atualizado | date: "%d/%m/%Y" }}: <a href="/dados/ine/#ind={{ n.varcd }}">{{ n.indicador | xml_escape }}</a>, até {{ n.periodo }}</li>
{%- endfor %}
</ul>
{% endif %}

{%- assign sorted_items = site.posts | sort: 'date' | reverse -%}
<div class="colunas">
<section>
<h2><a href="/blog">Opinião</a></h2>
<ul>
{%- assign n = 0 -%}
{%- for post in sorted_items -%}
{%- if post.op and n < 5 -%}
  {%- assign n = n | plus: 1 -%}
  {%- assign author = site.authors | where: "short_name", post.author | first %}
  <li><a href="{{ post.url }}">{{ post.title | xml_escape }}</a>
    <span class="meta">{% if author %}{{ author.name }}{% else %}{{ post.author }}{% endif %}, {{ post.date | date: "%d/%m/%Y" }}</span></li>
{%- endif -%}
{%- endfor %}
</ul>
<p><a href="/blog">Todos os artigos de opinião</a></p>
</section>

<section class="a101">
<h2><a href="/acores-101/">Açores 101</a></h2>
<p>Primeira vez por aqui? Os Açores explicados sem jargão, em dez minutos,
com os números mais recentes e a fonte de cada um.</p>
<ul>
  <li><a href="/acores-101/#ilhas">Quantas pessoas vivem em cada ilha?</a></li>
  <li><a href="/acores-101/#quem-decide">Quem decide o quê: Assembleia, Governo, câmaras</a></li>
  <li><a href="/acores-101/#dinheiro">De onde vem e para onde vai o dinheiro da Região</a></li>
  <li><a href="/acores-101/#viver">Rendimentos, rendas, pobreza e turismo, comparados com o país</a></li>
  <li><a href="/acores-101/#palavras">Seis palavras para ler os números</a></li>
</ul>
<p><a href="/acores-101/">Começar →</a></p>
</section>
</div>

## Sobre

O açores.net pretende promover uma cidadania ativa, com informação
acessível e fidedigna. Os dados são recolhidos automaticamente das fontes
oficiais (INE, Governo Regional, Assembleia Legislativa, Jornal Oficial,
portal BASE) e podem ser descarregados e reutilizados. O código está no
[GitHub](https://github.com/fmesqg/a-ores.net-site).

<style>
.lead { font-size: 1.15em; max-width: 40em; margin-bottom: 1.25em; }
.portas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(17em, 100%), 1fr)); gap: 1em; margin-bottom: 1.5em; }
.porta { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .9em 1em .4em; background: rgba(147,161,161,.08); }
.porta h2 { font-size: 1.15em; margin: 0 0 .4em; }
.porta p { font-size: .95em; margin-bottom: .5em; }
.porta ul { margin: 0 0 .6em 1.1em; font-size: .95em; }
.colunas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(20em, 100%), 1fr)); gap: 0 2em; }
.colunas h2 { font-size: 1.3em; }
.a101 { border-left: 4px solid #268bd2; padding-left: 1em; }
.meta { color: #586e75; font-size: .85em; white-space: nowrap; }
</style>
