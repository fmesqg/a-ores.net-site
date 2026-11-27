---
title: Setor público dos Açores
layout: default
permalink: /economia/setor-publico/
secao: economia
description: Quantas pessoas trabalham para a Região, o Estado e as autarquias nos Açores, em que carreiras e secretarias, quanto ganham e que peso têm no emprego, com dados da DGAEP (SIOE), do SREA e do CFP.
---
{%- assign e = site.data.publico -%}
{%- assign p = site.data.sper -%}
{%- assign w = e.peso -%}
{% include economia-nav.html %}

# Setor público dos Açores

<p class="lead">Quem trabalha para o setor público nos Açores: a administração
regional, os serviços do Estado e as autarquias, segundo o registo oficial do
emprego público, e as empresas que a Região controla. Para o dinheiro
(receita, despesa e dívida da Região) veja as
<a href="/financas/">Finanças da Região</a>.</p>

{% if e.ap %}
<div class="numeros">
<div class="numero">
  <p class="rotulo">Administrações públicas nos Açores</p>
  <p class="grande">{{ e.ap_t }}</p>
  <p>Postos de trabalho na Região, no Estado e nas autarquias a {{ e.periodo }}{% if e.provisorio %} (provisório){% endif %}{% if e.ap_var %}, {% if e.ap_var > 0 %}mais {{ e.ap_var_t }}{% else %}menos {{ e.ap_var_t | remove: "-" }}{% endif %} do que um ano antes{% endif %}.</p>
  <p class="fonte">DGAEP, <a href="{{ e.pagina }}">SIEP</a>, quadro 1.7.</p>
</div>
<div class="numero">
  <p class="rotulo">Administração Regional</p>
  <p class="grande">{{ e.ar_t }}</p>
  <p>Postos de trabalho no Governo Regional, nos seus serviços e nos hospitais; eram {{ e.ar_inicio_t }} no fim de {{ e.ano_inicio }}.</p>
  <p class="fonte">DGAEP, <a href="{{ e.pagina }}">SIEP</a>, quadro 1.1.</p>
</div>
{%- if p.total %}
<div class="numero">
  <p class="rotulo">Empresas públicas regionais</p>
  <p class="grande">{{ p.total.trabalhadores_t }}</p>
  <p>Trabalhadores em {{ p.ano }}{% if w.mercado %}; {{ w.mercado_t }} em empresas que não contam como administração pública (SATA, EDA, Portos dos Açores…){% endif %}.</p>
  <p class="fonte">CFP, <a href="/dados/sper/">empresas públicas</a>.</p>
</div>
{%- endif %}
{%- if w %}
<div class="numero">
  <p class="rotulo">Peso no emprego</p>
  <p class="grande">≈ {{ w.publico_pct }} <small>%</small></p>
  <p>Cerca de 1 em cada {{ w.um_em }} pessoas empregadas nos Açores trabalha para o setor público. <a href="#peso">Como se calcula</a>.</p>
  <p class="fonte">Cálculo do açores.net (DGAEP, CFP e SREA).</p>
</div>
{%- endif %}
</div>

<nav class="indice" aria-label="Nesta página">
  <a href="#peso">Público e privado</a>
  <a href="#comparar">Açores, Madeira e país</a>
  <a href="#carreiras">Que profissões</a>
  <a href="#secretarias">Secretaria a secretaria</a>
  <a href="#evolucao">Desde {{ e.ano_inicio }}</a>
  <a href="#salarios">Salários</a>
  <a href="#fontes">Fontes</a>
</nav>

{% if w %}
<h2 id="peso">Público e privado</h2>

<p>Das {{ w.emprego_mil_t }} mil pessoas empregadas nos Açores no
{{ w.periodo }}, cerca de {{ w.publico_t }} trabalhavam para o setor
público. São {{ w.publico_pct }} em cada 100. As outras trabalham em
empresas privadas, por conta própria ou noutras organizações.</p>

<div class="tabela-scroll">
<table class="sper">
<thead><tr><th>Onde trabalham</th><th class="n">Pessoas</th><th class="n">Em cada 100 empregados</th></tr></thead>
<tbody>
<tr><th scope="row">Administrações públicas nos Açores<br><small>Governo Regional e serviços, hospitais, Estado, autarquias ({{ w.periodo }})</small></th><td class="n">{{ w.ap_t }}</td><td class="n">{{ w.ap_pct_t }}</td></tr>
<tr><th scope="row">Empresas públicas regionais fora das administrações<br><small>SATA, EDA, Portos dos Açores, Lotaçor… ({{ w.mercado_ano }})</small></th><td class="n">{{ w.mercado_t }}</td><td class="n"></td></tr>
<tr class="total"><th scope="row">Setor público</th><td class="n">≈ {{ w.publico_t }}</td><td class="n">≈ {{ w.publico_pct }}</td></tr>
<tr><th scope="row">Setor privado, por conta própria e outros</th><td class="n">≈ {{ w.privado_t }}</td><td class="n">≈ {{ w.privado_pct }}</td></tr>
</tbody>
<tfoot><tr><th scope="row">Pessoas empregadas nos Açores (SREA)</th><td class="n">{{ w.emprego_mil_t }} mil</td><td class="n">100</td></tr></tfoot>
</table>
</div>

<p class="nota"><strong>Como se calcula (açores.net):</strong> somam-se os
postos de trabalho nas administrações públicas localizados nos Açores (DGAEP)
e os trabalhadores das empresas públicas regionais que o INE não conta como
administração pública (CFP). A soma divide-se pelas pessoas empregadas
segundo o <a href="{{ w.url }}">Inquérito ao Emprego</a> do SREA. É uma
ordem de grandeza, não um número exato, porque as fontes contam coisas
diferentes:</p>
<ul class="nota">
  <li>a DGAEP conta postos de trabalho, e quem tem dois empregos públicos conta duas vezes;</li>
  <li>o inquérito conta pessoas pelo emprego principal, com base numa amostra;</li>
  <li>os números das empresas são de {{ w.mercado_ano }}, os outros do {{ w.periodo }};</li>
  <li>as empresas municipais, as empresas do Estado nos Açores (como a RTP Açores) e as participadas a menos de 50 % não entram.</li>
</ul>
<p class="nota">O SREA também conta quem trabalha no setor
"Administração pública e defesa" (CAE P): {{ w.setor_p_mil_t }} mil pessoas.
É um conceito diferente, porque os professores e os profissionais de saúde
ficam nos setores da educação e da saúde, sejam públicos ou privados.</p>
{% endif %}

{%- assign k = e.comparacao %}
{% if k.locais %}
<h2 id="comparar">Açores, Madeira e país</h2>

<p>Postos de trabalho nas administrações públicas por cada 100 pessoas
empregadas, no {{ k.periodo | downcase }}{% if k.provisorio %} (dados provisórios da DGAEP){% endif %}.</p>

<div class="tabela-scroll">
<table class="sper barras">
<thead><tr><th></th><th class="n">Administrações públicas</th><th class="n">Pessoas empregadas (INE)</th><th class="n">Em cada 100</th><th class="barra-col" aria-hidden="true"></th><th class="n">Só a administração regional, em cada 100</th></tr></thead>
<tbody>
{%- for x in k.locais %}
<tr><th scope="row">{{ x.local }}</th><td class="n">{{ x.ap_t }}</td><td class="n">{{ x.empregados_t }}</td><td class="n">{{ x.ap_pct_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra" style="width: {{ x.ap_pct | times: 100.0 | divided_by: k.max_pct }}%"></span></td><td class="n">{{ x.ar_pct_t | default: "" }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<ul class="nota">
  <li>Cálculo do açores.net: postos de trabalho por região da DGAEP
  (<a href="{{ e.pagina }}">SIEP</a>, quadro 1.7) a dividir pela
  <a href="{{ k.url_ine }}">população empregada</a> do Inquérito ao Emprego
  do INE no mesmo trimestre. Para as três regiões usa-se o INE, e não o SREA,
  para que a fonte seja a mesma.</li>
  <li>A DGAEP conta cada posto de trabalho onde fica o serviço. A PSP e a GNR,
  por exemplo, contam na sede, em Lisboa. Por isso os Açores e a Madeira têm
  menos postos do que pessoas a trabalhar lá para o Estado, e a comparação entre
  as duas regiões é mais justa do que com o país.</li>
  <li>As empresas públicas de mercado (SATA, EDA…) não entram, para comparar o
  mesmo em todo o lado. Os salários das três regiões estão em
  <a href="#salarios">Salários</a>.</li>
</ul>
{% endif %}

<h2 id="carreiras">Que profissões</h2>

<p>As {{ e.ap_t }} pessoas que trabalham para as administrações públicas nos
Açores ({{ e.periodo }}), por carreira. Os maiores grupos são os assistentes
operacionais, os professores e os administrativos.</p>

<div class="tabela-scroll">
<table class="sper barras">
<thead><tr><th>Carreira</th><th class="n">Postos de trabalho</th><th class="n">%</th><th class="barra-col" aria-hidden="true"></th><th class="n">Num ano</th></tr></thead>
<tbody>
{%- for c in e.carreiras %}
<tr><th scope="row">{{ c.nome }}</th><td class="n">{{ c.valor_t }}</td><td class="n">{{ c.pct_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra" style="width: {{ c.pct | times: 2.5 }}%"></span></td><td class="n">{% if c.var > 0 %}+{{ c.var_t }}{% elsif c.var < 0 %}−{{ c.var_t | remove: "-" }}{% else %}0{% endif %}</td></tr>
{%- endfor %}
<tr><th scope="row">Outras carreiras</th><td class="n">{{ e.carreiras_resto_t }}</td><td class="n">{{ e.carreiras_resto_pct_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra" style="width: {{ e.carreiras_resto_pct | times: 2.5 }}%"></span></td><td class="n"></td></tr>
</tbody>
<tfoot><tr><th scope="row">Total</th><td class="n">{{ e.ap_t }}</td><td class="n">100</td><td></td><td class="n">{% if e.ap_var > 0 %}+{{ e.ap_var_t }}{% elsif e.ap_var < 0 %}−{{ e.ap_var_t | remove: "-" }}{% endif %}</td></tr></tfoot>
</table>
</div>
<p class="nota">"Num ano": diferença face ao mesmo trimestre do ano anterior.
A DGAEP avisa que a divisão por região é aproximada, porque algumas
entidades declaram todos os trabalhadores na sede. Por isso a PSP, a GNR e
outros serviços do Estado com sede em Lisboa não aparecem aqui, apesar de
terem pessoal nos Açores.</p>

<h2 id="secretarias">Administração Regional, secretaria a secretaria</h2>

<p>A Administração Regional tem {{ e.ar_t }} postos de trabalho. Há ainda
{{ e.fss_t }} na segurança social regional, que a DGAEP conta à parte
(fundos de segurança social da Região). Os restantes {{ e.outros_t }} dos
{{ e.ap_t }} trabalham para o Estado (tribunais, Universidade dos Açores,
Forças Armadas…) e para as câmaras municipais e juntas de
freguesia (diferença calculada pelo açores.net).</p>

<div class="tabela-scroll">
<table class="sper barras">
<thead><tr><th>Departamento do Governo Regional</th><th class="n">Postos de trabalho</th><th class="n">%</th><th class="barra-col" aria-hidden="true"></th><th class="n">Num ano</th></tr></thead>
<tbody>
{%- for c in e.secretarias %}
<tr{% if c.ser %} class="sep"{% endif %}><th scope="row">{{ c.nome }}</th><td class="n">{{ c.valor_t }}</td><td class="n">{{ c.pct_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra" style="width: {{ c.pct | times: 2 }}%"></span></td><td class="n">{% if c.var > 0 %}+{{ c.var_t }}{% elsif c.var < 0 %}−{{ c.var_t | remove: "-" }}{% else %}0{% endif %}</td></tr>
{%- endfor %}
</tbody>
<tfoot><tr><th scope="row">Administração Regional dos Açores</th><td class="n">{{ e.ar_t }}</td><td class="n">100</td><td></td><td class="n">{% if e.ar_var > 0 %}+{{ e.ar_var_t }}{% elsif e.ar_var < 0 %}−{{ e.ar_var_t | remove: "-" }}{% endif %}</td></tr></tfoot>
</table>
</div>
<p class="nota">A DGAEP arruma os números pela orgânica do Governo Regional
atual (<a href="https://www.dgaep.gov.pt/index.cfm?OBJID=120BF3B2-FB82-4662-B232-A9D8E055B030">notas da DGAEP</a>).
A Educação inclui os professores e o pessoal das escolas. A última linha são
as empresas públicas que o INE conta como administração pública (sobretudo
os três hospitais, E.P.E.R.), que a DGAEP põe à parte das secretarias.</p>

<h2 id="evolucao">Desde {{ e.ano_inicio }}</h2>

<p>Postos de trabalho no fim de cada ano: na Administração Regional e em
todas as administrações públicas nos Açores.</p>

<div class="tabela-scroll">
<table class="sper barras">
<thead><tr><th>Ano</th><th class="n">Administração Regional</th><th class="n">Todas as administrações nos Açores</th><th class="barra-col" aria-hidden="true"></th></tr></thead>
<tbody>
{%- for a in e.evolucao reversed %}
<tr><th scope="row">{{ a.ano }}{% if a.quando != "31 dez" %} <small>({{ a.quando }})</small>{% endif %}</th><td class="n">{{ a.ar_t }}</td><td class="n">{{ a.ap_t }}</td><td class="barra-col" aria-hidden="true">{% if a.ap %}<span class="barra" style="width: {{ a.ap | times: 100.0 | divided_by: e.evolucao_max }}%"></span>{% endif %}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h2 id="salarios">Salários</h2>

{%- assign sal = e.salarios %}
<p>Quanto se ganha por mês, em média, nas administrações públicas
(trabalhadores a tempo completo, {{ sal.mes }}).</p>

<div class="tabela-scroll">
<table class="sper">
<thead><tr><th></th><th class="n">Remuneração base média</th><th class="n">Ganho médio</th></tr></thead>
<tbody>
{%- if sal.acores %}<tr><th scope="row">Todas as administrações públicas nos Açores</th><td class="n">{{ sal.acores.base_t }} €</td><td class="n">{{ sal.acores.ganho_t }} €</td></tr>{% endif %}
{%- if sal.ar %}<tr><th scope="row">Administração Regional dos Açores</th><td class="n">{{ sal.ar.base_t }} €</td><td class="n">{{ sal.ar.ganho_t }} €</td></tr>{% endif %}
{%- if sal.madeira %}<tr><th scope="row">Administração Regional da Madeira</th><td class="n">{{ sal.madeira.base_t }} €</td><td class="n">{{ sal.madeira.ganho_t }} €</td></tr>{% endif %}
{%- if sal.pais %}<tr><th scope="row">Todas as administrações públicas do país</th><td class="n">{{ sal.pais.base_t }} €</td><td class="n">{{ sal.pais.ganho_t }} €</td></tr>{% endif %}
</tbody>
</table>
</div>
<p class="nota">Resumo do açores.net das definições da DGAEP
(<a href="https://www.dgaep.gov.pt/index.cfm?OBJID=120BF3B2-FB82-4662-B232-A9D8E055B030">metodologia</a>):
a <strong>remuneração base</strong> é o salário da tabela, antes de
impostos. O <strong>ganho</strong> junta-lhe os subsídios e suplementos
regulares, os prémios e as horas extraordinárias. São médias de todas as
carreiras, por isso dependem de quantos médicos, professores ou assistentes
operacionais há em cada administração.</p>

<h2 id="mais">Empresas públicas e contas da Região</h2>

<div class="portas">
<section class="porta">
<h3><a href="/dados/sper/">Empresas públicas regionais</a></h3>
<p>SATA, EDA, Portos dos Açores, os hospitais e as outras empresas da Região:
trabalhadores, contas e quanto a Região gasta com elas.</p>
</section>
<section class="porta">
<h3><a href="/financas/">Finanças da Região</a></h3>
<p>Quanto a Região cobra, gasta e deve, mês a mês, e o que o Tribunal de
Contas diz das contas de cada ano.</p>
</section>
</div>

<p class="aviso">A DGAEP avisa que as empresas não financeiras da Região
<strong>não reportam os seus dados</strong> ao registo do emprego público
(SIOE) ("estão em incumprimento no reporte de dados no
SIOE", <a href="{{ e.ficheiro }}">SIEP, quadros 2.1 a 2.4</a>). Por isso os
trabalhadores da SATA, da EDA e das outras empresas vêm aqui dos relatórios
do <a href="/dados/sper/">Conselho das Finanças Públicas</a>.</p>

<h2 id="fontes">Fontes</h2>

<ul class="fonte">
  <li>Direção-Geral da Administração e do Emprego Público (DGAEP),
  <a href="{{ e.pagina }}">Síntese Estatística do Emprego Público</a>, com
  dados do SIOE: <a href="{{ e.ficheiro }}">ficheiro Excel</a>, quadros 1.1
  (por subsetor e área governativa), 1.7 (por carreira e NUTS I), 1.9 e 1.13
  (remunerações). Os dados do último trimestre são provisórios e a DGAEP
  revê os anteriores em cada edição.</li>
  <li>SREA, <a href="{{ w.url | default: 'https://srea.azores.gov.pt/area/mercado-de-trabalho/' }}">Inquérito ao Emprego</a> (pessoas empregadas).</li>
  <li>Conselho das Finanças Públicas, relatório sobre o setor empresarial
  regional (<a href="/dados/sper/">empresas públicas</a>).</li>
  <li>Dados: <a href="/dados/emprego_publico.csv">emprego_publico.csv</a>
  (todas as séries trimestrais desde {{ e.ano_inicio }}, com a ligação ao
  ficheiro de origem) e a tabela <code>emprego_publico</code> da
  <a href="/dados/">base de dados</a>. Atualizado todas as semanas.</li>
</ul>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(9.5em, 100%), 1fr)); gap: .9em; margin: 1.2em 0 1.5em; }
.numero { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .8em 1em .3em; background: rgba(147,161,161,.08); }
.numero p { margin-bottom: .4em; font-size: .95em; }
.numero .rotulo { font-weight: bold; margin-bottom: .2em; }
.numero .grande { font-size: 1.8em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.numero .grande small { font-size: .5em; font-weight: normal; }
.indice { display: flex; flex-wrap: wrap; gap: .3em 1em; margin: 0 0 1em; font-size: .95em; }
.tabela-scroll { overflow-x: auto; margin-bottom: 1em; }
table.sper { border-collapse: collapse; font-size: .9em; min-width: 100%; }
table.sper th, table.sper td { padding: .3em .5em; border-bottom: 1px solid rgba(147,161,161,.35); text-align: left; vertical-align: top; }
table.sper th[scope="row"] { font-weight: normal; }
table.sper th[scope="row"] small { color: #839496; }
table.sper .n { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
table.sper thead th, table.sper thead th.n { white-space: normal; }
table.sper tfoot th, table.sper tfoot td, table.sper tr.total th, table.sper tr.total td { font-weight: bold; }
table.sper tr.sep th, table.sper tr.sep td { border-top: 2px solid rgba(147,161,161,.6); }
table.barras .barra-col { width: 28%; min-width: 4em; vertical-align: middle; }
table.barras .barra { display: block; height: .7em; max-width: 100%; background: #268bd2; border-radius: 0 4px 4px 0; }
.portas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(18em, 100%), 1fr)); gap: 1em; margin-bottom: 1.5em; }
.porta { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .9em 1em .4em; background: rgba(147,161,161,.08); }
.porta h3 { font-size: 1.1em; margin: 0 0 .4em; }
.porta p { font-size: .95em; }
.nota, .fonte { font-size: .85em; color: #586e75; }
ul.nota { margin-top: -.6em; }
.aviso { border-left: 4px solid #b58900; padding: .4em .8em; background: rgba(181,137,0,.08); }
@media (prefers-color-scheme: dark) { .nota, .fonte { color: #93a1a1; } table.barras .barra { background: #4aa3df; } }
</style>
