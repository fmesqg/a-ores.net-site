---
title: Açores
layout: default
permalink: /
---
{%- assign alra = site.alra_updates | sort: "date" | last -%}
{%- assign joraa = site.joraa_updates | sort: "date" | last -%}
{%- assign base = site.base_updates | sort: "date" | last -%}
<p class="lead">Dados públicos sobre os Açores, num só sítio:</p>
<ul class="lead-lista">
  <li>estatísticas por concelho e freguesia (INE) e por ilha (SREA)</li>
  <li>contas da Região e das câmaras municipais</li>
  <li>contratos públicos, Jornal Oficial e Assembleia Legislativa, todos os dias</li>
  <li>cada número com ligação à fonte oficial, e tudo em CSV</li>
</ul>

<div class="comecar">
<section class="via">
  <h2><a href="/introducao/">Introdução aos dados dos Açores</a></h2>
  <p>Para quem chega agora. Dez minutos, sem jargão:</p>
  <ul>
    <li><a href="/introducao/#ilhas">quantas pessoas vivem em cada ilha</a></li>
    <li><a href="/introducao/#quem-decide">quem decide o quê: Assembleia, Governo, câmaras</a></li>
    <li><a href="/introducao/#dinheiro">de onde vem e para onde vai o dinheiro da Região</a></li>
    <li><a href="/introducao/#palavras">seis palavras para ler os números</a></li>
  </ul>
</section>
<section class="via">
  <h2><a href="/tutorial/">Guia para quem trabalha com dados</a></h2>
  <p>Jornalistas, decisores políticos, investigadores:</p>
  <ul>
    <li><a href="/tutorial/#fontes">cada fonte num quadro: nível, período, atualização, cuidados</a></li>
    <li><a href="/tutorial/#dinheiro">casos reais: seguir um contrato do BASE ao Jornal Oficial</a></li>
    <li><a href="/tutorial/#verificar">CSV e SQL no navegador, sem instalar nada</a></li>
  </ul>
</section>
</div>

<div class="portas">

<section class="porta">
  <h2><a href="/dados/ine/">Estatísticas</a></h2>
  <p>Por concelho e freguesia (INE): rendimentos e IRS, rendas e preço das
  casas, população, turismo, câmaras municipais. Para a Região, mês a mês
  (SREA): preços, emprego, atividade e turismo por ilha. Cada indicador vem
  com a definição oficial.</p>
  <ul>
    <li><a href="/dados/ine/#ind=0012757&nivel=Freguesia">Quanto se ganha em cada freguesia?</a></li>
    <li><a href="/dados/ine/#ind=0012759">Como se distribui o rendimento (quintis)?</a></li>
    <li><a href="/dados/ine/#ind=0014698">Quanto custa arrendar casa?</a></li>
    <li><a href="/dados/ine/#ind=0013210">Onde há mais turistas por habitante?</a></li>
    <li><a href="/dados/srea/">Como estão os preços, o emprego e o turismo agora?</a></li>
  </ul>
</section>

<section class="porta">
  <h2><a href="/financas/">Finanças da Região</a></h2>
  <p>Quanto a Região cobra e quanto gasta, mês a mês, a partir dos boletins
  de execução orçamental, com um glossário dos termos.{% if site.data.beo_ultimo.periodo %}
  Último boletim: <a href="{{ site.data.beo_ultimo.url }}">{{ site.data.beo_ultimo.periodo }}</a>.{% endif %}</p>
  <ul>
    <li><a href="/dados/beo/#quadro=sintese-global&modo=acum">Há défice ou excedente?</a></li>
    <li><a href="/dados/beo/#quadro=receita-fiscal-do-gra&grafico=anos">Quanto rendem o IRS e o IVA, mês a mês?</a></li>
    <li><a href="/dados/beo/#quadro=despesa-do-gra-por-departamento">Quanto gasta cada secretaria?</a></li>
    <li><a href="/financas/camaras/">Quanto gasta cada câmara por habitante?</a></li>
    <li><a href="/dados/tdc/">O que diz o Tribunal de Contas sobre as contas da Região?</a>{% if site.data.tdc_ultimo.conta %} (último parecer: <a href="{{ site.data.tdc_ultimo.url }}">Conta de {{ site.data.tdc_ultimo.conta }}</a>){% endif %}</li>
  </ul>
</section>

<section class="porta">
  <h2><a href="/economia/">Economia</a></h2>
  <p>Setor público e privado: quem trabalha para a Região, o Estado e as
  autarquias, as empresas públicas regionais (SATA, EDA, Portos, hospitais)
  e as 200 maiores empresas com sede nos Açores (revista <cite>100 Maiores
  Empresas dos Açores</cite>).</p>
  <ul>
    <li><a href="/economia/setor-publico/">Quantas pessoas trabalham para o setor público?</a></li>
    <li><a href="/dados/sper/#empresas">Quanto fatura e quanto perde cada empresa pública?</a></li>
    <li><a href="/dados/sper/#esforco">Quanto paga a Região às suas empresas?</a></li>
    <li><a href="/dados/maiores-empresas/">Quais são as maiores empresas dos Açores?</a></li>
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

</div>

## Sobre

O açores.net pretende promover uma cidadania ativa, com informação
acessível e fidedigna. Os dados são recolhidos automaticamente das fontes
oficiais (INE, Governo Regional, Assembleia Legislativa, Jornal Oficial,
portal BASE) e podem ser descarregados e reutilizados. O código está no
[GitHub](https://github.com/fmesqg/a-ores.net-site).

<style>
.lead { font-size: 1.15em; max-width: 40em; margin-bottom: .3em; }
.lead-lista { font-size: 1.05em; margin: 0 0 1.2em 1.2em; max-width: 40em; }
.lead-lista li { margin-bottom: .15em; }
.comecar { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(20em, 100%), 1fr)); gap: 1em; margin-bottom: 1.5em; }
.via { border-left: 4px solid #268bd2; padding: .1em 0 .1em 1em; }
.via h2 { font-size: 1.2em; margin: 0 0 .3em; }
.via p { margin-bottom: .3em; }
.via ul { margin: 0 0 .3em 1.1em; font-size: .95em; }
.portas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(17em, 100%), 1fr)); gap: 1em; margin-bottom: 1.5em; }
.porta { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .9em 1em .4em; background: rgba(147,161,161,.08); }
.porta h2 { font-size: 1.15em; margin: 0 0 .4em; }
.porta p { font-size: .95em; margin-bottom: .5em; }
.porta ul { margin: 0 0 .6em 1.1em; font-size: .95em; }
.colunas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(20em, 100%), 1fr)); gap: 0 2em; }
.colunas h2 { font-size: 1.3em; }
.meta { color: #586e75; font-size: .85em; white-space: nowrap; }
</style>
