"""Aplicação console principal do SAA Corporate."""

from __future__ import annotations

import sys
from pathlib import Path

from logger import make_logger
from parser import load_producers


def _input_path() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).expanduser()
    return Path(__file__).resolve().parent.parent / "input" / "notas.txt"


def _print_summary(producers: list[dict]) -> None:
    total_prod = len(producers)
    total_notes = 0
    total_pf = 0
    total_pj = 0

    print("\n=== RESUMO DA CARGA ===")
    for i, producer in enumerate(producers, start=1):
        count_notes = len(producer["notas"])
        total_notes += count_notes
        if producer["tipo"] == "PF":
            total_pf += count_notes
        else:
            total_pj += count_notes

        print(
            f"{i:02d}. {producer['nome']} | tipo={producer['tipo']} | "
            f"instrução={producer['instrucao']} | notas={count_notes}"
        )

    print(f"\nTotal produtores: {total_prod}")
    print(f"Total notas: {total_notes}")
    print(f"Notas PF: {total_pf}")
    print(f"Notas PJ: {total_pj}")


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    log, log_path = make_logger(str(base_dir / "logs"))

    input_path = _input_path()
    log.info("SAA Corporate iniciado")
    log.info("Arquivo de entrada: %s", input_path)

    producers, errors = load_producers(str(input_path))
    if errors:
        print("\nForam encontrados erros de validação no arquivo de entrada:\n")
        for err in errors:
            print(f" - {err}")
            log.error(err)
        print(f"\nLog: {log_path}")
        return 2

    _print_summary(producers)

    answer = input("\nCONFIRMAR INICIO? (S/N): ").strip().upper()
    if answer != "S":
        print("Execução cancelada pelo usuário.")
        log.warn("Execução cancelada antes da automação.")
        print(f"Log: {log_path}")
        return 0

    print("\nDeixe o Corporate em foco. O script vai pressionar F2.")
    print("Para interromper: ESC ou failsafe (mouse no canto superior esquerdo).")

    try:
        from automacao import AutomationAbort, AutomationFailSafe, Automator
    except ModuleNotFoundError as exc:
        missing = exc.name or "dependência"
        print(f"\nDependência ausente: {missing}")
        print("Instale com: pip install pyautogui pyperclip keyboard")
        print(f"Log: {log_path}")
        log.error("Dependência ausente: %s", missing)
        return 1

    automator = Automator(producers, log)

    try:
        automator.countdown_focus()
        ok_count, error_count = automator.run()

        print("\n=== RESULTADO ===")
        print("Status: SUCESSO")
        print(f"Chaves lançadas com sucesso: {ok_count}")
        print(f"Erros: {error_count}")
        print(f"Log: {log_path}")
        return 0

    except (AutomationAbort, AutomationFailSafe) as exc:
        print("\n=== RESULTADO ===")
        print(f"Status: INTERROMPIDO ({exc})")
        print(f"Log: {log_path}")
        return 3
    except Exception as exc:
        print("\nErro inesperado durante execução.")
        print(f"Detalhes: {exc}")
        print(f"Log: {log_path}")
        log.exception("Erro inesperado no console: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
