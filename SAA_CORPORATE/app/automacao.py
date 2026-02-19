"""Automação por teclado do ERP Corporate."""

from __future__ import annotations

import time

import keyboard
import pyautogui
import pyperclip

from config import (
    CODE_PF,
    CODE_PJ,
    DELAY_AFTER_F2,
    DELAY_AFTER_F4,
    DELAY_AFTER_INSTRUCAO,
    DELAY_AFTER_PASTE,
    DELAY_AFTER_TAB,
    DELAY_AFTER_TIPO,
    FINAL_DELAY_ENTER,
    FINAL_DELAY_F4,
    FINAL_DELAY_RIGHT,
    START_DELAY,
)


class AutomationAbort(Exception):
    """Interrupção controlada (ESC)."""


class AutomationFailSafe(Exception):
    """Interrupção de failsafe do pyautogui."""


class Automator:
    def __init__(self, producers: list[dict], logger):
        self.producers = producers
        self.logger = logger
        self.ok_count = 0
        self.error_count = 0

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.02

    def _check_stop(self) -> None:
        if keyboard.is_pressed("esc"):
            self.logger.warn("ABORTADO ESC | Tecla ESC detectada.")
            raise AutomationAbort("Interrompido por ESC")

    def countdown_focus(self) -> None:
        for seconds in range(START_DELAY, 0, -1):
            self._check_stop()
            print(f"Iniciando em {seconds}... foque o ERP Corporate.")
            self.logger.info("Contagem regressiva: %s", seconds)
            time.sleep(1)

    def press_f2(self) -> None:
        pyautogui.press("f2")
        time.sleep(DELAY_AFTER_F2)

    def paste_text(self, text: str) -> None:
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(DELAY_AFTER_PASTE)

    def tab(self) -> None:
        pyautogui.press("tab")
        time.sleep(DELAY_AFTER_TAB)

    def type_instrucao(self, instrucao: str) -> None:
        pyautogui.typewrite(instrucao)
        time.sleep(DELAY_AFTER_INSTRUCAO)
        self.tab()

    def type_tipo_doc(self, producer_type: str) -> None:
        code = CODE_PF if producer_type == "PF" else CODE_PJ
        pyautogui.typewrite(code)
        time.sleep(DELAY_AFTER_TIPO)

    def press_f4(self) -> None:
        pyautogui.press("f4")

    def finalize_producer(self) -> None:
        self.press_f4()
        time.sleep(FINAL_DELAY_F4)
        pyautogui.press("right")
        time.sleep(FINAL_DELAY_RIGHT)
        pyautogui.press("enter")
        time.sleep(FINAL_DELAY_ENTER)

    def run(self) -> tuple[int, int]:
        try:
            for producer in self.producers:
                self._check_stop()
                name = producer["nome"]
                ptype = producer["tipo"]
                instrucao = producer["instrucao"]
                notas = producer["notas"]

                self.logger.info("Produtor: %s | Tipo: %s | Notas: %s", name, ptype, len(notas))
                self.press_f2()
                self.type_instrucao(instrucao)

                for chave in notas:
                    self._check_stop()
                    self.paste_text(chave)
                    self.tab()
                    self.type_tipo_doc(ptype)
                    self.press_f4()
                    time.sleep(DELAY_AFTER_F4)
                    self.ok_count += 1
                    self.logger.info("CHAVE OK | %s | %s", name, chave)

                self._check_stop()
                self.finalize_producer()
                self.logger.info("Produtor finalizado: %s", name)

            return self.ok_count, self.error_count

        except pyautogui.FailSafeException as exc:
            self.logger.warn("ABORTADO FAILSAFE | Mouse no canto superior esquerdo.")
            raise AutomationFailSafe("ABORTADO FAILSAFE") from exc
        except AutomationAbort:
            raise
        except Exception as exc:
            self.error_count += 1
            self.logger.exception("Erro inesperado durante automação: %s", exc)
            raise
