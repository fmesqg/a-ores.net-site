from abc import abstractmethod


class Record:
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def export_table_row(self, **kwargs): ...

    @abstractmethod
    def to_markdown(self, **kwargs): ...


class Requerimento(Record):
    """_eg_ data:
    {
        "id": 8251,
        "Texto Requerimento": "http://base.alra.pt:82/Doc_Req/XIIIreque2.pdf",
        "Legislatura": "XIII",
        "Número": "2",
        "Data entrada": "29/02/2024",
        "Processo": "054.09.08",
        "Requerente(s)": "José Pacheco CH; José Sousa CH",
        "Assunto": "Falta de escoamento de pescado das Flores",
        "Data de envio ao G.R.": "06/03/2024",
        "Anúncio em plenário do requerimento": "13/03/2024",
        "Texto Resposta": "http://base.alra.pt:82/Doc_Req/XIIIrequeresp2.pdf",
        "Data da resposta do G.R.": "25/03/2024",
        "Data da entrada da resposta": "26/03/2024",
        "Anúncio em plenário da resposta": "09/04/2024",
    }
    """

    def export_table_row(self, *, headers, prev, now):
        x: dict = self.data
        if len((requerentes := x["Requerente(s)"].split(";"))) > 1:
            x["Requerente(s)"] = requerentes[0] + " ..."
        x["Número"] = f"[{x['Número']}]({x['url']})"
        prev_status = "Não existente" if prev is None else prev
        x["Alteração do Status"] = f"{prev_status} → {now}"
        x["Texto Requerimento"] = f"[Requerimento]({x['Texto Requerimento']})"
        x["Texto Resposta"] = (
            f"[Resposta]({t})" if (t := x.get("Texto Resposta", None)) else None
        )
        return [x.get(header, "") for header in headers]

    def to_markdown(self, *, prev, now):
        x: dict = self.data
        assunto = x.get("Assunto", x.get("id"))
        md = f"* [{assunto}]({x['url']})"
        status = (
            "Novo Requerimento"
            if prev is None
            else f"Alteração do estado: {prev} → {now}"
        )
        md += f"\n  * {status}"
        if doc_req := x.get("Texto Requerimento", None):
            md += (
                f"\n  * [requerimento]({doc_req}) ( data entrada: {x['Data entrada']})"
            )
        if doc_resp := x.get("Texto Resposta", None):
            md += f"\n  * [resposta]({doc_resp}) (data entrada resposta: {x['Data da entrada da resposta']})"  # noqa: 501
        if len((requerentes := x["Requerente(s)"].split(";"))) > 1:
            x["Requerente(s)"] = requerentes[0] + ", ..."
        md += f"\n  * Requerente(s): {x['Requerente(s)']}"

        return md


class Info(Record):
    def export_table_row(self, *, headers):
        x = self.data
        x["link"] = f"[link]({x['url']})"
        x["Texto Informação"] = (
            f"[Informação]({t})" if (t := x.get("Texto Informação", None)) else None
        )
        return [x.get(header, "") for header in headers]

    def to_markdown(self):
        x = self.data
        if not (assunto := x.get("Assunto")):
            return None
        md = f"* [{assunto}]({x['url']})"
        if doc := x.get("Texto Informação", None):
            md += f"\n  * [pdf]({doc})"
        return md


class Iniciativa(Record):
    def to_markdown(self):
        x = self.data
        if not (assunto := x.get("Assunto")):
            return None
        md = f"* [{assunto}]({x['url']})"
        if titulo := x.get("Titulo", None):
            md += f"\n  * {titulo}"
        if entrada := x.get("Data de entrada", None):
            md += f"\n  * Dada de entrada: {entrada}"
        if aut := x.get("Autor do texto inicial", None):
            md += f"\n  * Autor do texto inicial: {aut}"
        if tema := x.get("Tema", None):
            md += f"\n  * Tema: {tema}"
        if pdf_apresentado := x.get("Texto Iniciativa", None):
            md += f"\n  * [Texto Iniciativa (pdf)]({pdf_apresentado})"
        if estado := x.get("Estado", None):
            md += f"\n  * Resultado: {estado}"
        return md

    def export_table_row(self, *, headers):
        x = self.data
        x["Nº Processo"] = f"[{x['Nº Processo']}]({x['url']})"
        x["Texto Iniciativa"] = (
            f"[Texto Iniciativa]({t})"
            if (t := x.get("Texto Iniciativa", None))
            else None
        )
        return [x.get(header, "") for header in headers]


class Voto(Record):
    def export_table_row(self, *, headers):
        x = self.data
        x["Nº Entrada"] = f"[{x['Nº Entrada']}]({x['url']})"
        x["Texto Voto Apresentado"] = (
            f"[Texto Voto Apresentado]({t})"
            if (t := x.get("Texto Voto Apresentado", None))
            else None
        )
        x["Texto Voto Aprovado"] = (
            f"[Texto Voto Aprovado]({t})"
            if (t := x.get("Texto Voto Aprovado", None))
            else None
        )
        return [x.get(header, "") for header in headers]

    def to_markdown(self):
        x = self.data
        if not (assunto := x.get("Assunto")):
            return None
        md = f"* [{assunto}]({x['url']})"
        if titulo := x.get("Titulo", None):
            md += f"\n  * {titulo}"
        if autores := x.get("Autores", None):
            md += f"\n  * Autores: {autores}"
        if resultado := x.get("Resultado", None):
            md += f"\n  * Resultado: {resultado}"
        if pdf_apresentado := x.get("Texto Voto Apresentado", None):
            md += f"\n  * [pdf - voto apresentado]({pdf_apresentado})"
        if pdf_aprovado := x.get("Texto Voto Aprovado", None):
            md += f"\n  * [pdf - voto aprovado]({pdf_aprovado})"
        if video := x.get("Video", None):
            md += f"\n  * [video]({video})"
        if entrada := x.get("Data entrada", None):
            md += f"\n  * Dada de entrada: {entrada}"
        return md
