---
title: Economia dos Açores
nav_title: Economia
layout: default
permalink: /economia/
secao: economia
description: A economia dos Açores num só sítio - preços, emprego, PIB por ilha, as empresas públicas regionais e as maiores empresas, com ligação às fontes oficiais.
---
{%- assign s = site.data.resumo.srea -%}
{%- assign p = site.data.sper -%}
{%- assign m = site.data.maiores -%}
{% include economia-nav.html %}

# Economia dos Açores

<p class="lead">Como está a economia dos Açores e quem a faz: os indicadores
do Serviço Regional de Estatística, as empresas que a Região controla e as
maiores empresas com sede nas ilhas.</p>

<div class="numeros">
{%- if s.pib_hab %}
<div class="numero">
  <p class="rotulo">PIB de {{ s.pib_hab.ano }}{% if s.pib_hab.provisorio %} (provisório){% endif %}</p>
  <p class="grande">{{ s.pib_hab.total_mm_t }} <small>mil milhões €</small></p>
  <p>{{ s.pib_hab.acores_t }} € por habitante.</p>
  <p class="fonte">SREA, <a href="/dados/srea/#ilhas">contas regionais</a>.</p>
</div>
{%- endif %}
{%- if s.ipc %}
<div class="numero">
  <p class="rotulo">Inflação</p>
  <p class="grande">{{ s.ipc.valor_t }} <small>%</small></p>
  <p>Subida dos preços entre {{ s.ipc.antes }} e {{ s.ipc.periodo }}.</p>
  <p class="fonte">SREA, <a href="/dados/srea/#precos">IPC</a>.</p>
</div>
{%- endif %}
{%- if s.desemprego %}
<div class="numero">
  <p class="rotulo">Desemprego</p>
  <p class="grande">{{ s.desemprego.valor_t }} <small>%</small></p>
  <p>No {{ s.desemprego.periodo }} ({{ s.desemprego.antes_t }} % um ano antes).</p>
  <p class="fonte">SREA, <a href="/dados/srea/#emprego">Inquérito ao Emprego</a>.</p>
</div>
{%- endif %}
{%- if p.vab_pib %}
<div class="numero">
  <p class="rotulo">Empresas públicas regionais</p>
  <p class="grande">{{ p.vab_pib_t }} <small>% do PIB</small></p>
  <p>{{ p.total.trabalhadores_t }} trabalhadores ({{ p.emprego_t }} % do emprego) em {{ p.peso_ano }}.</p>
  <p class="fonte">CFP, <a href="/dados/sper/">relatório n.º {{ p.relatorio }}</a>.</p>
</div>
{%- endif %}
</div>

<div class="portas">

<section class="porta">
<h2><a href="/dados/srea/">Indicadores, mês a mês</a></h2>
<p>Preços, emprego, atividade económica, consumo, turistas por ilha e o que
cada ilha produz, com os números mais recentes do SREA.</p>
<ul>
  <li><a href="/dados/srea/#precos">O que mais subiu de preço?</a></li>
  <li><a href="/dados/srea/#emprego">Há mais ou menos desemprego?</a></li>
  <li><a href="/dados/srea/#turismo">Quantos turistas vão a cada ilha?</a></li>
  <li><a href="/dados/srea/#ilhas">Qual é o PIB por habitante de cada ilha?</a></li>
</ul>
</section>

<section class="porta">
<h2><a href="/dados/sper/">Empresas públicas regionais</a></h2>
<p>SATA, EDA, Portos dos Açores, Atlânticoline, Lotaçor, os hospitais e
outras {% if p.n %}(são {{ p.n }}){% endif %}: trabalhadores, contas e
quanto a Região gasta com elas.{% if p.total %} Em {{ p.ano }} tiveram um
resultado líquido de {{ p.total.rl_t | replace: "-", "−" }} M€.{% endif %}</p>
<ul>
  <li><a href="/dados/sper/#empresas">Quanto fatura e quanto perde cada empresa?</a></li>
  <li><a href="/dados/sper/#evolucao">Os prejuízos estão a aumentar?</a></li>
  <li><a href="/dados/sper/#esforco">Quanto paga a Região às suas empresas?</a></li>
</ul>
</section>

<section class="porta">
<h2><a href="/dados/maiores-empresas/">Maiores empresas</a></h2>
<p>As {{ m.n | default: 200 }} empresas com sede nos Açores que mais
faturaram{% if m.ano %} em {{ m.ano }}{% endif %}, por setor e por ilha,
segundo a revista <cite>100 Maiores Empresas dos Açores</cite> (Açoriano
Oriental).{% if m.top10_pct %}
As dez maiores fazem {{ m.top10_pct }} % do volume de negócios das
{{ m.n }}.{% endif %}</p>
<ul>
  <li><a href="/dados/maiores-empresas/#lista">Quais são as maiores empresas?</a></li>
  <li><a href="/dados/maiores-empresas/#setores">Que setores pesam mais?</a></li>
  <li><a href="/dados/maiores-empresas/#ilhas">Onde estão as sedes?</a></li>
</ul>
</section>

</div>

<p class="fonte">Para as contas do Governo Regional (receita, despesa,
dívida), veja as <a href="/financas/">Finanças da Região</a>; para
rendimentos, rendas e população por concelho e freguesia, as
<a href="/dados/ine/">estatísticas do INE</a>.</p>

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(9.5em, 100%), 1fr)); gap: .9em; margin: 1.2em 0 1.5em; }
.numero { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .8em 1em .3em; background: rgba(147,161,161,.08); }
.numero p { margin-bottom: .4em; font-size: .95em; }
.numero .rotulo { font-weight: bold; margin-bottom: .2em; }
.numero .grande { font-size: 1.8em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.numero .grande small { font-size: .5em; font-weight: normal; }
.portas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(18em, 100%), 1fr)); gap: 1em; margin-bottom: 1.5em; }
.porta { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .9em 1em .4em; background: rgba(147,161,161,.08); }
.porta h2 { font-size: 1.2em; margin: 0 0 .4em; }
.porta p, .porta ul { font-size: .95em; }
.porta ul { margin-left: 1.1em; }
.fonte { font-size: .85em; color: #586e75; }
@media (prefers-color-scheme: dark) { .fonte { color: #93a1a1; } }
</style>
