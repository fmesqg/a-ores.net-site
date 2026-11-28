---
title: Empresas públicas regionais
layout: default
permalink: /dados/sper/
secao: economia
description: As empresas do setor público empresarial dos Açores (SATA, EDA, Portos, Lotaçor, hospitais...), empresa a empresa - trabalhadores, volume de negócios, resultados, dívida e quanto a Região gasta com elas, segundo o Conselho das Finanças Públicas.
---
{%- assign s = site.data.sper -%}
{% include economia-nav.html %}

# Empresas públicas regionais

<p class="lead">A Região Autónoma dos Açores controla {{ s.n }} empresas:
transportes aéreos e marítimos, eletricidade, portos, lotas, os três
hospitais e outras. É o <strong>setor público empresarial regional</strong>.
Os números vêm do <a href="{{ s.url }}">relatório do Conselho das Finanças
Públicas (CFP) n.º {{ s.relatorio }}</a>, que reúne os relatórios e contas
de cada empresa.</p>

{% if s.total %}
{%- assign t = s.total -%}
<div class="numeros">
<div class="numero">
  <p class="rotulo">Trabalhadores em {{ s.ano }}</p>
  <p class="grande">{{ t.trabalhadores_t }}</p>
  <p>{% if s.emprego %}{{ s.emprego_t }} % do emprego nos Açores.{% endif %}</p>
</div>
<div class="numero">
  <p class="rotulo">Volume de negócios</p>
  <p class="grande">{{ t.vn_t }} <small>M€</small></p>
  <p>{% if s.vab_pib %}O valor acrescentado ({{ t.vab_t }} M€) equivale a {{ s.vab_pib_t }} % do PIB regional.{% endif %}</p>
</div>
<div class="numero">
  <p class="rotulo">Resultado líquido</p>
  <p class="grande">{{ t.rl_t | replace: "-", "−" }} <small>M€</small></p>
  <p>{{ t.prejuizo }} das {{ s.empresas | size | minus: s.sem_ficha.size }} empresas tiveram prejuízo.</p>
</div>
<div class="numero">
  <p class="rotulo">Passivo</p>
  <p class="grande">{{ t.passivo_t }} <small>M€</small></p>
  <p>Capital próprio de {{ t.cp_t }} M€.{% if s.cp_negativo.size > 0 %} Com capital próprio negativo: {{ s.cp_negativo | join: ", " }}.{% endif %}</p>
</div>
</div>
{% endif %}

<nav class="indice" aria-label="Nesta página">
  <a href="#empresas">Empresa a empresa</a>
  <a href="#evolucao">Ano a ano</a>
  <a href="#esforco">Quanto a Região gasta com elas</a>
  <a href="#fontes">Fontes e notas</a>
</nav>

<h2 id="empresas">Empresa a empresa, {{ s.ano }}</h2>
<p class="nota">Milhões de euros, exceto trabalhadores. Ordenadas por volume
de negócios.{% if s.maiores_ano %} "Posição" é o lugar entre as
<a href="/dados/maiores-empresas/">200 maiores empresas dos Açores</a> em
{{ s.maiores_ano }}, segundo a revista <cite>100 Maiores Empresas dos
Açores</cite> (Açoriano Oriental).{% endif %} AP: a empresa conta como administração
pública nas contas nacionais (o seu défice e a sua dívida entram nos da
Região).</p>
<div class="tabela-scroll">
<table class="sper">
  <thead><tr>
    <th scope="col">Empresa</th>
    <th scope="col" class="n">Trabalhadores</th>
    <th scope="col" class="n">Volume de negócios</th>
    <th scope="col" class="n">Resultado líquido</th>
    <th scope="col" class="n">Capital próprio</th>
    <th scope="col" class="n">Passivo</th>
    {% if s.maiores_ano %}<th scope="col" class="n">Posição</th>{% endif %}
  </tr></thead>
  <tbody>
  {%- for e in s.empresas %}
  <tr>
    <th scope="row"><abbr title="{{ e.empresa | escape }}">{{ e.nome }}</abbr>{% if e.ap %} <span class="tag" title="Conta como administração pública nas contas nacionais">AP</span>{% endif %}<br><small>{{ e.setor }}{% if e.participacao %} · Região: {{ e.participacao_t }} %{% if e.acionista != "RAA" and e.acionista != "" %} via {{ e.acionista }}{% endif %}{% endif %}</small></th>
    {%- if e.vn %}
    <td class="n">{{ e.trabalhadores_t }}</td>
    <td class="n">{{ e.vn_t }}</td>
    <td class="n{% if e.rl < 0 %} neg{% endif %}">{{ e.rl_t | replace: "-", "−" }}</td>
    <td class="n{% if e.cp < 0 %} neg{% endif %}">{{ e.cp_t | replace: "-", "−" }}</td>
    <td class="n">{{ e.passivo_t }}</td>
    {%- else %}
    <td colspan="5" class="nota">Sem ficha no relatório do CFP.</td>
    {%- endif %}
    {% if s.maiores_ano %}<td class="n">{% if e.posicao %}{{ e.posicao }}.ª{% endif %}</td>{% endif %}
  </tr>
  {%- endfor %}
  </tbody>
  <tfoot><tr>
    <th scope="row">Total</th>
    <td class="n">{{ s.total.trabalhadores_t }}</td>
    <td class="n">{{ s.total.vn_t }}</td>
    <td class="n neg">{{ s.total.rl_t | replace: "-", "−" }}</td>
    <td class="n">{{ s.total.cp_t }}</td>
    <td class="n">{{ s.total.passivo_t }}</td>
    {% if s.maiores_ano %}<td></td>{% endif %}
  </tr></tfoot>
</table>
</div>
{%- assign notas = s.empresas | where_exp: "e", "e.nota != ''" %}
{% if notas.size > 0 %}
<ul class="nota">
{%- for e in notas %}
  <li>{{ e.nome }}: {{ e.nota }}</li>
{%- endfor %}
</ul>
{% endif %}

<h2 id="evolucao">Ano a ano</h2>
<p class="nota">Soma das empresas com ficha no relatório do CFP, em milhões
de euros.</p>
<div class="tabela-scroll">
<table class="sper">
  <thead><tr><th scope="col"></th>{% for a in s.totais %}<th scope="col" class="n">{{ a.ano }}</th>{% endfor %}</tr></thead>
  <tbody>
    <tr><th scope="row">Trabalhadores</th>{% for a in s.totais %}<td class="n">{{ a.trabalhadores_t }}</td>{% endfor %}</tr>
    <tr><th scope="row">Volume de negócios</th>{% for a in s.totais %}<td class="n">{{ a.vn_t }}</td>{% endfor %}</tr>
    <tr><th scope="row">Gastos com pessoal</th>{% for a in s.totais %}<td class="n">{{ a.pessoal_t }}</td>{% endfor %}</tr>
    <tr><th scope="row">Valor acrescentado bruto</th>{% for a in s.totais %}<td class="n">{{ a.vab_t }}</td>{% endfor %}</tr>
    <tr><th scope="row">EBITDA</th>{% for a in s.totais %}<td class="n">{{ a.ebitda_t }}</td>{% endfor %}</tr>
    <tr><th scope="row">Resultado líquido</th>{% for a in s.totais %}<td class="n{% if a.rl < 0 %} neg{% endif %}">{{ a.rl_t | replace: "-", "−" }}</td>{% endfor %}</tr>
    <tr><th scope="row">Empresas com prejuízo</th>{% for a in s.totais %}<td class="n">{{ a.prejuizo }}</td>{% endfor %}</tr>
    <tr><th scope="row">Capital próprio</th>{% for a in s.totais %}<td class="n">{{ a.cp_t }}</td>{% endfor %}</tr>
    <tr><th scope="row">Passivo</th>{% for a in s.totais %}<td class="n">{{ a.passivo_t }}</td>{% endfor %}</tr>
  </tbody>
</table>
</div>

<h3>Resultado líquido de cada empresa</h3>
<div class="tabela-scroll">
<table class="sper">
  <thead><tr><th scope="col">Empresa</th>{% for a in s.anos %}<th scope="col" class="n">{{ a.ano }}</th>{% endfor %}</tr></thead>
  <tbody>
  {%- for e in s.empresas %}{% if e.vn %}
  <tr><th scope="row">{{ e.nome }}</th>{% for x in e.rl_anos %}<td class="n{% if x.v < 0 %} neg{% endif %}">{% if x.v_t %}{{ x.v_t | replace: "-", "−" }}{% else %}–{% endif %}</td>{% endfor %}</tr>
  {%- endif %}{% endfor %}
  </tbody>
</table>
</div>

{% if s.esforco %}
{%- assign f = s.esforco -%}
<h2 id="esforco">Quanto a Região gasta com elas</h2>
<p>O <strong>esforço financeiro líquido</strong> é o que a Região paga às
suas empresas (transferências, indemnizações compensatórias, aumentos de
capital, empréstimos, dívida assumida) menos o que recebe delas
(dividendos). Em {{ f.ano }} foi de <strong>{{ f.total_t }} M€</strong>,
segundo o CFP, <strong>sem contar os hospitais</strong>.</p>
<div class="tabela-scroll">
<table class="sper">
  <thead><tr><th scope="col">Milhões de euros</th>{% for a in f.anos %}<th scope="col" class="n">{{ a.ano }}</th>{% endfor %}</tr></thead>
  <tbody>
  {%- for l in f.linhas %}
  <tr{% if l.total %} class="total"{% endif %}><th scope="row">{{ l.rubrica }}{% if l.unidade != "M€" %} ({{ l.unidade }}){% endif %}</th>{% for x in l.valores %}<td class="n">{{ x.v_t | default: "–" }}</td>{% endfor %}</tr>
  {%- endfor %}
  </tbody>
</table>
</div>
{% if f.antes %}
<p class="aviso"><strong>Atenção às comparações.</strong> No relatório
anterior (<a href="{{ f.antes.url }}">n.º {{ f.antes.relatorio }}</a>) o
esforço de {{ f.antes.ano }} era de {{ f.antes.valor_t }} M€; no relatório
n.º {{ f.relatorio }} o mesmo ano aparece com {{ f.antes.agora_t }} M€. O
CFP mudou o método: passou a deixar de fora as transferências para as
empresas da saúde (os hospitais), para comparar com o setor empresarial do
Estado. Não some nem compare números dos dois relatórios.</p>
{% endif %}
<p class="fonte">{{ f.nota }}</p>
{% endif %}

<h2 id="fontes">Fontes e notas</h2>
<ul>
  <li>Conselho das Finanças Públicas, <a href="{{ s.url }}">relatório n.º
  {{ s.relatorio }}</a>: fichas individuais das empresas
  (<a href="{{ s.ficheiro }}">Excel</a>), lista das empresas, peso na
  economia e esforço financeiro. O CFP lê os relatórios e contas de cada
  empresa; o valor acrescentado é calculado numa ótica próxima das contas
  nacionais.</li>
  <li>O CFP conta no setor as empresas em que a Região tem influência
  dominante, direta ou através de outra empresa pública (por isso a EDA,
  com 50,1 %, conta, e a Globaleda, detida pela EDA, também).
  {% if s.sem_ficha.size > 0 %}{{ s.sem_ficha | join: ", " }} não tem ficha
  própria.{% endif %}</li>
  <li>Dados abertos: <a href="/dados/sper.csv">sper.csv</a> (todos os
  indicadores, empresa a empresa, desde 2022),
  <a href="/dados/sper_empresas.csv">sper_empresas.csv</a> (lista e
  participações) e <a href="/dados/sper_regiao.csv">sper_regiao.csv</a>
  (peso na economia e esforço financeiro, por relatório). Atualizados todas
  as semanas a partir do site do CFP.</li>
  <li>As explicações desta página são do açores.net, não são texto
  oficial.</li>
</ul>

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(9.5em, 100%), 1fr)); gap: .9em; margin: 1.2em 0 1.5em; }
.indice { display: flex; flex-wrap: wrap; gap: .3em 1em; margin: 0 0 1em; font-size: .95em; }
table.sper th[scope="row"] { font-weight: normal; }
table.sper thead th, table.sper thead th.n, table.sper .n small { white-space: normal; }
table.sper .neg { color: #b5442c; }
table.sper tfoot th, table.sper tfoot td, table.sper tr.total th, table.sper tr.total td { font-weight: bold; }
table.sper abbr { text-decoration: none; }
.tag { font-size: .7em; border: 1px solid var(--s1); border-radius: 4px; padding: 0 .25em; vertical-align: middle; }
.nota, .fonte { font-size: .85em; color: var(--s01); }
.aviso { border-left: 4px solid #b58900; padding: .4em .8em; background: rgba(181,137,0,.08); }
@media (prefers-color-scheme: dark) { .nota, .fonte { color: var(--s01); } table.sper .neg { color: #e0805f; } }
</style>
