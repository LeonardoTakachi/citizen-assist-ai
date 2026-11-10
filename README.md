# Citizen Assist AI

Assistente de terminal, em Python, que orienta consumidores quando uma compra ou um serviço dá errado.
Projeto da Global Solution de Pensamento Computacional e Automação com Python (FIAP).

> **Aviso:** este assistente **não é um canal oficial** e não substitui orientação jurídica. Ele indica o caminho e a fonte oficial de cada orientação.

## 1. Integrantes

| Nome | RM |
|---|---|
| Leonardo Takachi | RM 569066 |
| Giovane Salazar | RM 570396 |

## 2. Público e problema

**Público:** consumidores que não sabem o que fazer quando uma compra ou um serviço dá errado.

**Problema:** quando um produto chega com defeito, um Pix cai em golpe ou aparece uma cobrança indevida, muita gente não sabe quais são seus direitos, quais documentos juntar nem onde reclamar. A informação existe em sites oficiais, mas está espalhada e escrita em linguagem difícil.

O assistente reúne orientações curtas em três categorias:

- **Compras:** desistência, defeito, atraso na entrega e garantia.
- **Bancos e Pix:** golpe no Pix, Pix recebido por engano, empréstimos no seu nome e valores esquecidos em bancos.
- **Reclamações:** consumidor.gov.br, Procon, cobrança indevida e nome negativado.

## 3. ODS relacionados

- **ODS 12 – Consumo e Produção Responsáveis:** o assistente informa o consumidor sobre seus direitos, o que incentiva escolhas e relações de consumo mais conscientes.
- **ODS 16 – Paz, Justiça e Instituições Eficazes:** o assistente aproxima o cidadão dos canais oficiais (Procon, consumidor.gov.br, Banco Central), facilitando o acesso à justiça e às instituições.

## 4. Como executar

**Requisito:** Python 3. Não usa bibliotecas externas, só a biblioteca padrão (`json`, `csv`, `os`, `time` e `datetime`).

```bash
git clone https://github.com/LeonardoTakachi/citizen-assist-ai.git
cd citizen-assist-ai
python main.py
```

**Menu:**

| Opção | O que faz |
|---|---|
| 1. Fazer uma pergunta | Você digita a dúvida com suas palavras. O assistente mostra a melhor orientação, o nível de confiança e até 2 alternativas. |
| 2. Navegar por categorias | Lista as categorias e as orientações numeradas. O 0 volta em todas as telas. |
| 3. Ver indicadores | Mostra os indicadores calculados a partir do histórico de atendimentos. |
| 4. Exportar atendimentos para CSV | Gera `data/atendimentos.csv` com todos os atendimentos. |
| 0. Sair | Pede uma nota de facilidade de 1 a 5 (se houve atendimento na sessão) e encerra. |

**Arquivos:**

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Ponto de entrada e menu |
| `orientacao.py` | Classe `Orientacao` (uma orientação da base) |
| `base_conhecimento.py` | Classe `BaseConhecimento`, normalização e busca com pontuação |
| `assistente.py` | Classe `Assistente`: atendimento, histórico, indicadores e CSV |
| `data/base_conhecimento.json` | As 12 orientações |
| `data/historico.json` | Histórico dos atendimentos |

**Privacidade:** o assistente nunca pede nome, CPF, telefone ou e-mail. Uma pergunta com `@` ou com 8 ou mais dígitos é recusada e não é registrada no histórico.

Cada atendimento é salvo em `data/historico.json` com estes campos: `data`, `sessao`, `origem` (pergunta ou categoria), `pergunta`, `id_orientacao`, `encontrou`, `ajudou`, `tentativas`, `tempo_segundos` (medido com `time.time()` e arredondado com `round(..., 1)`) e `facilidade`.

## 5. Regra de pontuação

Para cada orientação da base, o assistente soma pontos:

- **+3** para cada palavra-chave da orientação que aparece na pergunta.
- **+1** para cada palavra da pergunta, com 4 letras ou mais, que aparece no título da orientação.

| Pontos | Resultado |
|---|---|
| 6 ou mais | Confiança **ALTA** |
| 3 a 5 | Confiança **MÉDIA** |
| Abaixo de 3 | "Não encontrei", com sugestão das categorias |

**Exemplo:** "Meu produto chegou com defeito" na orientação 2 ("Produto chegou com defeito").

| Regra | Quem pontua | Pontos |
|---|---|---|
| Palavra-chave | "defeito" | +3 |
| Palavra-chave | "com defeito" | +3 |
| Palavra no título (4+ letras) | "produto" | +1 |
| Palavra no título (4+ letras) | "chegou" | +1 |
| Palavra no título (4+ letras) | "defeito" | +1 |
| **Total** | | **9 pontos (ALTA)** |

"Meu" e "com" têm menos de 4 letras, por isso não contam no título.

**Normalização:** antes de comparar, a pergunta, as palavras-chave e o título passam pela função `normalizar()`, que:

1. coloca tudo em minúsculas;
2. remove os acentos (por exemplo, "não" vira "nao" e "cobrança" vira "cobranca");
3. troca a pontuação por espaço (`? ! . , ; : ( ) ' " - / …`);
4. junta os espaços repetidos e coloca um espaço no início e no fim.

Esse espaço nas pontas garante que só palavras inteiras sejam encontradas. Por exemplo, "med" não é encontrada dentro de "medo".

## 6. Integrações com outras disciplinas

Não houve integração com outras disciplinas.

## 7. Fontes consultadas

| Fonte | Orientações que usam |
|---|---|
| Código de Defesa do Consumidor (Lei 8.078/1990): https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm | 1, 2, 3, 4, 11, 12 |
| consumidor.gov.br: https://www.consumidor.gov.br | 5 |
| Procon-SP: https://www.procon.sp.gov.br | 6 |
| Banco Central (segurança no Pix): https://www.bcb.gov.br/estabilidadefinanceira/pix-seguranca | 7 |
| Banco Central (Pix): https://www.bcb.gov.br/estabilidadefinanceira/pix | 8 |
| Banco Central (Registrato): https://www.bcb.gov.br/meubc/registrato | 9 |
| Banco Central (Valores a Receber): https://valoresareceber.bcb.gov.br | 10 |

A data em que cada orientação foi conferida está no campo `verificado_em` do JSON.

## 8. Resultado do teste com usuários

Teste com 3 pessoas de fora da equipe, somando 17 atendimentos. Nenhum nome ou dado pessoal dos participantes foi registrado.

| Indicador | Valor |
|---|---|
| Resposta encontrada | 64,7 % |
| Ajudou (taxa de acerto) | 64,7 % |
| Tempo médio para encontrar | 16,3 s |
| Tentativas por atendimento | 1,1 |
| Facilidade média (1 a 5) | 3,7 |

### Dúvidas sem solução

- "Comprei um fone pela internet há 3 dias e quero devolver"
- "o que fazer se a geladeira nova parar de funcionar na primeira semana"
- "Fiz um pix para um falso venderdor, o que fazer?"
- "o" (o participante digitou a letra "o" em vez do número 0 para voltar)
- "paguei uma conta duas vezes, a empresa tem que devolver?"
- "recebi um pix de alguém que eu não conheço"

### Análise

Todas as orientações encontradas foram consideradas úteis pelos participantes. As dúvidas sem solução aconteceram porque as pessoas usaram expressões do dia a dia ("parar de funcionar", "duas vezes", "recebi um pix") que não estavam nas palavras-chave. Um participante também digitou a letra "o" no lugar do zero, e o programa registrou isso como pergunta.

### Melhorias feitas a partir do teste

1. **Novas palavras-chave** nas orientações 1, 2, 7, 8 e 11, usando as expressões dos próprios participantes. Com elas, as 5 dúvidas sem solução passaram a ser encontradas.
2. **Entradas muito curtas recusadas:** perguntas com menos de 3 caracteres agora mostram um aviso e não são registradas.

## 9. Limitações

- A busca só reconhece palavras exatas. Ela não entende sinônimos nem erros de digitação.
- A busca não reconhece erros de digitação: no teste, 'falso venderdor' não casou com 'falso vendedor'; a pergunta só foi encontrada por causa da expressão 'fiz um pix'.
- A base tem 12 orientações, então muitas dúvidas ainda ficam sem resposta.
- As orientações do Procon se referem a São Paulo (Procon-SP). Em outras cidades, o consumidor deve procurar o Procon local.
- O assistente não é canal oficial e não substitui orientação jurídica.

## 10. Vídeo técnico

Link: [PREENCHER]

## Decisões técnicas

- **Caminhos com `__file__`:** os arquivos em `data/` são encontrados a partir da pasta do próprio código (`os.path.dirname(os.path.abspath(__file__))`). Assim o programa funciona mesmo se for executado de outra pasta.
- **Ordenação com `key=lambda`:** `buscar()` ordena com `sort(key=lambda tupla: tupla[0], reverse=True)`. Ordenar as tuplas `(pontos, orientacao)` direto daria erro em empates, porque o Python tentaria comparar dois objetos `Orientacao`.
- **JSON ausente ou corrompido:** `carregar()` trata arquivo não encontrado, JSON inválido, arquivo fora de UTF-8 e campos faltando ou a mais. O programa avisa e continua rodando. O histórico corrompido também não trava o programa: um novo histórico é iniciado.
