---
title: Fontes e métodos
layout: page
permalink: /fontes
---

Material reunido no dossiê do desconto regional no IRS e da derrama regional (ORAA 2027), de novembro de 2026. Só tópicos: falta escrever o texto.

## 1. Fontes, por pergunta

**Quanto rende cada imposto na Região?**
- Proposta de Orçamento (ORAA 2027, PpDLR 44/XIII), quadro 16 do relatório, p. 188 do PDF: http://base.alra.pt:82/iniciativas/iniciativas/XIIIEPpDLR044.pdf#page=188
- Conta da Região (CRAA) e parecer do CESA, para os valores executados (fig. 21).
- Boletim de Execução Orçamental mensal: https://portal.azores.gov.pt/documents/36626/21646330/BEO_2026_09_Setembro
- Eurostat `gov_10a_taxag`, para comparar com o país e a UE.

**Quem paga, por escalão?**
- AT, Dossiers Estatísticos IRS e IRC (xlsx, três anos cada), com mapas por região e escalão: https://info.portaldasfinancas.gov.pt/pt/dgci/divulgacao/estatisticas/estatisticas_ir/Pages/estatisticas_irs.aspx
  - IRS: mapas 30, 32, 34 e 41. IRC: mapas 6, 49, 50, 58, 60 e 61 (derrama).
  - Ler sempre as Notas Prévias. Por exemplo, as empresas contam onde têm a sede e as sucursais do continente contam no continente.
  - Saem no início de abril (31/03 a 11/04 nos últimos anos). A data de publicação está no Last-Modified do servidor e na Wayback Machine.

**Qual é a lei em vigor?**
- CIRS, art. 68.º (taxas do continente) e art. 68.º-A (taxa adicional de solidariedade), no Portal das Finanças.
- Diplomas regionais em PDF no Portal das Finanças (DLR 2/99/A, 15/2015/A, 1/2018/A, 15-A/2021/A). Na Madeira: DLR 17/2026/M.
- LFRA, Lei Orgânica 2/2013, via pgdlisboa.pt (art. 59.º, art. 28.º). CRP, art. 227.º.
- Informações vinculativas da AT (p. ex. PIV 25858), sobre como a AT aplica o desconto.
- Ofícios circulados da AT sobre a derrama municipal por concelho (OC 20293/2026, p. 16).

**Dívida e contas públicas**
- Banco de Portugal, BPstat, série 12561464 (dívida da Região): https://bpstat.bportugal.pt/serie/12561464
- CFP, relatórios anuais sobre as Regiões Autónomas (rel. 01/2026, sobre 2024).

**O que se votou e quem votou**
- base.alra.pt:82: fichas das iniciativas (`/4DACTION/w_pesquisa_registo/3/<n>`), propostas de alteração, grelhas de votação e Diários das Sessões (`/diario/`).
  - Votações por partido nos ORAA anteriores: DS 32 (ORAA 2025) e DS 68 (ORAA 2026).
- Vídeos e áudio de comissões e plenários: video.alra.pt (pesquisa por título e data: `/Search?SrcTitle=…`).
- Composição das comissões: `base.alra.pt:82/4DACTION/w_foto_comissao/1/<código>`.
- Orçamento do Estado: pesquisa de propostas de alteração no parlamento.pt (filtro "Açores - Sim"), com detalhe por BID e votação.

**Contexto e reações**
- Imprensa regional (Açoriano Oriental, RTP Açores, Correio dos Açores, Diário dos Açores).
- Pareceres escritos na ficha da iniciativa (AT, CCIA, sindicatos).
- Órgãos sociais das associações (para ver quem fala em nome de quem).

**Quanto recebe e gasta cada câmara?**
- DGAL, Portal Autárquico: contas de gerência por classificação económica (SNC-AP, desde 2020, xlsx), dívida face ao limite legal (art. 52.º da Lei 73/2013, PDF anual desde 2014) e prazo médio de pagamentos (trimestral): https://portalautarquico.dgal.gov.pt
  - No açores.net: `data/dgal_contas.csv.gz`, `dgal_divida.csv`, `dgal_pmp.csv` e /financas/camaras/.
  - As receitas e despesas das câmaras no INE (0013908 e 0013909) são as mesmas contas: a despesa bate ao euro.
  - Uma câmara marcada `**` não entregou contas validadas nesse ano (Praia da Vitória 2020–21, Angra 2021).
- Anuário Financeiro dos Municípios Portugueses (OCC e IPCA): um PDF por ano, com SMAS e empresas municipais no anexo I. A página do OCC não traz o link do PDF.
- Derrama municipal por concelho (taxa geral, reduzida, isenções): ofício circulado anual da AT (OC 20293/2026, p. 16, para o lucro de 2025). Nove câmaras cobram, dez não; as contas da DGAL de 2025 mostram receita de derrama nas mesmas nove.
- Contratos públicos das câmaras: IMPIC, dados abertos do BASE em dados.gov.pt (todos os contratos desde 2012). No açores.net: `data/base_impic/<ano>.csv.gz`.
- Tribunal de Contas, Secção Regional dos Açores (SRATC): auditorias às câmaras e às empresas municipais. As listas carregam por JavaScript; o número do relatório aparece na imprensa.

**Estatísticas regionais e por concelho**
- INE, API pública (`pindica.jsp`): indicadores por NUTS, concelho e freguesia. No açores.net: `data/ine.csv` e /dados/ine/.
  - O INE suprime células pequenas e algumas séries em euros vêm em milhares (ver `Potencia10` nos metadados).
- SREA (srea.azores.gov.pt): IPC, emprego e desemprego, dormidas, PIB por ilha, em Excel. O nome do ficheiro muda a cada edição.
- DGAEP, Síntese Estatística do Emprego Público (trimestral, xlsx).
- CFP, relatórios sobre o setor empresarial regional (fichas por empresa em xlsx).
- INE 0013860 (IRC por CAE, Açores, 2023–24).

**Contas e execução da Região**
- Boletins de Execução Orçamental (mensais, PDF). No açores.net: /dados/beo/.
- Tribunal de Contas, parecer sobre a Conta da Região (anual). No açores.net: /dados/tdc/.
- Jornal Oficial (JORAA), API pública em jo.azores.gov.pt: atos, apoios, montantes.

**Eleições, partidos e titulares de cargos**
- CNE: mapas oficiais de resultados por círculo e freguesia (cne.pt). Resultados provisórios em eleicoes.mai.gov.pt.
- ECFP (tribunalconstitucional.pt): orçamentos e contas das campanhas regionais (`/tc/contas_eleicoes-raa-<ano>.html`) e contas anuais dos partidos.
- Entidade para a Transparência: declarações de rendimentos e interesses. Aplicação JavaScript, só funciona no browser.
- Tribunal Constitucional, acórdãos: fiscalização de diplomas regionais e limites da autonomia fiscal.

**Empresas**
- Publicações de atos societários (publicacoes.mj.pt): constituição, capital, órgãos sociais. A pesquisa tem reCAPTCHA: fazê-la à mão.
- Relatórios e contas das empresas públicas regionais (SATA, Portos dos Açores, Lotaçor, hospitais, EDA).
- AdC, decisões de concentração (concorrencia.pt): estrutura de mercado e compromissos.
- ERSE: decisões tarifárias e custos de referência.
- TED (concursos UE): lotes, número de propostas e vencedores, pela API oficial.

## 2. Métodos

- **Cruzar duas fontes primárias** antes de publicar um número. Os agregadores dão pistas e não se citam.
- **Fazer a conta com as tabelas legais, não com médias.** O IRS é cobrado por fatias e o desconto é uma percentagem do imposto, por isso o mesmo desconto vale 27 € no 1.º escalão e 20 mil € no 9.º.
  - Simular casos-tipo (50k, 85k, 100k, 150k, 300k) e decompor as diferenças: os 12 413 € face ao continente = 9 357 + 2 881 + 175.
- **Estimar a receita a partir da distribuição da AT**, calibrada pela receita orçamentada. Dar um intervalo (cerca de 3,6 M€ sem crescimento dos rendimentos; 6,1 M€ calibrado).
- **Testar a sensibilidade** quando um número vem de percentagens arredondadas.
- **Separar facto, estimativa e inferência** no texto ("estimo que", "deduzo que") e mostrar a conta numa nota.
- **Folha de cálculo com fórmulas, não com valores**, para qualquer pessoa poder verificar e mudar os pressupostos. Separadores: Leia-me, Simulador, Exemplos, Fontes.
  - Recalcular de forma independente antes de partilhar (p. ex. com o pacote Python `formulas`).
- **Comparações que contam:** com o continente, com a Madeira (mesma lei de finanças) e com o próprio passado (2015–2021: 20% no último escalão).
- **Ler o historial das votações** antes de argumentar: quem votou o quê nos anos anteriores e o que mudou na proposta.
- **Ler para lá da citação** nas transcrições: um "mas" logo a seguir pode mudar o sentido.
- **Verificar datas com mais de uma pista**: a data da sessão na página do vídeo, a data de criação do ficheiro e as referências no próprio discurso.

## 3. Ferramentas

- Arquivo diário do açores.net (BASE, JORAA, ALRA, portal do Governo) com RSS. Serve para contratos por intervalo de datas, porque a pesquisa do base.gov.pt está bloqueada.
- Transcrição local de sessões (Whisper large-v3 no Mac): áudio da ALRA → texto com minutagem e falantes (pyannote).
  - Correções de nomes próprios em ficheiros reutilizáveis (ALRA, energia).
  - Lista de deputados e de membros do Governo, para identificar quem fala.
- Scraper das propostas de alteração ao OE (parlamento.pt, por BID): cerca de 3 000 registos com votação.
- API do TED (concursos UE) para lotes, número de propostas e vencedores.
- PDF para texto com `pypdf`. OCR (tesseract) para PDFs digitalizados, sempre com confirmação no original.
- Base de dados local (sqlite) com as séries da AT, receita fiscal e derrama municipal.

## 4. Bloqueios e alternativas oficiais

- www.alra.pt: a cadeia TLS falhou em vários dias de 2026. Usar base.alra.pt:82 e video.alra.pt, que funcionam.
- video.alra.pt: o filtro de datas de `/Search` devolveu zero resultados a 23/11/2026. Os vídeos novos estão em "Em destaque" na página inicial.
- tcontas.pt (SRATC): SharePoint; o HTML não traz os PDF.
- occ.pt: a página do Anuário não traz o link do PDF.
- Sites de empresas privadas com Cloudflare: usar a imprensa ou o relatório e contas.
- base.gov.pt (pesquisa): usar o arquivo diário do açores.net.
- Diário da República / dre.tretas.org: devolvem páginas vazias ou têm Cloudflare. Tentar o TED, o Portal das Finanças ou o pgdlisboa.pt.
- PDFs do TED: usar a API.
- Regra: não contornar bloqueios. Usar a via oficial ou pedir a página a quem tem acesso.
- Conteúdo pago (imprensa por assinatura, relatórios IES): usar os números com a fonte, mas não publicar o documento.

## 5. Comunicação com os deputados

- Vários níveis no mesmo documento: resumo em três linhas, explicação em três passos, tabelas e perguntas frequentes.
- Um email por deputado, pelo nome, com um parágrafo por partido que fala da história e das posições desse partido (sem mudar os números).
- Anexos verificáveis: PDF curto e a folha de cálculo com fórmulas.
- Declaração de interesses explícita no fim.
- Pedir que apontem erros.

## 6. Ideias para o açores.net

- Página permanente "Fontes" com a tabela fonte / para quê / fiabilidade / como aceder (secções 1 e 4).
- Simulador público do desconto regional no IRS (a folha de cálculo já existe).
- Calendário dos dados: quando saem os dossiers da AT, a conta da Região, os BEO e as votações.
- Página por iniciativa: ficha, pareceres, audições (vídeo e transcrição com minutagem) e votações.
- Lista aberta de deputados e contactos institucionais (os emails @alra.pt são públicos).
