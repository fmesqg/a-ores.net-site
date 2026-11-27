---
title: Descarregar os dados
layout: default
permalink: /dados/descarregar/
secao: dados
---
{% include dados-nav.html %}

# Descarregar os dados

| Ficheiro | Conteúdo | Cobertura |
|---|---|---|
| [base.csv](/dados/base.csv) | um contrato por linha: adjudicante, adjudicatário, preço, procedimento, data de assinatura, número de concorrentes e origem da linha (`açores.net` ou `IMPIC`) | <span data-meta="base"></span> |
| [alra.csv](/dados/alra.csv) | requerimentos (com estado e resposta), iniciativas, votos, petições, intervenções, diários, audições, notas de imprensa | <span data-meta="alra"></span> |
| [joraa.csv](/dados/joraa.csv) | atos do Jornal Oficial com montantes (portarias, despachos, resoluções) | <span data-meta="joraa"></span> |
| [ine.csv](/dados/ine.csv) | um valor por linha: indicador, período, local (região, concelho ou freguesia), concelho, ilha, categoria, valor, unidade | <span data-meta="ine"></span> |
| [beo.csv](/dados/beo.csv) | um valor por linha: quadro do boletim de execução orçamental, rubrica, subsetor ou departamento, medida, mês (acumulado desde janeiro), valor, boletim | <span data-meta="beo"></span> |
| [tdc.csv](/dados/tdc.csv) | o texto dos pareceres do Tribunal de Contas sobre a Conta da Região: juízo, reservas, ênfases e recomendações (com o estado que o parecer seguinte lhes deu) | <span data-meta="tdc"></span> |
| [tdc_valores.csv](/dados/tdc_valores.csv) | os números desses pareceres: conta consolidada, dívida total, receita e despesa fora da Conta | <span data-meta="tdc_valores"></span> |
| [at_irs.csv](/dados/at_irs.csv) | um valor por linha: IRS por escalão (agregados, rendimento englobado, IRS liquidado) nos Açores, na Madeira e no continente, a taxa adicional de solidariedade e as taxas gerais | <span data-meta="at_irs"></span> |
| [at_irc.csv](/dados/at_irc.csv) | um valor por linha: IRC à taxa da Região, derrama estadual por escalão e taxas nominais de IRC, nos Açores, na Madeira e no continente | <span data-meta="at_irc"></span> |
| [at_distritos.csv](/dados/at_distritos.csv) | um valor por linha: os mapas «por distrito» da AT, de IRS (agregados, rendimento, imposto, taxa efetiva, desde 2015) e de IRC (declarações, lucro, prejuízo, matéria coletável, imposto, taxa efetiva, desde 2011), com o distrito como a AT o escreve e a região | <span data-meta="at_distritos"></span> |
| [bportugal.csv](/dados/bportugal.csv) | um valor por linha, do Banco de Portugal: empréstimos a particulares (habitação, consumo) e a empresas, crédito vencido e devedores por região (mensal), depósitos por região (mensal, desde 2018), investimento direto do exterior por região (anual) e indicadores das empresas por região e setor (anual, desde 2006), com o número da série no BPstat | <span data-meta="bportugal"></span> |
| [contratos.db](/dados/contratos.db), [parlamento.db](/dados/parlamento.db), [financas.db](/dados/financas.db), [estatisticas.db](/dados/estatisticas.db), [empresas.db](/dados/empresas.db) | as tabelas acima em SQLite, uma base por tema, com pesquisa de texto; a tabela `base` tem mais colunas (NIF, CPV, preço base e preço efetivo, propostas, local de execução, fundamentação) | ver abaixo |

Os CSV estão em UTF-8 e abrem diretamente no Excel, no LibreOffice ou no
Google Sheets. Todos os ficheiros são refeitos todos os dias a partir das
[páginas diárias](/rsss) e do código em
[`bot/datasets.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/datasets.py).
O `ine.csv` é atualizado uma vez por semana a partir da
[API do INE](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api), pelo
código em [`bot/ine.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/ine.py),
que tem a lista de indicadores. O `beo.csv` é atualizado uma vez por semana a
partir dos PDF dos boletins, por
[`bot/beo.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/beo.py).
Os `tdc*.csv` mudam uma vez por ano, quando sai um parecer novo, por
[`bot/tdc.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/tdc.py).
Os contratos anteriores a agosto de 2024 vêm dos ficheiros anuais do IMPIC,
relidos uma vez por mês por
[`bot/base_impic.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/base_impic.py).
Os `at_*.csv` mudam uma vez por ano, quando a AT publica os dossiês
estatísticos de IRS e de IRC, por
[`bot/at_ir.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/at_ir.py).
O `bportugal.csv` é relido uma vez por semana da API do BPstat por
[`bot/bportugal.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/bportugal.py).
Última geração: <span data-meta="gerado"></span>.
<script>
fetch("/dados/meta.json?v={{ site.time | date: '%s' }}").then(function (r) { return r.json(); }).then(function (m) {
  document.querySelectorAll("[data-meta]").forEach(function (el) {
    var k = el.getAttribute("data-meta"), x = m[k];
    if (!x) return;
    el.textContent = k === "gerado" ? x.replace("T", " ") : x.linhas.toLocaleString("pt-PT") + " linhas, " + x.de + " a " + x.ate;
  });
}).catch(function () {});
</script>
