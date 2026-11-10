# base_conhecimento.py - classe BaseConhecimento

import json
import os

from orientacao import Orientacao

PASTA_DO_PROJETO = os.path.dirname(os.path.abspath(__file__))

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação, com espaço nas pontas."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Conjunto de todas as orientações. Lê o JSON e faz a busca."""

    def __init__(self, caminho):
        # Caminho relativo vira caminho a partir da pasta do projeto
        if not os.path.isabs(caminho):
            caminho = os.path.join(PASTA_DO_PROJETO, caminho)
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Retorna True se deu certo."""
        try:
            with open(self.caminho, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            self.orientacoes = [Orientacao(**registro) for registro in dados]
            return True
        except FileNotFoundError:
            print("Erro: a base de conhecimento não foi encontrada.")
        except json.JSONDecodeError:
            print("Erro: a base de conhecimento está corrompida (JSON inválido).")
        except TypeError:
            print("Erro: alguma orientação da base está com campos faltando ou a mais.")
        return False

    def categorias(self):
        """Retorna a lista de categorias, sem repetição e em ordem alfabética."""
        return sorted({orientacao.categoria for orientacao in self.orientacoes})

    def por_categoria(self, categoria):
        """Retorna as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]
