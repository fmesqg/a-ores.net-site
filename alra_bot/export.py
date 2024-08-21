from tabulate import tabulate

from .fetch import (
    fetch_info,
    fetch_iniciativa,
    fetch_requerimento,
    fetch_voto,
)


class Export:
    def req_markdown(delta):
        assert delta is not None, "req: delta is None."
        table_headers = [
            "Número",
            "Data entrada",
            "Alteração do Status",
            "Texto Requerimento",
            "Requerente(s)",
            "Assunto",
            "Texto Resposta",
            "Data da entrada da resposta",
        ]
        reqs_wide = [(fetch_requerimento(id), prev, now) for id, prev, now in delta]
        rows = [
            row
            for req, prev, now in reqs_wide
            if (row := req.export_markdown(headers=table_headers, prev=prev, now=now))
        ]
        return "## Requerimentos\n\n" + tabulate(
            rows, headers=table_headers, tablefmt="github"
        )

    def info_markdown(delta):
        assert delta is not None, "infos: delta is None."
        table_headers = [
            "Data",
            "Tipo",
            "Autor",
            "Assunto",
            "Texto Informação",
            "link",
        ]
        rows = [fetch_info(id).export_markdown(headers=table_headers) for id in delta]
        return "## Informações\n\n " + tabulate(
            rows, headers=table_headers, tablefmt="github"
        )

    def votos_markdown(delta):
        assert delta is not None, "votos: delta is None."
        table_headers = [
            "Nº Entrada",
            "Data entrada",
            "Titulo",
            "Autores",
            "Assunto",
            "Resultado",
            "Texto Voto Apresentado",
            "Texto Voto Aprovado",
        ]

        rows = [fetch_voto(id).export_markdown(headers=table_headers) for id in delta]
        return "## Votos\n\n" + tabulate(rows, headers=table_headers, tablefmt="github")

    def ini_markdown(delta):
        assert delta is not None, "ini: delta is None."
        table_headers = [
            "Nº Processo",
            "Data de entrada",
            "Titulo",
            "Autor do texto inicial",
            "Assunto",
            "Tema",
            "Texto Iniciativa",
            "Comissão",
            "Com pedido de",
        ]
        rows = [
            fetch_iniciativa(id).export_markdown(headers=table_headers) for id in delta
        ]
        return "## Iniciativas\n\n " + tabulate(
            rows, headers=table_headers, tablefmt="github"
        )

    def markdown(k, v):
        match k:
            case "requerimentos":
                return Export.req_markdown(v)
            case "informacoes":
                return Export.info_markdown(v)
            case "votos":
                return Export.votos_markdown(v)
            case "iniciativas":
                return Export.ini_markdown(v)
            case _:
                raise RuntimeError(f"unknown delta: {k}.")
