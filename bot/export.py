from typing import List, Union

from bot.classes import FetchError

from .record import (
    AudiARep,
    AudiGRep,
    Diario,
    Info,
    Iniciativa,
    Interven,
    Peti,
    Record,
    Requerimento,
    Voto,
)


class Export:
    def markdown(blob: Union[FetchError, dict]) -> str:
        _types_to_print_names = {
            Diario: "Diários",
            Interven: "Intervenções",
            Requerimento: "Requerimentos",
            Info: "Informações",
            Voto: "Votos",
            Iniciativa: "Iniciativas",
            Peti: "Petições",
            AudiGRep: "Audições - Governo da República",
            AudiARep: "Audições - Assembleia da República",
        }

        def simple_record_markdown(record_type: type, records: List[Record]):
            return f"### {_types_to_print_names[record_type]}\n\n" + "\n".join(
                [md for x in records if (md := x.to_markdown())]
            )

        def req_markdown(reqs_wide):

            rows = [
                row
                for req, prev, now in reqs_wide
                if (row := req.to_markdown(prev=prev, now=now))
            ]
            return "### Requerimentos\n\n" + "\n".join(rows)

        if isinstance(blob, FetchError):
            return "## ALRA\n\n" + "Sem ligação a `alra.pt`"
        md = [
            simple_record_markdown(k, records)
            for k, records in blob.items()
            if k
            in [
                Info,
                Diario,
                Voto,
                Iniciativa,
                Interven,
                Peti,
                AudiGRep,
                AudiARep,
            ]
        ]
        if Requerimento in blob:
            md.insert(0, req_markdown(blob[Requerimento]))

        if md:
            return "## ALRA\n\n" + "\n\n".join(md)
        return ""
