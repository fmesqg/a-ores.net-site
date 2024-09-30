from .fetch import fetch_record
from .record import (
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


class Export:
    def markdown(delta: dict) -> str:
        _state_keys_to_simple_types = {
            # "requerimentos": Requerimento,
            "informacoes": Info,
            "diarios": Diario,
            "votos": Voto,
            "iniciativas": Iniciativa,
            "intervencoes": Interven,
            "peticoes": Peti,
            "audi_gr": AudiGRep,
            "audi_ar": AudiARep,
        }
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

        def simple_record_markdown(record_type: type, delta_ids):
            return f"### {_types_to_print_names[record_type]}\n\n" + "\n".join(
                [
                    md
                    for id in delta_ids
                    if (md := fetch_record(record_type, id).to_markdown())
                ]
            )

        def req_markdown(delta):
            reqs_wide = [
                (fetch_record(Requerimento, id), prev, now) for id, prev, now in delta
            ]
            rows = [
                row
                for req, prev, now in reqs_wide
                if (row := req.to_markdown(prev=prev, now=now))
            ]
            return "### Requerimentos\n\n" + "\n".join(rows)

        md = [
            simple_record_markdown(record_type, ids)
            for k, ids in delta.items()
            if (record_type := _state_keys_to_simple_types.get(k))
        ]
        if "requerimentos" in delta:
            md.insert(0, req_markdown(delta["requerimentos"]))

        return "## ALRA\n\n" + "\n\n".join(md)
