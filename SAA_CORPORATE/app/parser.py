"""Parser e validação do arquivo TXT de entrada."""

from __future__ import annotations

from pathlib import Path


def _new_producer() -> dict:
    return {
        "nome": "",
        "tipo": "",
        "instrucao": "",
        "pedido": None,
        "notas": [],
    }


def _validate_producer(producer: dict, index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"Produtor #{index}"

    nome = str(producer.get("nome", "")).strip()
    tipo = str(producer.get("tipo", "")).strip().upper()
    instrucao = str(producer.get("instrucao", "")).strip()
    notas = producer.get("notas", [])

    if not nome:
        errors.append(f"{prefix}: NOME é obrigatório.")

    if tipo not in {"PF", "PJ"}:
        errors.append(f"{prefix} ({nome or 'sem nome'}): TIPO deve ser PF ou PJ.")

    if not instrucao or not instrucao.isdigit():
        errors.append(f"{prefix} ({nome or 'sem nome'}): INSTRUCAO deve conter apenas dígitos.")

    if not isinstance(notas, list) or not notas:
        errors.append(f"{prefix} ({nome or 'sem nome'}): informe ao menos 1 chave em NOTAS.")
    else:
        for note_index, key in enumerate(notas, start=1):
            key_txt = str(key).strip()
            if not key_txt.isdigit() or len(key_txt) != 44:
                errors.append(
                    f"{prefix} ({nome or 'sem nome'}) nota {note_index}: chave inválida '{key_txt}'. "
                    "A chave deve ter exatamente 44 dígitos numéricos."
                )

    return errors


def load_producers(path: str) -> tuple[list[dict], list[str]]:
    file_path = Path(path)
    if not file_path.exists():
        return [], [f"Arquivo de entrada não encontrado: {file_path}"]

    producers: list[dict] = []
    errors: list[str] = []

    current: dict | None = None
    in_notes = False

    lines = file_path.read_text(encoding="utf-8").splitlines()

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        if not line:
            if in_notes:
                in_notes = False
            continue

        if line.startswith("#"):
            continue

        if line.upper() == "[PRODUTOR]":
            if current is not None:
                producers.append(current)
            current = _new_producer()
            in_notes = False
            continue

        if current is None:
            errors.append(f"Linha {line_number}: conteúdo fora de bloco [PRODUTOR].")
            continue

        if line.upper() == "NOTAS:":
            in_notes = True
            continue

        if in_notes:
            current["notas"].append(line)
            continue

        if "=" not in line:
            errors.append(f"Linha {line_number}: esperado formato CAMPO=VALOR.")
            continue

        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()

        if key == "NOME":
            current["nome"] = value
        elif key == "TIPO":
            current["tipo"] = value.upper()
        elif key == "INSTRUCAO":
            current["instrucao"] = value
        elif key == "PEDIDO":
            current["pedido"] = value or None
        else:
            errors.append(f"Linha {line_number}: campo desconhecido '{key}'.")

    if current is not None:
        producers.append(current)

    if not producers:
        errors.append("Nenhum bloco [PRODUTOR] encontrado no arquivo.")
        return [], errors

    for idx, producer in enumerate(producers, start=1):
        errors.extend(_validate_producer(producer, idx))

    return producers, errors
