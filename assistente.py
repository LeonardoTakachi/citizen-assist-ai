# assistente.py - classe Assistente
# Faz o atendimento, guarda o histórico e calcula os indicadores.
import csv
import json
import os
import time
from datetime import datetime

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_HISTORICO = os.path.join(PASTA, "data", "historico.json")
CAMINHO_CSV = os.path.join(PASTA, "data", "atendimentos.csv")

# Limites da confiança
LIMITE_ALTA = 6    # 6 pontos ou mais -> ALTA
LIMITE_MEDIA = 3   # 3 a 5 pontos -> MÉDIA; abaixo disso -> "não encontrei"
MAX_ALTERNATIVAS = 2

CAMPOS_CSV = ["data", "sessao", "origem", "pergunta", "id_orientacao", "encontrou", "ajudou", "tentativas", "tempo_segundos", "facilidade"]

class Assistente:
    """Quem conversa com o cidadão: atende, registra e calcula indicadores."""

    def __init__(self, nome, base, caminho_historico=CAMINHO_HISTORICO, caminho_csv=CAMINHO_CSV):
        self.nome = nome
        self.base = base  # objeto BaseConhecimento (composição)
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        # identifica esta execução; usado para contar uma nota de facilidade por sessão
        self.sessao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.historico = self.carregar_historico()

    # ------------------------------------------------------------------
    # Entrada de dados e validações
    # ------------------------------------------------------------------
    @staticmethod
    def entrada(texto):
        """Lê uma linha do teclado. Devolve None se a entrada for interrompida."""
        try:
            return input(texto).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

    @staticmethod
    def contem_dado_pessoal(texto):
        """Dado pessoal = tem '@' (e-mail) ou 8 ou mais dígitos (CPF, telefone)."""
        digitos = sum(1 for letra in texto if letra.isdigit())
        return "@" in texto or digitos >= 8

    @staticmethod
    def confianca(pontos):
        """Converte pontos em nível de confiança."""
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None

    def ler_opcao(self, maximo, texto="Escolha uma opção: "):
        """Lê um número de 0 a maximo. Entrada inválida nunca encerra o programa."""
        while True:
            resposta = self.entrada(texto)
            if resposta is None:
                return 0
            if not resposta:
                print("Digite um número.")
            elif not resposta.isdecimal():
                print("Opção inválida: digite apenas números.")
            elif int(resposta) > maximo:
                print(f"Opção inválida: escolha de 0 a {maximo}.")
            else:
                return int(resposta)

    def perguntar_sim_nao(self, texto):
        """Pergunta s/n e repete até a resposta ser válida."""
        while True:
            resposta = self.entrada(texto)
            if resposta is None:
                return False
            resposta = resposta.lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            print("Resposta inválida: digite s para sim ou n para não.")

    # ------------------------------------------------------------------
    # Atendimento
    # ------------------------------------------------------------------
    def boas_vindas(self):
        print("=" * 50)
        print(f"  {self.nome}")
        print("  Orientação ao consumidor")
        print("=" * 50)
        print("Aviso: este assistente NÃO é um canal oficial.")
        print("Nunca peço nome, CPF, telefone ou e-mail. Não digite esses dados.")

    def perguntar(self):
        """Atendimento por texto livre: busca com pontuação na base."""
        while True:  # cada volta é um atendimento novo
            inicio = time.time()
            tentativas = 0
            encontrou = False
            id_orientacao = None
            ultima_pergunta = ""

            while True:
                pergunta = self.entrada("\nDigite sua dúvida (0 para voltar): ")

                if pergunta is None or pergunta == "0":
                    if tentativas > 0:  # tentou e desistiu: registra sem solução
                        self.registrar("pergunta", ultima_pergunta,
                                       id_orientacao, encontrou, False,
                                       tentativas,
                                       round(time.time() - inicio, 1))
                    return

                if not pergunta:
                    print("Digite sua dúvida ou 0 para voltar.")
                    continue

                if len(pergunta) < 3:
                    print("Escreva sua dúvida com um pouco mais de detalhes (ou 0 para voltar).")
                    continue

                if self.contem_dado_pessoal(pergunta):
                    # não conta como tentativa e não é registrada
                    print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                    continue

                tentativas += 1
                ultima_pergunta = pergunta

                resultados = self.base.buscar(pergunta)  # lista de (pontos, orientacao)
                validos = [(p, o) for p, o in resultados if p >= LIMITE_MEDIA]

                if not validos:
                    self.mostrar_nao_encontrei()
                    continue

                pontos, melhor = validos[0]
                encontrou = True
                id_orientacao = melhor.id

                print(f"\nConfiança da resposta: {self.confianca(pontos)} ({pontos} pontos)")
                melhor.exibir()
                self.mostrar_alternativas(validos[1:1 + MAX_ALTERNATIVAS])

                if self.perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                    self.registrar("pergunta", pergunta, melhor.id, True, True,
                                   tentativas, round(time.time() - inicio, 1))
                    break
                print("Tente reescrever a pergunta com outras palavras, ou digite 0 para voltar.")

    def mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Tente usar outras palavras ou navegue pelas categorias (opção 2 do menu):")
        for categoria in self.base.categorias():
            print(f"  - {categoria}")
        print("Aviso: este assistente NÃO é um canal oficial.")

    @staticmethod
    def mostrar_alternativas(alternativas):
        if not alternativas:
            return
        print("\nOutras orientações que podem ajudar:")
        for pontos, orientacao in alternativas:
            print(f"  - {orientacao.titulo} [{orientacao.categoria}] ({pontos} pontos)")

    def navegar(self):
        """Navegação por categorias, com '0 para voltar' em todas as telas."""
        while True:
            categorias = self.base.categorias()
            if not categorias:
                print("\nA base de conhecimento está vazia.")
                return

            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero}. {categoria}")
            print("  0. Voltar")

            escolha = self.ler_opcao(len(categorias), "Escolha uma categoria: ")
            if escolha == 0:
                return
            self.navegar_categoria(categorias[escolha - 1])

    def navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        if not orientacoes:
            print("\nNão há orientações nessa categoria.")
            return

        inicio = time.time()
        tentativas = 0
        ultima = None

        while True:
            print(f"\n{categoria}:")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"  {numero}. {orientacao.titulo}")
            print("  0. Voltar")

            escolha = self.ler_opcao(len(orientacoes), "Escolha uma orientação: ")
            if escolha == 0:
                if tentativas > 0:  # abriu orientações, mas não se resolveu
                    self.registrar("categoria", ultima.titulo, ultima.id, True,
                                   False, tentativas,
                                   round(time.time() - inicio, 1))
                return

            tentativas += 1
            ultima = orientacoes[escolha - 1]
            ultima.exibir()

            if self.perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                self.registrar("categoria", ultima.titulo, ultima.id, True, True,
                               tentativas, round(time.time() - inicio, 1))
                return

    # ------------------------------------------------------------------
    # Histórico
    # ------------------------------------------------------------------
    def carregar_historico(self):
        """Lê o historico.json. Arquivo ausente ou corrompido não trava o programa."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            print("Aviso: não foi possível ler o histórico anterior. Será criado um novo.")
            return []

        if not isinstance(dados, list):
            print("Aviso: o histórico anterior está em formato inesperado. Será criado um novo.")
            return []
        return [item for item in dados if isinstance(item, dict)]

    def salvar_historico(self):
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar o histórico.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):
        """Guarda um atendimento no histórico (lista) e no historico.json."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,                  # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,    # None se nada foi encontrado
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "facilidade": None,                # preenchida ao sair
        }
        self.historico.append(atendimento)
        self.salvar_historico()

    # ------------------------------------------------------------------
    # Indicadores e CSV
    # ------------------------------------------------------------------
    @staticmethod
    def media(valores):
        numeros = [v for v in valores
                   if isinstance(v, (int, float)) and not isinstance(v, bool)]
        return round(sum(numeros) / len(numeros), 1) if numeros else None

    def indicadores(self):
        """Calcula e exibe os indicadores. Devolve um dicionário com os valores."""
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
            return None

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]

        # uma nota de facilidade por sessão (a mesma nota vale para a sessão toda)
        notas_por_sessao = {}
        for a in self.historico:
            if a.get("facilidade") is not None:
                notas_por_sessao[a.get("sessao")] = a["facilidade"]

        sem_solucao = []
        for a in self.historico:
            pergunta = a.get("pergunta")
            if not a.get("ajudou") and pergunta and pergunta not in sem_solucao:
                sem_solucao.append(pergunta)

        dados = {
            "atendimentos": total,
            "encontrada_pct": round(len(encontrados) / total * 100, 1),
            "acerto_pct": round(len(ajudaram) / total * 100, 1),
            "tempo_medio": self.media([a.get("tempo_segundos") for a in encontrados]),
            "tentativas_media": self.media([a.get("tentativas") for a in self.historico]),
            "facilidade": self.media(list(notas_por_sessao.values())),
            "sem_solucao": sem_solucao,
        }

        print(f"\n===== Indicadores ({total} atendimentos) =====")
        print(f"Resposta encontrada: {dados['encontrada_pct']}%")
        print(f"Taxa de acerto (ajudou): {dados['acerto_pct']}%")
        tempo = dados["tempo_medio"]
        print("Tempo médio para encontrar: " + (f"{tempo} s" if tempo is not None else "sem dados"))
        tent = dados["tentativas_media"]
        print("Tentativas por atendimento: " + (str(tent) if tent is not None else "sem dados"))
        fac = dados["facilidade"]
        print("Facilidade de uso (1 a 5): " + (str(fac) if fac is not None else "sem notas ainda"))
        print("Dúvidas sem solução:")
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  (nenhuma)")
        return dados

    def exportar_csv(self):
        """Exporta o histórico para data/atendimentos.csv com csv.DictWriter."""
        if not self.historico:
            print("\nNão há atendimentos para exportar.")
            return
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            # utf-8-sig: o Excel abre os acentos corretamente
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore", restval="")
                escritor.writeheader()
                escritor.writerows(self.historico)
            print(f"\nArquivo exportado: {self.caminho_csv} ({len(self.historico)} atendimentos)")
        except OSError:
            print("Aviso: não foi possível exportar o CSV.")

    # ------------------------------------------------------------------
    # Encerramento
    # ------------------------------------------------------------------
    def encerrar(self):
        """Ao sair, pede a nota de facilidade (1 a 5) se houve atendimentos."""
        da_sessao = [a for a in self.historico if a.get("sessao") == self.sessao]
        if not da_sessao:
            return

        print("\nAntes de sair, uma pergunta rápida.")
        while True:
            resposta = self.entrada("De 1 a 5, qual a facilidade de usar este assistente? ")
            if resposta is None:
                return
            if resposta in ("1", "2", "3", "4", "5"):
                nota = int(resposta)
                break
            print("Nota inválida: digite um número de 1 a 5.")

        for atendimento in da_sessao:
            atendimento["facilidade"] = nota
        self.salvar_historico()