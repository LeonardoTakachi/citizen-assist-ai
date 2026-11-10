# main.py - ponto de entrada do Citizen Assist AI
import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")

def mostrar_menu():
    print("\n===== MENU =====")
    print("1. Fazer uma pergunta")
    print("2. Navegar por categorias")
    print("3. Ver indicadores")
    print("4. Exportar atendimentos para CSV")
    print("0. Sair")

def ler_opcao_menu():
    """Lê a opção do menu. Opção inválida nunca encerra o programa."""
    while True:
        try:
            resposta = input("Escolha uma opção: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not resposta:
            print("Digite um número de 0 a 4.")
        elif not resposta.isdecimal():
            print("Opção inválida: digite apenas números.")
        elif int(resposta) > 4:
            print("Opção inválida: escolha de 0 a 4.")
        else:
            return int(resposta)


def main():
    base = BaseConhecimento(CAMINHO_BASE)
    base.carregar()  # lê o JSON e cria os objetos Orientacao

    if not base.orientacoes:
        print("Aviso: a base de conhecimento está vazia ou não foi carregada.")
        print("Confira o arquivo data/base_conhecimento.json.")

    assistente = Assistente("Citizen Assist AI", base)
    assistente.boas_vindas()

    while True:
        mostrar_menu()
        opcao = ler_opcao_menu()

        if opcao == 1:
            assistente.perguntar()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        else:  # 0
            assistente.encerrar()
            print("\nObrigado por usar o Citizen Assist AI. Até logo!")
            break

if __name__ == "__main__":
    main()