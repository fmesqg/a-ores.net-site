from abc import abstractmethod


class Record:
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def export_markdown(self, **kwargs): ...


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

    def export_markdown(self, *, headers, prev, now):
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


class Info(Record):
    def export_markdown(self, *, headers):
        x = self.data
        x["link"] = f"[link]({x['url']})"
        x["Texto Informação"] = (
            f"[Informação]({t})" if (t := x.get("Texto Informação", None)) else None
        )
        return [x.get(header, "") for header in headers]


class Iniciativa(Record):
    def export_markdown(self, *, headers):
        x = self.data
        x["Nº Processo"] = f"[{x['Nº Processo']}]({x['url']})"
        x["Texto Iniciativa"] = (
            f"[Texto Iniciativa]({t})"
            if (t := x.get("Texto Iniciativa", None))
            else None
        )
        return [x.get(header, "") for header in headers]


class Voto(Record):
    def export_markdown(self, *, headers):
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
