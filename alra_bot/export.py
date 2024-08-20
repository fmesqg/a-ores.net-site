from tabulate import tabulate

from .fetch import fetch_info, fetch_iniciativa, fetch_requerimento


class Export:

    def req_markdown(delta):
        assert delta is not None, "req: delta is None."
        reqs_table_headers = [
            "Link",
            "Data entrada",
            "Alteração do Status",
            "Texto Requerimento",
            # "Processo",
            "Requerente(s)",
            "Assunto",
            # "Data de envio ao G.R.",
            # "Anúncio em plenário do requerimento",
            "Texto Resposta",
            # "Data da resposta do G.R.",
            "Data da entrada da resposta",
            # "Anúncio em plenário da resposta",
        ]
        rows = []
        for id, prev, now in delta:
            x = fetch_requerimento(id)
            if len((requerentes := x["Requerente(s)"].split(";"))) > 1:
                x["Requerente(s)"] = requerentes[0] + " ..."
            x["Link"] = (
                f"[Link](http://base.alra.pt:82/4DACTION/w_pesquisa_registo/4/{id})"
            )
            prev_status = "Não existente" if prev is None else prev
            x["Alteração do Status"] = f"{prev_status} → {now}"
            x["Texto Requerimento"] = f"[Texto Requerimento]({x['Texto Requerimento']})"
            x["Texto Resposta"] = (
                f"[Texto Resposta]({t})"
                if (t := x.get("Texto Resposta", None))
                else None
            )

            rows.append([x.get(header, "") for header in reqs_table_headers])
        return "## Requerimentos\n\n" + tabulate(
            rows, headers=reqs_table_headers, tablefmt="github"
        )

    def info_markdown(delta):
        assert delta is not None, "infos: delta is None."
        info_table_headers = [
            "Link",
            "Data",
            "Tipo",
            "Autor",
            "Assunto",
            "Texto Informação",
        ]
        rows = []
        for id in delta:
            x = fetch_info(id)
            x["Link"] = (
                f"[Link](http://base.alra.pt:82/4DACTION/w_pesquisa_registo/8/{id})"
            )
            x["Texto Informação"] = (
                f"[Texto Informação]({t})"
                if (t := x.get("Texto Informação", None))
                else None
            )
            rows.append([x.get(header, "") for header in info_table_headers])
        return "## Informações\n\n " + tabulate(
            rows, headers=info_table_headers, tablefmt="github"
        )

    def votos_markdown(delta):
        assert delta is not None, "votos: delta is None."
        info_table_headers = [
            "Link",
            "Data entrada",
            "Titulo",
            "Autores",
            "Assunto",
            "Resultado",
            "Texto Voto Apresentado",
            "Texto Voto Aprovado",
        ]
        rows = []
        for id in delta:
            x = fetch_info(id)
            x["Link"] = (
                f"[Link](http://base.alra.pt:82/4DACTION/w_pesquisa_registo/1/{id})"
            )
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
            rows.append([x.get(header, "") for header in info_table_headers])
        return "## Votos\n\n" + tabulate(
            rows, headers=info_table_headers, tablefmt="github"
        )

    def ini_markdown(delta):
        assert delta is not None, "ini: delta is None."
        info_table_headers = [
            "Link",
            "Data de entrada",
            "Titulo",
            "Autor do texto inicial",
            "Assunto",
            "Tema",
            "Texto Iniciativa",
            "Comissão",
            "Com pedido de",
        ]
        rows = []
        for id in delta:
            x = fetch_iniciativa(id)
            x["Link"] = (
                f"[Link](http://base.alra.pt:82/4DACTION/w_pesquisa_registo/3/{id})"
            )
            x["Texto Iniciativa"] = (
                f"[Texto Iniciativa]({t})"
                if (t := x.get("Texto Iniciativa", None))
                else None
            )

            rows.append([x.get(header, "") for header in info_table_headers])
        return "## Iniciativas\n\n" + tabulate(
            rows, headers=info_table_headers, tablefmt="github"
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
