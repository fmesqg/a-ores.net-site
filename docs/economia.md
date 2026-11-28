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

{%- assign i = site.data.resumo.ine -%}
{%- assign trio = "0014103,0014663,0012136" | split: "," %}
<div class="numeros">
{%- for v in trio %}
{%- assign x = i[v] -%}
{%- if v == "0014103" %}{% assign u = " €" %}{% else %}{% assign u = " %" %}{% endif -%}
{%- if x.acores %}
<div class="numero">
  {%- case v -%}
  {%- when "0014103" %}<p class="rotulo">PIB por habitante, {{ x.periodo }}</p>
  <p class="grande">{{ x.acores_t }} <small>€</small></p>
  {%- when "0014663" %}<p class="rotulo">Inflação, {{ x.periodo | downcase }}</p>
  <p class="grande">{{ x.acores_t }} <small>%</small></p>
  {%- when "0012136" %}<p class="rotulo">Desemprego, {{ x.periodo | downcase }}</p>
  <p class="grande">{{ x.acores_t }} <small>%</small></p>
  {%- endcase %}
  <p class="ref">Madeira {{ x.madeira_t }}{{ u }} · Portugal {{ x.pt_t }}{{ u }}</p>
  <p class="fonte">INE, <a href="/dados/ine/#ind={{ v }}">série</a> · <a href="{{ x.url }}">fonte</a></p>
</div>
{%- endif %}
{%- endfor %}
</div>

<p class="fonte">A inflação é a variação dos preços face ao mesmo mês do ano
anterior. O desemprego vem do Inquérito ao Emprego, por amostragem. O SREA
publica as mesmas séries para os Açores, com mais detalhe, nas
<a href="/dados/srea/">Estatísticas</a>; o PIB do SREA para {{ s.pib_hab.ano }} é
uma estimativa mais recente ({{ s.pib_hab.acores_t }} € por habitante).</p>

{%- assign sp = site.data.resumo.salario_pib %}
{% if sp.locais %}
<h3 id="salarios">Salários e PIB por habitante, {{ sp.ano }}</h3>

{% assign a = sp.locais[0] -%}
<p>Nos Açores, metade dos contribuintes declarou ao IRS menos de
<strong>{{ a.mediana_t }} €</strong> brutos no ano: {{ a.mediana_pct }} % do
PIB por habitante ({{ a.pib_t }} €).</p>

<ul>
  <li><strong>PIB por habitante</strong>: o que a economia produz num ano a dividir por todos os residentes.</li>
  <li><strong>Mediana do rendimento bruto</strong>: metade dos contribuintes declarou menos do que este valor ao IRS.</li>
  <li><strong>Ganho médio × 14</strong>: o ganho médio mensal dos trabalhadores por conta de outrem, vezes 14 meses.</li>
</ul>

<div class="tabela">
<table class="salarios">
<thead><tr><th scope="col"></th><th scope="col">PIB por habitante</th><th scope="col">Mediana do rendimento bruto</th><th scope="col">Ganho médio × 14</th></tr></thead>
<tbody>
{%- for l in sp.locais %}
<tr>
  <th scope="row">{{ l.local }}</th>
  <td>{{ l.pib_t }} €</td>
  <td>{{ l.mediana_t }} €<span class="barra"><span style="width: {{ l.mediana_pct }}%"></span></span><small>{{ l.mediana_pct }} % do PIB por habitante</small></td>
  <td>{{ l.ganho_ano_t }} €<span class="barra"><span style="width: {{ l.ganho_pct }}%"></span></span><small>{{ l.ganho_pct }} % do PIB por habitante</small></td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>

<ul class="notas">
  <li>O PIB por habitante não é um rendimento: inclui lucros, impostos sobre
  a produção e a depreciação, e divide por toda a população, incluindo
  crianças e reformados.</li>
  <li>A mediana do IRS é por sujeito passivo e inclui pensões e outros
  rendimentos declarados; fica de fora quem não entrega declaração.</li>
  <li>O ganho médio vem dos Quadros de Pessoal: trabalhadores por conta de
  outrem a tempo completo, sem a administração pública. A média puxa para
  cima com os salários altos. Multiplicar por 14 é uma aproximação do
  açores.net ao valor anual.</li>
</ul>

<p class="fonte">INE: <a href="{{ sp.url_pib }}">PIB por habitante</a>,
<a href="{{ sp.url_mediana }}">rendimento bruto mediano</a>,
<a href="{{ sp.url_ganho }}">ganho médio mensal</a>. As percentagens são
cálculo do açores.net.</p>
{% endif %}

<p class="fonte">Mais números nas <a href="/dados/srea/">Estatísticas</a>:
preços, emprego, turismo e PIB por ilha (SREA) e rendimentos, rendas e
população por concelho e freguesia (<a href="/dados/ine/">INE</a>).</p>

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.divisao { margin: 1.2em 0 1.5em; }
.divisao figcaption { font-weight: bold; margin-bottom: .4em; }
.barra-dupla { display: flex; gap: 2px; border-radius: 6px; overflow: hidden; font-size: .9em; }
.barra-dupla span { padding: .45em .6em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.barra-dupla .pub { background: #268bd2; color: var(--sobre-acento); }
.barra-dupla .priv { background: rgba(147,161,161,.25); }
.lados { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(22em, 100%), 1fr)); gap: 1.5em; }
.lado h2 { margin-top: .3em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(9.5em, 100%), 1fr)); gap: .9em; margin: .6em 0 1em; }
.perguntas { margin-left: 1.1em; font-size: .95em; }
.numero .ref { font-size: .9em; }
.tabela { overflow-x: auto; }
.salarios { border-collapse: collapse; font-size: .95em; }
.salarios th, .salarios td { text-align: left; vertical-align: top; padding: .4em .6em; }
.salarios td small { display: block; font-size: .8em; color: var(--s01); }
.barra { display: block; width: 9em; max-width: 100%; height: 6px; margin: .3em 0 .15em; background: rgba(147,161,161,.25); border-radius: 3px; }
.barra span { display: block; height: 6px; background: #268bd2; border-radius: 3px; }
.notas { font-size: .9em; max-width: 42em; }
.fonte { font-size: .85em; color: var(--s01); }
@media (prefers-color-scheme: dark) { .fonte, .salarios td small { color: var(--s01); } .barra-dupla .pub { background: #2f7fb8; } }
</style>
