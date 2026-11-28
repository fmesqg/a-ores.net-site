---
title: Câmaras municipais por habitante
nav_title: Câmaras municipais
layout: default
permalink: /financas/camaras/
secao: financas
description: Quanto recebe e gasta cada uma das 19 câmaras municipais dos Açores por habitante, ao lado do rendimento, do turismo, do RSI e dos contratos públicos do mesmo concelho, e quanto das suas compras aparece no BASE.
---
{%- assign c = site.data.camaras -%}
{% include financas-nav.html %}

# Câmaras municipais por habitante

<p class="lead">As receitas e despesas das 19 câmaras, divididas pela
população do concelho, ao lado de outros dados do mesmo concelho: rendimento,
turismo, RSI e contratos públicos.</p>

{% if c.concelhos %}
{%- assign acores = c.refs | where: "nome", "Açores" | first -%}
{%- assign topo = c.concelhos | first -%}
{%- assign fim = c.concelhos | last -%}
<div class="numeros">
<div class="numero">
  <p class="rotulo">Despesa por habitante, {{ c.ano }}</p>
  <p class="grande">{{ acores.despesa_hab_t }} <small>€</small></p>
  <p>Média das câmaras dos Açores: {{ acores.despesa_m_t }} M€ para {{ acores.pop_t }} residentes.
  Em {{ c.inicio }} eram {{ acores.despesa_hab_inicio_t }} €.</p>
</div>
<div class="numero">
  <p class="rotulo">Mais alta</p>
  <p class="grande">{{ topo.despesa_hab_t }} <small>€</small></p>
  <p>{{ topo.nome }}, {{ topo.pop_t }} habitantes.</p>
</div>
<div class="numero">
  <p class="rotulo">Mais baixa</p>
  <p class="grande">{{ fim.despesa_hab_t }} <small>€</small></p>
  <p>{{ fim.nome }}, {{ fim.pop_t }} habitantes.</p>
</div>
</div>
<p class="fonte">Despesa e população do INE; a divisão é do açores.net
(<a href="#metodo">como se calcula</a>).</p>

<h2 id="despesa">Despesa e receita por habitante, {{ c.ano }}</h2>

<p class="nota">Clique num cabeçalho para ordenar. Euros correntes: a
variação desde {{ c.inicio }} não desconta a inflação.</p>
<div class="tabela-scroll">
<table class="sper ordenavel barras">
<thead><tr>
  <th scope="col">Concelho</th>
  <th scope="col" class="n" data-tipo="n">População</th>
  <th scope="col" class="n" data-tipo="n">Despesa (M€)</th>
  <th scope="col" class="n" data-tipo="n">Despesa por habitante (€)</th>
  <th class="barra-col" aria-hidden="true"></th>
  <th scope="col" class="n" data-tipo="n" title="Receitas das operações não financeiras por habitante, publicado pelo INE">Receita por hab. (INE, sem operações financeiras)</th>
  <th scope="col" class="n" data-tipo="n">Despesa por hab. desde {{ c.inicio }}</th>
</tr></thead>
<tbody class="refs">
{%- for d in c.refs %}
<tr><th scope="row">{{ d.nome }}</th><td class="n">{{ d.pop_t }}</td><td class="n">{{ d.despesa_m_t }}</td><td class="n">{{ d.despesa_hab_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra ref" style="width: {{ d.despesa_hab | times: 100.0 | divided_by: c.max_hab }}%"></span></td><td class="n">{{ d.rnf_hab_t }}</td><td class="n">{% if d.var_pct > 0 %}+{% endif %}{{ d.var_pct_t | replace: "-", "−" }} %</td></tr>
{%- endfor %}
</tbody>
<tbody>
{%- for d in c.concelhos %}
<tr><th scope="row">{{ d.nome }}{% if d.ilha != d.nome %} <small>{{ d.ilha }}</small>{% endif %}</th><td class="n" data-v="{{ d.pop }}">{{ d.pop_t }}</td><td class="n" data-v="{{ d.despesa_m }}">{{ d.despesa_m_t }}</td><td class="n" data-v="{{ d.despesa_hab }}">{{ d.despesa_hab_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra" style="width: {{ d.despesa_hab | times: 100.0 | divided_by: c.max_hab }}%"></span></td><td class="n" data-v="{{ d.rnf_hab }}">{{ d.rnf_hab_t }}</td><td class="n" data-v="{{ d.var_pct }}">{% if d.var_pct > 0 %}+{% endif %}{{ d.var_pct_t | replace: "-", "−" }} %</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h2 id="tamanho">Tamanho do concelho e despesa por habitante</h2>

{%- assign g = c.grafico %}
<figure class="dispersao">
<svg viewBox="0 0 {{ g.w }} {{ g.h }}" role="img" aria-labelledby="disp-t" aria-describedby="disp-d">
  <title id="disp-t">Despesa da câmara por habitante e população do concelho, {{ c.ano }}</title>
  <desc id="disp-d">Um ponto por concelho. Os concelhos com menos habitantes gastam mais por habitante. Os valores estão na tabela acima.</desc>
  {%- for t in g.yt %}
  <line class="grelha" x1="{{ g.esq }}" x2="{{ g.dir }}" y1="{{ t.y }}" y2="{{ t.y }}"/>
  <text class="eixo" x="{{ g.esq | minus: 6 }}" y="{{ t.y | plus: 4 }}" text-anchor="end">{{ t.v | divided_by: 1000 }} mil €</text>
  {%- endfor %}
  {%- for t in g.xt %}
  <text class="eixo" x="{{ t.x }}" y="{{ g.base | plus: 18 }}" text-anchor="middle">{% if t.v >= 1000 %}{{ t.v | divided_by: 1000 }} mil{% else %}{{ t.v }}{% endif %}</text>
  {%- endfor %}
  <text class="eixo" x="{{ g.dir }}" y="{{ g.h | minus: 2 }}" text-anchor="end">habitantes (escala logarítmica)</text>
  {%- for p in g.pontos %}
  <g class="ponto" tabindex="0"><circle cx="{{ p.x }}" cy="{{ p.y }}" r="5"><title>{{ p.nome }}</title></circle>
  {%- if p.rotulo %}<text x="{{ p.lx }}" y="{{ p.ly }}" text-anchor="{{ p.ancora }}">{{ p.nome | remove: " (R.A.A.)" }}</text>{% endif %}</g>
  {%- endfor %}
</svg>
</figure>

<p>Os concelhos mais pequenos gastam mais por habitante. {{ topo.nome }}, com
{{ topo.pop_t }} residentes, gasta {{ topo.despesa_hab_t }} € por habitante;
{{ fim.nome }}, com {{ fim.pop_t }}, gasta {{ fim.despesa_hab_t }} €.
<span class="fonte">(Explicação do açores.net: uma parte dos custos de uma
câmara, como os serviços, as estradas ou a recolha do lixo, não diminui na
mesma proporção que a população.)</span></p>

<h2 id="cruzar">O mesmo concelho noutras fontes</h2>

<p class="nota">Clique num cabeçalho para ordenar. Cada coluna é do último
ano publicado; o ano está no cabeçalho.</p>
<div class="tabela-scroll">
<table class="sper ordenavel">
<thead><tr>
  <th scope="col">Concelho</th>
  <th scope="col" class="n" data-tipo="n">Despesa por hab. {{ c.ano }} (€)</th>
  <th scope="col" class="n" data-tipo="n"><a href="/dados/ine/#ind=0012757">Rendimento mediano</a> {{ c.anos_de.rendimento }} (€)</th>
  <th scope="col" class="n" data-tipo="n"><a href="/dados/ine/#ind=0013210">Dormidas por 100 hab.</a> {{ c.anos_de.dormidas }}</th>
  <th scope="col" class="n" data-tipo="n"><a href="/dados/ine/#ind=0013420">RSI por 1000 hab.</a> {{ c.anos_de.rsi }}</th>
  <th scope="col" class="n" data-tipo="n">Contratos da câmara no BASE</th>
  <th scope="col" class="n" data-tipo="n">Valor dos contratos (M€)</th>
  <th scope="col" class="n" data-tipo="n">Valor dos contratos por hab. (€)</th>
</tr></thead>
<tbody class="refs">
{%- for d in c.refs %}
<tr><th scope="row">{{ d.nome }}</th><td class="n">{{ d.despesa_hab_t }}</td><td class="n">{{ d.rendimento_t }}</td><td class="n">{{ d.dormidas_t }}</td><td class="n">{{ d.rsi_t }}</td><td class="n"></td><td class="n"></td><td class="n"></td></tr>
{%- endfor %}
</tbody>
<tbody>
{%- for d in c.concelhos %}
<tr><th scope="row">{{ d.nome }}{% if d.ilha != d.nome %} <small>{{ d.ilha }}</small>{% endif %}</th><td class="n" data-v="{{ d.despesa_hab }}">{{ d.despesa_hab_t }}</td><td class="n" data-v="{{ d.rendimento }}">{{ d.rendimento_t | default: "x" }}</td><td class="n" data-v="{{ d.dormidas }}">{{ d.dormidas_t }}</td><td class="n" data-v="{{ d.rsi }}">{{ d.rsi_t }}</td><td class="n" data-v="{{ d.contratos_n }}">{% if d.contratos_n %}<a href="/dados/#fonte=base&q={{ d.nome | remove: ' (R.A.A.)' | remove: 'Vila da ' | url_encode }}">{{ d.contratos_n_t }}</a>{% else %}—{% endif %}</td><td class="n" data-v="{{ d.contratos_m }}">{{ d.contratos_m_t | default: "—" }}</td><td class="n" data-v="{{ d.contratos_hab }}">{{ d.contratos_hab_t | default: "—" }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<ul class="notas">
  <li><strong>x</strong>: o INE não publica o rendimento destes concelhos
  (segredo estatístico, poucos contribuintes).</li>
  <li><strong>Contratos</strong>: contratos publicados no BASE em que a câmara
  é a entidade adjudicante, publicados entre
  {{ c.base_de | date: "%d/%m/%Y" }} e {{ c.base_ate | date: "%d/%m/%Y" }}
  (o ano da despesa; dados abertos do IMPIC).
  É o preço contratual, não despesa paga, e pode ser pago em vários anos. Não
  inclui serviços municipalizados, empresas municipais nem associações de
  municípios.{% if c.sem_contratos.size > 0 %} Não encontrámos contratos de:
  {{ c.sem_contratos | join: ", " }}; confirme no
  <a href="https://www.base.gov.pt/Base4/pt/pesquisa/?type=contratos">BASE</a>.{% endif %}</li>
  <li>Os nomes das câmaras no BASE variam ("Município de…", "Câmara Municipal
  de…"); o açores.net junta-os pelo nome do concelho. O código está em
  <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/datasets.py">bot/datasets.py</a>
  (<code>municipio</code>).</li>
</ul>

{%- assign k = c.compras -%}
{% if k.concelhos %}
{%- assign k0 = k.anos | first -%}{%- assign k1 = k.anos | last -%}
<h2 id="compras">Quanto das compras aparece no BASE</h2>

<p>De {{ k0 }} a {{ k1 }}, as 19 câmaras gastaram {{ k.total_3a.compras_m_t }} M€ em
bens e serviços e bens de capital e publicaram no BASE contratos de
{{ k.total_3a.contratos_m_t }} M€: <strong>{{ k.total_3a.pct_t }} %</strong>. Uma
percentagem baixa quer dizer compras que não se veem no portal: contratos
que não foram publicados, compras pequenas que a lei não obriga a publicar,
ou contratos sem o município como entidade adjudicante.</p>

<div class="tabela-scroll">
<table class="sper ordenavel">
<thead><tr>
  <th scope="col">Concelho</th>
  <th scope="col" class="n" data-tipo="n">Compras {{ k0 }}-{{ k1 }} (M€)</th>
  <th scope="col" class="n" data-tipo="n">Contratos no BASE {{ k0 }}-{{ k1 }} (M€)</th>
  <th scope="col" class="n" data-tipo="n">No BASE, {{ k0 }}-{{ k1 }}</th>
  <th scope="col" class="n" data-tipo="n">No BASE, {{ k1 }}</th>
</tr></thead>
<tbody>
{%- for d in k.concelhos %}
<tr><th scope="row">{{ d.nome }}{% if d.ilha != d.nome %} <small>{{ d.ilha }}</small>{% endif %}</th><td class="n" data-v="{{ d.compras_3a_m }}">{{ d.compras_3a_m_t }}</td><td class="n" data-v="{{ d.contratos_3a_m }}">{{ d.contratos_3a_m_t }}</td><td class="n" data-v="{{ d.pct_3a }}">{{ d.pct_3a_t }} %</td><td class="n" data-v="{{ d.pct }}">{{ d.pct_t }} %</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<p class="nota">Ano a ano, todas as câmaras:
{% for a in k.serie %}{{ a.ano }}: {{ a.pct_t }} %{% unless forloop.last %} · {% endunless %}{% endfor %}.</p>

<ul class="notas">
  <li><strong>Cálculo do açores.net.</strong> Compras: as rubricas
  "Aquisição de bens e serviços" e "Aquisição de bens de capital" das
  <a href="/dados/ine/#ind=0013909&nivel=Concelho">despesas das câmaras</a>
  (INE, classificador económico). Contratos: o preço contratual dos contratos
  publicados no BASE nesse ano em que a câmara é a adjudicante.</li>
  <li>Um contrato plurianual conta todo no ano em que é publicado, por isso um
  ano isolado pode passar de 100 %; a soma de três anos é mais justa. Não
  inclui serviços municipalizados nem empresas municipais.</li>
</ul>
{% endif %}

<h2 id="metodo">Como se calcula</h2>

<dl class="metodo">
  <dt>Despesa por habitante</dt>
  <dd>Cálculo do açores.net: <a href="{{ c.url.despesa }}">despesas das câmaras
  municipais</a> (INE) a dividir pela <a href="{{ c.url.pop }}">população residente</a> do mesmo ano (INE,
  estimativa a 31 de dezembro). Incluem as operações financeiras, como
  empréstimos e amortizações.</dd>
  <dt>Receita por habitante</dt>
  <dd>Valor publicado pelo INE (<a href="{{ c.url.rnf_hab }}">receitas das
  operações não financeiras por habitante</a>), sem empréstimos nem outras
  operações financeiras. Serve também para conferir o método: a
  <a href="{{ c.url.receita }}">receita total</a> a dividir pela população dá
  o mesmo valor, ou muito perto, quando a câmara tem poucas operações
  financeiras.</dd>
  <dt>Outras colunas</dt>
  <dd>Valores do INE tal como publicados, com a definição de cada um na
  <a href="/dados/ine/">página do INE</a>.</dd>
</dl>

<p class="fonte">Todos os dados por concelho: <a href="/dados/ine/#ind=0013909&nivel=Concelho">despesas</a>,
<a href="/dados/ine/#ind=0013908&nivel=Concelho">receitas</a> e
<a href="/dados/ine/#ind=0012918&nivel=Concelho">população</a> na página do INE;
contratos na <a href="/dados/#fonte=base">pesquisa do BASE</a>.</p>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(12em, 100%), 1fr)); gap: .9em; margin: 1em 0 .4em; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
table.sper th[scope="row"] { font-weight: normal; white-space: nowrap; }
table.sper tbody.refs th, table.sper tbody.refs td { font-weight: bold; background: rgba(147,161,161,.08); }
table.ordenavel thead th[data-tipo] { cursor: pointer; }
table.ordenavel thead th[aria-sort="descending"]::after { content: " ▼"; }
table.ordenavel thead th[aria-sort="ascending"]::after { content: " ▲"; }
.barra-col { width: 12%; min-width: 4em; }
.barra { display: block; height: .8em; margin-top: .25em; background: #268bd2; border-radius: 0 4px 4px 0; }
.barra.ref { background: var(--s1); }
.dispersao { margin: .5em 0 1em; max-width: 44em; }
.dispersao svg { width: 100%; height: auto; overflow: visible; }
.dispersao .grelha { stroke: rgba(147,161,161,.35); stroke-width: 1; }
.dispersao .eixo { font-size: 11px; fill: var(--s00); }
.dispersao circle { fill: #268bd2; stroke: var(--s3); stroke-width: 2; }
.dispersao .ponto text { font-size: 12px; fill: currentColor; }
.dispersao .ponto:hover circle, .dispersao .ponto:focus circle { fill: #cb4b16; }
.dispersao .ponto:focus { outline: none; }
.metodo dt { font-weight: bold; margin-top: .6em; }
.metodo dd { margin-left: 0; max-width: 42em; }
.fonte { font-size: .85em; color: var(--s01); }
@media (prefers-color-scheme: dark) {
  .fonte { color: var(--s01); }
  .dispersao .eixo { fill: var(--s01); }
  .dispersao circle { stroke: var(--s3); }
}
</style>

<script>
(function () {
  document.querySelectorAll("table.ordenavel").forEach(function (tabela) {
    var corpo = tabela.tBodies[tabela.tBodies.length - 1];
    var ths = tabela.tHead.rows[0].cells;
    Array.prototype.forEach.call(ths, function (th, i) {
      if (!th.dataset.tipo) return;
      th.tabIndex = 0;
      function ordenar(e) {
        if (e.target.closest("a")) return;
        var desc = th.getAttribute("aria-sort") !== "descending";
        Array.prototype.forEach.call(ths, function (o) { o.removeAttribute("aria-sort"); });
        th.setAttribute("aria-sort", desc ? "descending" : "ascending");
        var linhas = Array.prototype.slice.call(corpo.rows);
        linhas.sort(function (a, b) {
          var x = parseFloat(a.cells[i].dataset.v), y = parseFloat(b.cells[i].dataset.v);
          if (isNaN(x)) x = -Infinity;
          if (isNaN(y)) y = -Infinity;
          return desc ? y - x : x - y;
        });
        linhas.forEach(function (tr) { corpo.appendChild(tr); });
      }
      th.addEventListener("click", ordenar);
      th.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); ordenar(e); } });
    });
  });
})();
</script>
