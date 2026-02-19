SAA_CORPORATE (console) - Cadastro de notas no ERP Corporate (JBS)

1) Arquivo de entrada: input/notas.txt
Formato:
[PRODUTOR]
NOME=...
TIPO=PF|PJ
INSTRUCAO=1234
PEDIDO=opcional
NOTAS:
<chave 44 digitos>
<chave 44 digitos>

Regras:
- Ignora linhas vazias
- Ignora comentarios iniciados com #
- Cada chave precisa ter 44 digitos numericos

2) Como rodar
- Opcao A (Python portatil):
  a) Rode tools\setup_runtime_winpython.bat
  b) Rode run_portable.bat

- Opcao local (Python ja instalado):
  run_local_python.bat

- Opcao B (gerar EXE):
  a) Rode tools\build_exe.bat
  b) Execute dist\SAA_Notas.exe

3) Como parar imediatamente
- Pressione ESC
- Ou mova o mouse para o canto superior esquerdo (failsafe pyautogui)

4) Dicas importantes
- Deixe o Corporate em foco na tela de lancamento
- O script pressiona F2 automaticamente
- Ajuste delays em app\config.py se o ERP estiver lento
- A automacao usa somente teclado + clipboard (sem cliques de mouse)
