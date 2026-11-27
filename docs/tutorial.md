---
title: "Guia: trabalhar com os dados dos Açores"
layout: default
permalink: /tutorial/
description: Para jornalistas, decisores políticos e investigadores. Cada fonte num quadro e, com casos reais, onde está cada número no açores.net, de onde vem e o que tem de particular cada fonte - INE, contratos públicos, Jornal Oficial, contas da Região, câmaras municipais e Assembleia - com casos reais.
---

# Guia: trabalhar com os dados dos Açores

<p class="lead">Para jornalistas, decisores políticos e investigadores:</p>

<ul class="lead-lista">
  <li><a href="#fontes">cada fonte num quadro</a>: nível geográfico, período, atualização e o que convém saber</li>
  <li>seis casos reais, com o caminho para cada número</li>
  <li>um caso seguido de ponta a ponta, por todas as fontes:
  <a href="/casos/eda-bencom/">o fuelóleo da EDA e a BENCOM</a></li>
  <li>todos os números com ligação ao documento oficial</li>
</ul>

<nav class="indice" aria-label="Nesta página">
  <a href="#fontes"><span>•</span> As fontes num quadro</a>
  <a href="#citar"><span>1</span> Rendimento por freguesia</a>
  <a href="#comparar"><span>2</span> Câmaras e concelhos por habitante</a>
  <a href="#dinheiro"><span>3</span> Seguir o dinheiro</a>
  <a href="#contas"><span>4</span> Ler as contas da Região</a>
  <a href="#assembleia"><span>5</span> Acompanhar a Assembleia</a>
  <a href="#verificar"><span>6</span> Descarregar e fazer as próprias contas</a>
</nav>

<p class="fonte">Os números dos exemplos são os que estavam no site em
novembro de 2026. Se abrir as ligações mais tarde, podem ter mudado.</p>

<h2 id="fontes">As fontes num quadro</h2>

<div class="tabela">
<table class="fontes">
<thead><tr><th scope="col">Fonte</th><th scope="col">Nível</th><th scope="col">Período e atualização</th><th scope="col">Convém saber</th></tr></thead>
<tbody>
<tr><th scope="row"><a href="/dados/ine/">INE</a></th><td>concelho, freguesia; Açores, Madeira e país</td><td>varia por indicador; o site verifica uma vez por semana</td><td>segredo estatístico em concelhos e freguesias pequenos; definição oficial junto de cada indicador</td></tr>
<tr><th scope="row"><a href="/dados/srea/">SREA</a></th><td>Região, algumas séries por ilha</td><td>mensal ou trimestral; verificado uma vez por semana</td><td>o emprego e o desemprego vêm de um inquérito por amostragem</td></tr>
<tr><th scope="row"><a href="/dados/beo/">Execução orçamental</a></th><td>Região (subsetores e secretarias)</td><td>mensal, acumulado desde janeiro</td><td>despesa paga, não orçamentada; provisório até à Conta</td></tr>
<tr><th scope="row"><a href="/dados/tdc/">Tribunal de Contas</a></th><td>Região</td><td>um parecer por ano sobre a Conta</td><td>reservas e recomendações com o estado que lhes dá o parecer seguinte</td></tr>
<tr><th scope="row"><a href="/financas/camaras/">Câmaras</a></th><td>concelho</td><td>anual (INE)</td><td>valores por habitante calculados pelo açores.net; a despesa inclui amortização de empréstimos</td></tr>
<tr><th scope="row"><a href="/economia/setor-publico/">Emprego público</a></th><td>Açores, Madeira, país</td><td>trimestral (DGAEP)</td><td>postos de trabalho, não pessoas; o último trimestre é provisório</td></tr>
<tr><th scope="row"><a href="/dados/sper/">Empresas públicas</a></th><td>empresa</td><td>anual (CFP)</td><td>o site mostra o relatório mais recente</td></tr>
<tr><th scope="row"><a href="/dados/maiores-empresas/">Maiores empresas</a></th><td>empresa com sede nos Açores</td><td>anual, publicado com um ano de atraso</td><td>ranking de uma revista, não estatística oficial</td></tr>
<tr><th scope="row"><a href="/dados/#fonte=base">Contratos (BASE)</a></th><td>contrato</td><td>diário desde agosto de 2024; antes, desde 2012, dados abertos do IMPIC (mensal)</td><td>preço contratual, em regra sem IVA; não é despesa paga</td></tr>
<tr><th scope="row"><a href="/dados/#fonte=joraa">Jornal Oficial</a></th><td>ato</td><td>diário, desde agosto de 2024</td><td>o montante é uma soma automática dos valores no texto{% if site.data.joraa_estado.atraso_de %}; faltam os atos de {{ site.data.joraa_estado.atraso_de }} a {{ site.data.joraa_estado.atraso_ate }}{% endif %}</td></tr>
<tr><th scope="row"><a href="/dados/#fonte=alra">Assembleia</a></th><td>iniciativa, requerimento</td><td>diário, desde agosto de 2024</td><td>estado do requerimento é o último visto pelo robô</td></tr>
</tbody>
</table>
</div>

<p class="fonte">Descrição dos ficheiros e código de recolha de cada fonte na
<a href="/dados/#descarregar">página de dados</a>.</p>

<h2 id="citar">1. Rendimento por freguesia</h2>

**A pergunta:** quanto se ganha nos Açores, e onde se ganha menos?

<ol class="passos">
  <li>Abra o indicador
  <a href="/dados/ine/#ind=0012757&nivel=Freguesia">rendimento bruto declarado,
  deduzido do IRS, por sujeito passivo (mediana)</a> na página do INE.</li>
  <li>No topo da tabela estão as referências. Em 2024: Açores
  <strong>12 565 €</strong>, Madeira 12 626 €, país 12 316 €.</li>
  <li>Ordene a coluna de 2024. A freguesia com o valor mais baixo é Ponta
  Garça (Vila Franca do Campo), com <strong>9 305 €</strong>. A mais alta é
  Ponta Delgada (São Pedro), com 17 585 €.</li>
  <li>A definição oficial e a ligação ao indicador no INE estão junto ao
  nome do indicador.</li>
</ol>

<div class="cuidado">
<p><strong>Desta fonte</strong></p>
<ul>
  <li><strong>Só 25 freguesias e 16 dos 19 concelhos têm valor.</strong> Nas
  outras há poucos contribuintes e o INE mantém o valor em segredo
  estatístico. Ponta Garça é a mais baixa entre as que têm dados.</li>
  <li><strong>É rendimento declarado no IRS</strong>: fica de fora quem não
  entrega declaração e o que não é declarado.</li>
</ul>
</div>

<h2 id="comparar">2. Câmaras e concelhos por habitante</h2>

**A pergunta:** que câmara gasta mais?

<ol class="passos">
  <li>Abra <a href="/financas/camaras/">Câmaras municipais por habitante</a>.
  Em total, Ponta Delgada é a que mais gasta (67,5 M€ em 2025). Por habitante
  é das que menos gasta: <strong>942 €</strong>, contra 1 259 € na média dos
  Açores e <strong>7 194 €</strong> no Corvo.</li>
  <li>O gráfico por baixo da tabela mostra que a despesa por habitante desce com o tamanho
  do concelho.</li>
  <li>A segunda tabela junta, para cada concelho, o rendimento mediano, as
  dormidas por 100 habitantes, o RSI por 1000 habitantes e os contratos que a
  câmara assinou no BASE. Ordene por qualquer coluna.</li>
</ol>

<div class="cuidado">
<p><strong>Desta fonte</strong></p>
<ul>
  <li><strong>A divisão é do açores.net</strong>: despesa do INE a dividir
  pela população residente do INE no mesmo ano. A receita por habitante é o
  valor que o INE publica, sem operações financeiras.</li>
  <li><strong>A despesa inclui operações financeiras</strong> (amortização
  de empréstimos), o que pesa num ano de reembolso grande.</li>
  <li><strong>Os contratos são os que o açores.net recolheu do BASE</strong>
  desde agosto de 2024. Os nomes das câmaras no BASE variam e são juntados
  pelo nome do concelho. Da Câmara de Vila do Porto não aparece nenhum.</li>
  <li>Noutros indicadores do INE, a página do INE tem versões "por
  habitante" ou "por 1000 habitantes" (por exemplo,
  <a href="/dados/ine/#ind=0013210">dormidas por 100 habitantes</a>) e a
  escala "Índice" no gráfico, em que cada local começa em 100. O
  <a href="/dados/srea/#precos">IPC dos Açores</a> está no SREA.</li>
</ul>
</div>

<h2 id="dinheiro">3. Seguir o dinheiro</h2>

**O caso:** a obra do novo porto das Lajes das Flores. As três fontes que o
site junta contam partes diferentes da história.

<div class="cartoes">
<div class="cartao">
<h3>O contrato (BASE)</h3>
<p>Portos dos Açores, S.A. adjudicou a empreitada a um consórcio de quatro
construtoras, por <strong>194 830 000 €</strong>, num concurso limitado por
prévia qualificação. Publicado a 28/03/2025.</p>
<p class="ir"><a href="/dados/#fonte=base&q=lajes%20das%20flores">Pesquisar
no açores.net</a> · <a href="https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id=11314392">contrato
no BASE</a></p>
</div>
<div class="cartao">
<h3>A decisão (Jornal Oficial)</h3>
<p>O Despacho n.º 694/2025 autoriza a transferência de
<strong>3 175 000 €</strong> para a Portos dos Açores, para esta obra. O
Anúncio n.º 370/2025 abre a contratação da fiscalização.</p>
<p class="ir"><a href="/dados/#fonte=joraa&q=lajes%20das%20flores">Pesquisar
no açores.net</a> · <a href="https://jo.azores.gov.pt/#/ato/829fe0d8-6d31-411b-981b-00089ccecfeb">despacho
no JORAA</a></p>
</div>
<div class="cartao">
<h3>O debate (Assembleia)</h3>
<p>Notas do PS sobre a obra (2024) e um requerimento da IL (abril de
2026) sobre o desembarque de tripulantes no porto, com resposta do
Governo em PDF.</p>
<p class="ir"><a href="/dados/#fonte=alra&q=lajes%20das%20flores">Pesquisar
no açores.net</a> · <a href="http://base.alra.pt:82/4DACTION/w_pesquisa_registo/4/9275">requerimento
na ALRA</a></p>
</div>
</div>

<div class="cuidado">
<p><strong>Desta fonte</strong></p>
<ul>
  <li><strong>Valor do contrato não é despesa paga.</strong> O BASE dá o
  preço contratual, que normalmente não inclui IVA e pode mudar com
  trabalhos a mais. O pagamento faz-se ao longo da obra.</li>
  <li><strong>A coluna "Montante" do Jornal Oficial é uma soma
  automática.</strong> O açores.net soma todos os valores em euros
  que aparecem no texto do ato. Se o mesmo valor aparece duas vezes, conta
  duas vezes: o Despacho n.º 694/2025 aparece com 6 350 000 €, o dobro do
  que autoriza.</li>
  <li><strong>Em número e em valor, o peso é diferente.</strong> Desde agosto
  de 2024, os ajustes diretos são 64 % dos contratos para os Açores
  publicados no BASE, mas só 26 % do valor.</li>
  <li>O fundamento de cada ajuste direto (limite de valor ou artigo do
  Código dos Contratos Públicos) está na ficha do contrato no BASE.</li>
</ul>
</div>

<p>O mesmo método, aplicado a um caso com mais fontes (contratos, Jornal
Oficial, Assembleia, imprensa, contas das empresas e o regulador):
<a href="/casos/eda-bencom/">o fuelóleo da EDA e a BENCOM</a>.</p>

<h2 id="contas">4. Ler as contas da Região</h2>

**A pergunta:** a Região está a gastar menos em saúde?

<ol class="passos">
  <li>Abra a <a href="/dados/beo/#quadro=despesa-do-gra-por-funcao&modo=acum&grafico=anos">despesa
  por função</a> nos boletins de execução orçamental, em valores
  acumulados e com o gráfico "ano a ano".</li>
  <li>Na linha "Saúde", de janeiro a setembro: <strong>411,6 M€</strong> em
  2024, <strong>476,6 M€</strong> em 2025 e <strong>431,2 M€</strong> em
  2026, menos 9,5 % do que no ano anterior.</li>
  <li>O boletim em PDF de cada mês está ligado na página.</li>
</ol>

<div class="cuidado">
<p><strong>Desta fonte</strong></p>
<ul>
  <li><strong>É despesa paga até ao fim do mês</strong>, não orçamento nem
  despesa comprometida. Uma transferência para os hospitais paga em outubro,
  e não em setembro, muda a comparação até setembro. O ano completo está no
  boletim de dezembro.</li>
  <li>Os boletins são provisórios. Os valores finais estão na Conta da
  Região, e o <a href="/dados/tdc/">Tribunal de Contas</a> diz se os pode
  confirmar e com que reservas.</li>
  <li>Os termos (despesa efetiva, saldo primário, passivos financeiros)
  estão no <a href="/dados/beo/#glossario">glossário</a>, com ligação aos
  textos legais.</li>
</ul>
</div>

<h2 id="assembleia">5. Acompanhar a Assembleia</h2>

Os deputados fazem perguntas por escrito ao Governo: os
<a href="/dados/#fonte=alra&tipo=Requerimentos">requerimentos</a>. Cada
um tem o PDF da pergunta e, quando existe, o da resposta. A Assembleia
regista se a resposta chegou a tempo.

- Desde agosto de 2024, o site registou 825 requerimentos. A Assembleia
  marca 446 com "resposta atempada", 311 com "resposta tardia" e 37 "fora
  de prazo".
- [Requerimentos e respostas por deputado](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/parlamento.db#/parlamento?sql=select%20autores%2C%20count%28%2A%29%20as%20requerimentos%2C%20sum%28estado%20%3D%20%27RESPOSTA%20ATEMPADA%27%29%20as%20atempada%2C%20sum%28estado%20%3D%20%27RESPOSTA%20TADIA%27%29%20as%20tardia%2C%20sum%28estado%20%3D%20%27FORA%20DE%20PRAZO%27%29%20as%20fora_de_prazo%20from%20alra%20where%20tipo%20%3D%20%27Requerimentos%27%20group%20by%20autores%20order%20by%20requerimentos%20desc)
  (consulta SQL já feita, abre no navegador).
- Para saber o que entrou ontem, veja as [atualizações diárias](/atualizacoes/)
  ou siga por [RSS](/rsss).

<div class="cuidado">
<p><strong>Desta fonte</strong></p>
<ul>
  <li>O estado é o último que o robô viu no site da Assembleia. A ficha de
  cada requerimento, na ALRA, tem o estado atual.</li>
</ul>
</div>

<h2 id="verificar">6. Descarregar e fazer as próprias contas</h2>

Tudo o que o site mostra pode ser descarregado:

- **Em folha de cálculo.** Cada fonte tem um CSV na
  [página de dados](/dados/#descarregar), que abre no Excel, no LibreOffice ou
  no Google Sheets. Nas páginas de pesquisa, "Descarregar" guarda só as
  linhas filtradas.
- **Em SQL, sem instalar nada.** As bases de dados (uma por tema; a dos
  contratos é [contratos.db](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/contratos.db#/contratos))
  abrem no Datasette Lite, no navegador. Por exemplo, os
  [ajustes diretos por entidade](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/contratos.db#/contratos?sql=select%20adjudicante%2C%20count%28%2A%29%20as%20contratos%2C%20round%28sum%28preco%29%29%20as%20total_eur%20from%20base%20where%20procedimento%20like%20%27Ajuste%20Direto%25%27%20group%20by%20adjudicante%20order%20by%20total_eur%20desc%20limit%20100).
  Pode alterar a consulta e partilhar o endereço do resultado.

<div class="cuidado">
<p><strong>Limites dos dados</strong></p>
<ul>
  <li>Contratos, Assembleia e Jornal Oficial só desde agosto de 2024, e só
  o que o robô viu. Se uma fonte falhou num dia, esse dia pode faltar.</li>
  <li>De 11 de agosto a 27 de novembro de 2026, o site do Jornal Oficial
  bloqueou o robô. Os dias em falta estão a ser recolhidos, dos mais
  recentes para os mais antigos{% if site.data.joraa_estado.atraso_de %}:
  ainda faltam os atos publicados entre {{ site.data.joraa_estado.atraso_de }}
  e {{ site.data.joraa_estado.atraso_ate }}{% endif %}.</li>
  <li>Mais notas por fonte na <a href="/dados/#limitacoes">página de
  dados</a>.</li>
</ul>
</div>

Encontrou um erro no site ou quer um dado que ainda não está cá? Abra um
pedido no [GitHub](https://github.com/fmesqg/a-ores.net-site/issues).

<p class="fonte">Explicações do açores.net, não são texto oficial. As
definições oficiais estão junto de cada indicador, com ligação à fonte.</p>

<style>
.lead { font-size: 1.15em; max-width: 40em; margin-bottom: .3em; }
.lead-lista { margin: 0 0 1em 1.2em; max-width: 40em; }
.tabela { overflow-x: auto; margin-bottom: .6em; }
.fontes { font-size: .9em; border-collapse: collapse; }
.fontes th, .fontes td { vertical-align: top; text-align: left; padding: .35em .5em; }
.fontes th[scope=row] { white-space: nowrap; }
.indice { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(15em, 100%), 1fr)); gap: .4em; margin: 1em 0 1em; }
.indice a { display: block; padding: .45em .7em; border: 1px solid rgba(147,161,161,.6); border-radius: 6px; background: rgba(147,161,161,.08); text-decoration: none; }
.indice a:hover { background: rgba(38,139,210,.12); }
.indice span { display: inline-block; min-width: 1.4em; font-weight: bold; color: #268bd2; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
.passos { max-width: 42em; }
.passos li { margin-bottom: .4em; }
.cuidado { border-left: 4px solid #b58900; background: rgba(181,137,0,.08); padding: .6em 1em .1em; margin: 1em 0 1.4em; max-width: 42em; border-radius: 0 6px 6px 0; }
.cuidado p { margin-bottom: .3em; }
.cuidado li { margin-bottom: .35em; }
.cartoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(16em, 100%), 1fr)); gap: .9em; margin: 1em 0 1.2em; }
.cartao { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .8em 1em .3em; background: rgba(147,161,161,.08); }
.cartao h3 { font-size: 1.05em; margin: 0 0 .4em; }
.cartao p { font-size: .95em; margin-bottom: .5em; }
.cartao .ir { font-size: .9em; }
.fonte { font-size: .85em; color: #586e75; }
@media (prefers-color-scheme: dark) { .fonte { color: #93a1a1; } }
</style>
