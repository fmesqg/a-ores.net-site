from bot.record import (
    AudiARep,
    AudiGRep,
    Diario,
    Info,
    Iniciativa,
    Interven,
    Peti,
    Requerimento,
    Voto,
)


# --- Requerimento ---


def test_requerimento_to_markdown_new():
    data = {
        "id": 100,
        "url": "http://example.com/100",
        "Assunto": "Test assunto",
        "Requerente(s)": "João Silva",
        "Data entrada": "01/01/2024",
        "Texto Requerimento": "http://example.com/doc.pdf",
    }
    r = Requerimento(data)
    md = r.to_markdown(prev=None, now="NO PRAZO")
    assert "Novo Requerimento" in md
    assert "[Test assunto]" in md
    assert "Requerente(s): João Silva" in md


def test_requerimento_to_markdown_status_change():
    data = {
        "id": 100,
        "url": "http://example.com/100",
        "Assunto": "Test",
        "Requerente(s)": "Ana",
        "Data entrada": "01/01/2024",
    }
    r = Requerimento(data)
    md = r.to_markdown(prev="NO PRAZO", now="RESPOSTA ATEMPADA")
    assert "NO PRAZO → RESPOSTA ATEMPADA" in md
    assert "Novo Requerimento" not in md


def test_requerimento_to_markdown_multiple_requerentes():
    data = {
        "id": 100,
        "url": "http://example.com/100",
        "Assunto": "Test",
        "Requerente(s)": "João CH; Ana PS; Pedro PSD",
        "Data entrada": "01/01/2024",
    }
    r = Requerimento(data)
    md = r.to_markdown(prev=None, now="NO PRAZO")
    assert "João CH, ..." in md


def test_requerimento_to_markdown_with_resposta():
    data = {
        "id": 100,
        "url": "http://example.com/100",
        "Assunto": "Test",
        "Requerente(s)": "João",
        "Data entrada": "01/01/2024",
        "Texto Requerimento": "http://example.com/req.pdf",
        "Texto Resposta": "http://example.com/resp.pdf",
        "Data da entrada da resposta": "15/01/2024",
    }
    r = Requerimento(data)
    md = r.to_markdown(prev=None, now="RESPOSTA ATEMPADA")
    assert "[resposta]" in md
    assert "15/01/2024" in md


def test_requerimento_export_table_row():
    data = {
        "id": 100,
        "url": "http://example.com/100",
        "Número": "42",
        "Requerente(s)": "João CH; Ana PS",
        "Texto Requerimento": "http://example.com/req.pdf",
    }
    r = Requerimento(data)
    headers = ["Número", "Requerente(s)", "Alteração do Status", "Texto Requerimento", "Texto Resposta"]
    row = r.export_table_row(headers=headers, prev="NO PRAZO", now="RESPOSTA ATEMPADA")
    assert "[42]" in row[0]
    assert "João CH ..." in row[1]
    assert "NO PRAZO → RESPOSTA ATEMPADA" in row[2]
    assert "[Requerimento]" in row[3]
    assert row[4] is None


# --- Diario ---


def test_diario_to_markdown_full():
    data = {
        "url": "http://example.com/d1",
        "Número": "123",
        "Data": "01/01/2024",
        "Texto Separata": "http://example.com/sep.pdf",
        "SSumário": "Resumo do diário",
        "Texto Diário": "http://example.com/diario.pdf",
    }
    d = Diario(data)
    md = d.to_markdown()
    assert "[123]" in md
    assert "Sumário: Resumo do diário" in md
    assert "[Separata (pdf)]" in md
    assert "[Diário (pdf)]" in md


def test_diario_to_markdown_no_numero():
    data = {"url": "http://example.com/d1"}
    d = Diario(data)
    assert d.to_markdown() is None


# --- AudiGRep ---


def test_audigrep_to_markdown_full():
    data = {
        "url": "http://example.com/ag1",
        "Assunto": "Audição governo",
        "Titulo": "Título X",
        "Data entrada": "01/01/2024",
    }
    r = AudiGRep(data)
    md = r.to_markdown()
    assert "[Audição governo]" in md
    assert "Titulo: Título X" in md


def test_audigrep_to_markdown_no_assunto():
    data = {"url": "http://example.com/ag1"}
    assert AudiGRep(data).to_markdown() is None


# --- AudiARep ---


def test_audiarep_to_markdown_full():
    data = {
        "url": "http://example.com/aa1",
        "Assunto": "Audição AR",
        "Titulo": "Título Y",
        "Data entrada": "02/02/2024",
        "Texto Audição": "http://example.com/audi.pdf",
    }
    r = AudiARep(data)
    md = r.to_markdown()
    assert "[Audição AR]" in md
    assert "[Texto Audição (pdf)]" in md


def test_audiarep_to_markdown_no_assunto():
    data = {"url": "http://example.com/aa1"}
    assert AudiARep(data).to_markdown() is None


# --- Interven ---


def test_interven_to_markdown_full():
    data = {
        "url": "http://example.com/i1",
        "Assunto": "Intervenção X",
        "Video": "http://example.com/video",
        "Data": "03/03/2024",
    }
    md = Interven(data).to_markdown()
    assert "[Intervenção X]" in md
    assert "[video]" in md
    assert "Data: 03/03/2024" in md


def test_interven_to_markdown_no_assunto():
    data = {"url": "http://example.com/i1"}
    assert Interven(data).to_markdown() is None


# --- Peti ---


def test_peti_to_markdown_full():
    data = {
        "url": "http://example.com/p1",
        "Assunto": "Petição Y",
        "Autor": "Maria",
        "Petição": "http://example.com/pet.pdf",
        "Data entrada": "04/04/2024",
        "Estado": "Em apreciação",
        "Comissão": "Assuntos Sociais",
    }
    md = Peti(data).to_markdown()
    assert "[Petição Y]" in md
    assert "Maria" in md
    assert "[Petição (pdf)]" in md
    assert "Estado: Em apreciação" in md
    assert "Comissão: Assuntos Sociais" in md


def test_peti_to_markdown_no_assunto():
    data = {"url": "http://example.com/p1"}
    assert Peti(data).to_markdown() is None


# --- Info ---


def test_info_to_markdown_full():
    data = {
        "url": "http://example.com/n1",
        "Assunto": "Nota de Pesar",
        "Texto Informação": "http://example.com/info.pdf",
    }
    md = Info(data).to_markdown()
    assert "[Nota de Pesar]" in md
    assert "[pdf]" in md


def test_info_to_markdown_no_assunto():
    data = {"url": "http://example.com/n1"}
    assert Info(data).to_markdown() is None


def test_info_export_table_row():
    data = {
        "url": "http://example.com/n1",
        "Assunto": "Test",
        "Texto Informação": "http://example.com/info.pdf",
    }
    headers = ["link", "Assunto", "Texto Informação"]
    row = Info(data).export_table_row(headers=headers)
    assert "[link]" in row[0]
    assert row[1] == "Test"
    assert "[Informação]" in row[2]


# --- Iniciativa ---


def test_iniciativa_to_markdown_full():
    data = {
        "url": "http://example.com/ini1",
        "Assunto": "Projeto de lei",
        "Titulo": "PJL 1",
        "Data de entrada": "05/05/2024",
        "Autor do texto inicial": "PS",
        "Tema": "Educação",
        "Texto Iniciativa": "http://example.com/ini.pdf",
        "Estado": "Aprovado",
    }
    md = Iniciativa(data).to_markdown()
    assert "[Projeto de lei]" in md
    assert "PJL 1" in md
    assert "Autor do texto inicial: PS" in md
    assert "Tema: Educação" in md
    assert "[Texto Iniciativa (pdf)]" in md
    assert "Resultado: Aprovado" in md


def test_iniciativa_to_markdown_no_assunto():
    data = {"url": "http://example.com/ini1"}
    assert Iniciativa(data).to_markdown() is None


def test_iniciativa_export_table_row():
    data = {
        "url": "http://example.com/ini1",
        "Nº Processo": "105",
        "Texto Iniciativa": "http://example.com/ini.pdf",
    }
    headers = ["Nº Processo", "Texto Iniciativa"]
    row = Iniciativa(data).export_table_row(headers=headers)
    assert "[105]" in row[0]
    assert "[Texto Iniciativa]" in row[1]


# --- Voto ---


def test_voto_to_markdown_full():
    data = {
        "url": "http://example.com/v1",
        "Assunto": "Voto de congratulação",
        "Titulo": "VC 1",
        "Autores": "PSD",
        "Resultado": "Aprovado",
        "Texto Voto Apresentado": "http://example.com/va.pdf",
        "Texto Voto Aprovado": "http://example.com/vap.pdf",
        "Video": "http://example.com/video",
        "Data entrada": "06/06/2024",
    }
    md = Voto(data).to_markdown()
    assert "[Voto de congratulação]" in md
    assert "VC 1" in md
    assert "Autores: PSD" in md
    assert "[pdf - voto apresentado]" in md
    assert "[pdf - voto aprovado]" in md
    assert "[video]" in md


def test_voto_to_markdown_no_assunto():
    data = {"url": "http://example.com/v1"}
    assert Voto(data).to_markdown() is None


def test_voto_export_table_row():
    data = {
        "url": "http://example.com/v1",
        "Nº Entrada": "1550",
        "Texto Voto Apresentado": "http://example.com/va.pdf",
        "Texto Voto Aprovado": "http://example.com/vap.pdf",
    }
    headers = ["Nº Entrada", "Texto Voto Apresentado", "Texto Voto Aprovado"]
    row = Voto(data).export_table_row(headers=headers)
    assert "[1550]" in row[0]
    assert "[Texto Voto Apresentado]" in row[1]
    assert "[Texto Voto Aprovado]" in row[2]


def test_voto_export_table_row_no_docs():
    data = {
        "url": "http://example.com/v1",
        "Nº Entrada": "1550",
    }
    headers = ["Nº Entrada", "Texto Voto Apresentado", "Texto Voto Aprovado"]
    row = Voto(data).export_table_row(headers=headers)
    assert row[1] is None
    assert row[2] is None
