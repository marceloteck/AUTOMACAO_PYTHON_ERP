import time
import re
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

import pyautogui
import pyperclip
import keyboard

# ========= CONFIG =========
START_DELAY = 3
DELAY_AFTER_PASTE = 0.15
DELAY_AFTER_ENTER = 0.25
DELAY_AFTER_F4 = 0.55
DELAY_BETWEEN_NOTES = 0.20

CODE_PF = "2630"
CODE_PJ = "2629"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02

stop_flag = False


def parse_text(text: str):
    """
    Formato:
      INSTRUCAO=PECUARISTA_PF ou PECUARISTA_PJ
      CHAVE=...
    """
    instr = "PECUARISTA_PF"
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("INSTRUCAO="):
            instr = line.split("=", 1)[1].strip().upper()
            continue
        if line.upper().startswith("CHAVE="):
            chave = line.split("=", 1)[1].strip()
            chave = re.sub(r"\s+", "", chave)
            if chave:
                items.append((instr, chave))
    return items


def code_for(instr: str) -> str:
    return CODE_PJ if instr == "PECUARISTA_PJ" else CODE_PF


def paste_text(s: str):
    pyperclip.copy(s)
    pyautogui.hotkey("ctrl", "v")


def finalize_pecuarista():
    # Final do lote: F4 -> Right -> Enter (selecionar "NAO")
    time.sleep(0.25)
    pyautogui.press("f4")
    time.sleep(0.60)
    pyautogui.press("right")
    time.sleep(0.20)
    pyautogui.press("enter")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SAA - Cadastro de Notas (Pecuarista)")
        self.geometry("900x600")

        self.queue = []

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text="Cole aqui as instruções/chaves:").pack(anchor="w")

        self.txt = scrolledtext.ScrolledText(self, wrap="word", height=18)
        self.txt.pack(fill="both", expand=True, padx=10)

        # Exemplo pronto
        self.txt.insert("1.0", 
"""INSTRUCAO=PECUARISTA_PF
CHAVE=3524...

INSTRUCAO=PECUARISTA_PJ
CHAVE=3524...
""")

        controls = tk.Frame(self)
        controls.pack(fill="x", padx=10, pady=10)

        self.btn_analisar = tk.Button(controls, text="Analisar", command=self.analisar)
        self.btn_analisar.pack(side="left")

        self.btn_iniciar = tk.Button(controls, text="Iniciar Automação", command=self.iniciar, state="disabled")
        self.btn_iniciar.pack(side="left", padx=8)

        self.btn_stop = tk.Button(controls, text="STOP (ESC)", command=self.stop, state="disabled")
        self.btn_stop.pack(side="left")

        self.lbl = tk.Label(controls, text="Status: aguardando...", anchor="w")
        self.lbl.pack(side="left", padx=12)

        hint = tk.Label(self, text="Dicas: deixe o Corporate focado no campo da CHAVE. ESC para parar. Mouse no canto superior esquerdo para abortar.",
                        fg="gray")
        hint.pack(fill="x", padx=10, pady=(0,10))

        keyboard.add_hotkey("esc", self.stop)

    def set_status(self, s: str):
        self.lbl.config(text=f"Status: {s}")
        self.update_idletasks()

    def analisar(self):
        text = self.txt.get("1.0", "end").strip()
        q = parse_text(text)
        if not q:
            messagebox.showerror("Erro", "Nenhuma CHAVE encontrada.\nUse linhas CHAVE=...")
            self.btn_iniciar.config(state="disabled")
            return

        pf = sum(1 for instr, _ in q if instr != "PECUARISTA_PJ")
        pj = sum(1 for instr, _ in q if instr == "PECUARISTA_PJ")

        self.queue = q
        self.btn_iniciar.config(state="normal")
        messagebox.showinfo("Análise", f"Total: {len(q)}\nPF (2630): {pf}\nPJ (2629): {pj}")

    def iniciar(self):
        global stop_flag
        if not self.queue:
            messagebox.showwarning("Aviso", "Clique em Analisar primeiro.")
            return

        stop_flag = False
        self.btn_iniciar.config(state="disabled")
        self.btn_analisar.config(state="disabled")
        self.btn_stop.config(state="normal")

        t = threading.Thread(target=self.worker, daemon=True)
        t.start()

    def stop(self):
        global stop_flag
        stop_flag = True
        self.set_status("parando...")

    def worker(self):
        global stop_flag
        try:
            self.set_status(f"iniciando em {START_DELAY}s (focar Corporate)")
            time.sleep(START_DELAY)

            total = len(self.queue)
            for i, (instr, chave) in enumerate(self.queue, start=1):
                if stop_flag:
                    self.set_status("interrompido")
                    return

                codigo = code_for(instr)

                # 1) colar chave
                paste_text(chave)
                time.sleep(DELAY_AFTER_PASTE)

                # 2) digitar codigo
                pyautogui.write(codigo, interval=0.01)

                # 3) ENTER
                pyautogui.press("enter")
                time.sleep(DELAY_AFTER_ENTER)

                # 4) F4
                pyautogui.press("f4")
                time.sleep(DELAY_AFTER_F4)

                self.set_status(f"{i}/{total} - {instr} - codigo {codigo}")
                time.sleep(DELAY_BETWEEN_NOTES)

            if stop_flag:
                self.set_status("interrompido")
                return

            self.set_status("finalizando (F4 > direita > enter)")
            finalize_pecuarista()
            self.set_status("finalizado com sucesso")
            messagebox.showinfo("Concluído", "Automação finalizada com sucesso.")

        except pyautogui.FailSafeException:
            self.set_status("ABORTADO (failsafe)")
            messagebox.showwarning("Abortado", "FailSafe acionado (mouse no canto superior esquerdo).")
        except Exception as e:
            self.set_status("erro")
            messagebox.showerror("Erro", f"Erro na automação:\n{e}")
        finally:
            self.btn_iniciar.config(state="normal")
            self.btn_analisar.config(state="normal")
            self.btn_stop.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()
