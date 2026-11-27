---
title: Finanças da Região
nav_title: Finanças
layout: default
permalink: /financas/
secao: financas
description: Quanto a Região Autónoma dos Açores cobra, gasta e deve - a execução orçamental mês a mês e o que o Tribunal de Contas diz da Conta de cada ano, com ligação às fontes oficiais.
---
{%- assign b = site.data.resumo.beo -%}
{%- assign t = site.data.resumo.tdc -%}
{%- assign u = site.data.beo_ultimo -%}
{% include financas-nav.html %}

# Finanças da Região

<p class="lead">Quanto a Região cobra, quanto gasta e quanto deve. Há duas
fontes: os <strong>boletins de execução orçamental</strong>, que o Governo
Regional publica todos os meses, e o <strong>parecer do Tribunal de
Contas</strong>, que audita a Conta de cada ano.</p>

{% if b or t %}
<div class="numeros">
{%- if b %}
<div class="numero">
  <p class="rotulo">{% if b.saldo < 0 %}Défice{% else %}Excedente{% endif %} de {{ b.ano }}</p>
  <p class="grande">{{ b.saldo_abs | round: 1 | replace: ".", "," }} <small>M€</small></p>
  <p>Receita de {{ b.receita_t }} M€, despesa de {{ b.despesa_t }} M€.</p>
  <p class="fonte">Boletim de execução de <a href="{{ b.boletim }}">dezembro de {{ b.ano }}</a>
  (provisório). Receita e despesa efetivas, valores consolidados.</p>
</div>
{%- endif %}
{%- if t.divida %}
<div class="numero">
  <p class="rotulo">Dívida total no fim de {{ t.conta }}</p>
  <p class="grande">{{ t.divida_t }} <small>M€</small></p>
  <p>{% if t.divida_var %}Mais {{ t.divida_var_t }} % do que no ano anterior.{% endif %}</p>
  <p class="fonte">Tribunal de Contas, <a href="{{ t.url }}">parecer sobre a Conta de {{ t.conta }}</a>.
  Setor público administrativo regional.</p>
</div>
{%- endif %}
{%- if t.receita_fora %}
<div class="numero">
  <p class="rotulo">Fora da Conta de {{ t.conta }}</p>
  <p class="grande">{{ t.receita_fora_t }} <small>M€ de receita</small></p>
  <p>e {{ t.despesa_fora_t }} M€ de despesa que não foram registados na Conta.</p>
  <p class="fonte">Tribunal de Contas, <a href="{{ t.url }}">parecer sobre a Conta de {{ t.conta }}</a>
  (reserva ao juízo sobre a Conta).</p>
</div>
{%- endif %}
</div>
{% endif %}

<div class="portas">

<section class="porta">
<h2><a href="/dados/beo/">Execução orçamental, mês a mês</a></h2>
<p>O que entrou e saiu dos cofres da Região em cada mês: impostos,
transferências, salários, compras, juros, despesa por secretaria e por
função (saúde, educação, transportes).{% if u.periodo %} Último boletim:
<a href="{{ u.url }}">{{ u.periodo }}</a>.{% endif %}</p>
<ul>
  <li><a href="/dados/beo/#quadro=sintese-global&modo=acum">Há défice ou excedente este ano?</a></li>
  <li><a href="/dados/beo/#quadro=receita-fiscal-do-gra&grafico=anos">Quanto rendem o IRS e o IVA, mês a mês?</a></li>
  <li><a href="/dados/beo/#quadro=despesa-do-gra-por-departamento">Quanto gasta cada secretaria?</a></li>
  <li><a href="/dados/beo/#quadro=despesa-do-gra-por-funcao&modo=acum&grafico=anos">Quanto vai para a saúde, ano a ano?</a></li>
</ul>
</section>

<section class="porta">
<h2><a href="/dados/tdc/">Tribunal de Contas, ano a ano</a></h2>
<p>O juízo do Tribunal sobre a Conta de cada ano, as reservas e ênfases,
a dívida, e o que o Governo fez às recomendações.{% if t.conta %} Último
parecer: <a href="{{ t.url }}">Conta de {{ t.conta }}</a>, com
{{ t.reservas }} reservas e {{ t.recomendacoes }} recomendações.{% endif %}</p>
{%- if t.avaliadas %}
<p>Das {{ t.avaliadas }} recomendações anteriores que o Tribunal voltou a
avaliar:
{% for e in t.estados %}{{ e.n }} {{ e.nome | downcase }}{% if e.n != 1 %}s{% endif %}{% if forloop.last %}.{% elsif forloop.rindex == 2 %} e {% else %}, {% endif %}{% endfor %}
A mais antiga vem de {{ t.desde }}.</p>
{%- endif %}
<ul>
  <li><a href="/dados/tdc/#parecer">O que disse o Tribunal sobre cada Conta?</a></li>
  <li><a href="/dados/tdc/#numeros">Dívida, défice e dinheiro fora da Conta, ano a ano</a></li>
  <li><a href="/dados/tdc/#recomendacoes">Que recomendações ficaram por cumprir?</a></li>
</ul>
</section>

<section class="porta">
<h2><a href="/financas/camaras/">Câmaras municipais, por habitante</a></h2>
<p>Receitas e despesas das 19 câmaras divididas pela população, ao lado do
rendimento, do turismo, do RSI e dos contratos de cada câmara no BASE.</p>
<ul>
  <li><a href="/financas/camaras/#despesa">Quanto gasta cada câmara por habitante?</a></li>
  <li><a href="/financas/camaras/#tamanho">Os concelhos pequenos gastam mais?</a></li>
  <li><a href="/financas/camaras/#cruzar">Contratos, rendimento e turismo no mesmo concelho</a></li>
</ul>
</section>

</div>

## Como se ligam

<dl class="ligam">
  <dt>Orçamento</dt>
  <dd>O que o Governo prevê cobrar e gastar. É aprovado pela Assembleia
  Legislativa, normalmente no fim do ano anterior.</dd>
  <dt>Boletim de execução orçamental (todos os meses)</dt>
  <dd>O que foi de facto cobrado e pago até ao fim de cada mês. Os valores
  são provisórios.</dd>
  <dt>Conta da Região (uma vez por ano)</dt>
  <dd>Os valores finais do ano, do setor público administrativo regional.
  O Governo apresenta-a à Assembleia.</dd>
  <dt>Parecer do Tribunal de Contas (cerca de um ano depois)</dt>
  <dd>A auditoria à Conta: se está certa, o que não se pode confirmar
  (reservas), o que é preocupante (ênfases) e o que deve mudar
  (recomendações). A Assembleia vota a Conta depois de o ler.</dd>
</dl>

<p class="fonte">Explicações do açores.net, não são texto oficial. O défice do boletim de dezembro e o da Conta não coincidem exatamente: o
boletim é provisório, e a Conta tem os valores finais e abrange mais
entidades. Os termos técnicos
estão no <a href="/dados/beo/#glossario">glossário da execução
orçamental</a>, com ligação aos textos legais.</p>

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(13em, 100%), 1fr)); gap: .9em; margin: 1.2em 0 1.5em; }
.numero { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .8em 1em .3em; background: rgba(147,161,161,.08); }
.numero p { margin-bottom: .4em; font-size: .95em; }
.numero .rotulo { font-weight: bold; margin-bottom: .2em; }
.numero .grande { font-size: 1.8em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.numero .grande small { font-size: .5em; font-weight: normal; }
.portas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(20em, 100%), 1fr)); gap: 1em; margin-bottom: 1.5em; }
.porta { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .9em 1em .4em; background: rgba(147,161,161,.08); }
.porta h2 { font-size: 1.2em; margin: 0 0 .4em; }
.porta p, .porta ul { font-size: .95em; }
.porta ul { margin-left: 1.1em; }
.ligam { max-width: 42em; }
.ligam dt { font-weight: bold; margin-top: .7em; }
.ligam dd { margin: .15em 0 0 0; }
.fonte { font-size: .85em; color: #586e75; }
@media (prefers-color-scheme: dark) { .fonte { color: #93a1a1; } }
</style>
