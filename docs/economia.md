---
title: Economia dos Açores
nav_title: Economia
layout: default
permalink: /economia/
secao: economia
description: A economia dos Açores dividida em setor público (administração regional, Estado, autarquias e empresas públicas) e setor privado (as maiores empresas), com os indicadores do SREA e ligação às fontes oficiais.
---
{%- assign s = site.data.resumo.srea -%}
{%- assign p = site.data.sper -%}
{%- assign m = site.data.maiores -%}
{%- assign e = site.data.publico -%}
{%- assign w = e.peso -%}
{% include economia-nav.html %}

# Economia dos Açores

<p class="lead">Quem faz a economia dos Açores: o setor público (a Região, o
Estado, as autarquias e as empresas públicas) e o setor privado. Os números
vêm das fontes oficiais e de uma revista, ligadas em cada caso.</p>

{% if w %}
<figure class="divisao" aria-label="Emprego nos Açores: público e privado">
  <figcaption>Pessoas empregadas nos Açores no {{ w.periodo }} ({{ w.emprego_mil_t }} mil)</figcaption>
  <div class="barra-dupla">
    <span class="pub" style="width: {{ w.publico_pct }}%"><b>Setor público ≈ {{ w.publico_pct }} %</b></span>
    <span class="priv" style="width: {{ w.privado_pct }}%"><b>Privado e outros ≈ {{ w.privado_pct }} %</b></span>
  </div>
  <p class="fonte">Cálculo do açores.net com dados da DGAEP, do CFP e do SREA;
  é uma ordem de grandeza (<a href="/economia/setor-publico/#peso">como se calcula</a>).</p>
</figure>
{% endif %}

<div class="lados">

<section class="lado">
<h2 id="publico">Setor público</h2>
<div class="numeros">
{%- if e.ap %}
<div class="numero">
  <p class="rotulo">Administrações públicas</p>
  <p class="grande">{{ e.ap_t }}</p>
  <p>Postos de trabalho na Região, no Estado e nas autarquias nos Açores ({{ e.periodo }}). {{ e.ar_t }} são da Administração Regional.</p>
  <p class="fonte">DGAEP, <a href="/economia/setor-publico/">emprego público</a>.</p>
</div>
{%- endif %}
{%- if p.vab_pib %}
<div class="numero">
  <p class="rotulo">Empresas públicas regionais</p>
  <p class="grande">{{ p.vab_pib_t }} <small>% do PIB</small></p>
  <p>{{ p.n }} empresas, {{ p.total.trabalhadores_t }} trabalhadores e um resultado de {{ p.total.rl_t | replace: "-", "−" }} M€ em {{ p.ano }}.</p>
  <p class="fonte">CFP, <a href="/dados/sper/">relatório n.º {{ p.relatorio }}</a>.</p>
</div>
{%- endif %}
</div>
<ul class="perguntas">
  <li><a href="/economia/setor-publico/#carreiras">Quem trabalha para o setor público, e em que profissões?</a></li>
  <li><a href="/economia/setor-publico/#secretarias">Quantas pessoas tem cada secretaria regional?</a></li>
  <li><a href="/dados/sper/#empresas">Quanto fatura e quanto perde cada empresa pública?</a></li>
  <li><a href="/dados/sper/#esforco">Quanto paga a Região às suas empresas?</a></li>
  <li><a href="/financas/">Quanto a Região cobra, gasta e deve?</a></li>
</ul>
</section>

<section class="lado">
<h2 id="privado">Setor privado</h2>
<div class="numeros">
{%- if m.privadas %}
<div class="numero">
  <p class="rotulo">Maiores empresas privadas</p>
  <p class="grande">{{ m.privadas_vn_t }} <small>M€</small></p>
  <p>Volume de negócios das {{ m.privadas }} privadas entre as {{ m.n }} maiores empresas com sede nos Açores em {{ m.ano }}, com {{ m.privadas_trabalhadores_t }} trabalhadores.</p>
  <p class="fonte">Revista <cite>100 Maiores Empresas dos Açores</cite>, <a href="/dados/maiores-empresas/">ranking</a>.</p>
</div>
{%- endif %}
{%- if w %}
<div class="numero">
  <p class="rotulo">Emprego fora do setor público</p>
  <p class="grande">≈ {{ w.privado_pct }} <small>%</small></p>
  <p>Das pessoas empregadas: empresas privadas, conta própria, associações e outras organizações.</p>
  <p class="fonte">Cálculo do açores.net, <a href="/economia/setor-publico/#peso">como se calcula</a>.</p>
</div>
{%- endif %}
</div>
<ul class="perguntas">
  <li><a href="/dados/maiores-empresas/#lista">Quais são as maiores empresas?</a></li>
  <li><a href="/dados/maiores-empresas/#setores">Que setores pesam mais?</a></li>
  <li><a href="/dados/maiores-empresas/#ilhas">Onde estão as sedes?</a></li>
</ul>
<p class="fonte">O ranking inclui também {{ m.publicas }} empresas públicas
({{ m.publicas_pct }} % do volume de negócios), assinaladas na lista.</p>
</section>

</div>

<h2 id="conjuntura">Como está a economia</h2>

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
</div>

<p class="fonte">Mais números nas <a href="/dados/srea/">Estatísticas</a>:
preços, emprego, turismo e PIB por ilha (SREA) e rendimentos, rendas e
população por concelho e freguesia (<a href="/dados/ine/">INE</a>).</p>

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.divisao { margin: 1.2em 0 1.5em; }
.divisao figcaption { font-weight: bold; margin-bottom: .4em; }
.barra-dupla { display: flex; gap: 2px; border-radius: 6px; overflow: hidden; font-size: .9em; }
.barra-dupla span { padding: .45em .6em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.barra-dupla .pub { background: #268bd2; color: #fdf6e3; }
.barra-dupla .priv { background: rgba(147,161,161,.25); }
.lados { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(22em, 100%), 1fr)); gap: 1.5em; }
.lado h2 { margin-top: .3em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(9.5em, 100%), 1fr)); gap: .9em; margin: .6em 0 1em; }
.numero { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .8em 1em .3em; background: rgba(147,161,161,.08); }
.numero p { margin-bottom: .4em; font-size: .95em; }
.numero .rotulo { font-weight: bold; margin-bottom: .2em; }
.numero .grande { font-size: 1.8em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.numero .grande small { font-size: .5em; font-weight: normal; }
.perguntas { margin-left: 1.1em; font-size: .95em; }
.fonte { font-size: .85em; color: #586e75; }
@media (prefers-color-scheme: dark) { .fonte { color: #93a1a1; } .barra-dupla .pub { background: #2f7fb8; } }
</style>
