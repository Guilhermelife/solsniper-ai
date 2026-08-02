CONTEXTO DO PROJETO — SOLSNIPER AI

1\. Visão geral



Estou desenvolvendo um sistema chamado SolSniper AI.



O objetivo final é criar um sniper/trading bot para meme coins da rede Solana, capaz de:



Monitorar novos tokens automaticamente.

Analisar oportunidades usando dados on-chain e métricas de mercado.

Classificar oportunidades através de um sistema de pontuação (AI Score).

Simular operações inicialmente (Paper Trading).

Futuramente executar compras e vendas reais através de integração com carteira Solana.



O objetivo não é criar apenas um scanner, mas evoluir para um agente autônomo de trading.



2\. Estratégia desejada



A ideia inicial do produto:



Capital inicial:



$50



O bot deve:



Encontrar uma meme coin promissora.

Avaliar risco/oportunidade.

Entrar na operação.

Monitorar preço.

Sair quando atingir objetivo.

Reinvestir o capital.

Repetir continuamente.



Modelo:



Capital inicial

&#x20;      |

&#x20;      ↓

Scanner encontra token

&#x20;      |

&#x20;      ↓

AI Score

&#x20;      |

&#x20;      ↓

Compra simulada

&#x20;      |

&#x20;      ↓

Take Profit / Stop Loss

&#x20;      |

&#x20;      ↓

Venda

&#x20;      |

&#x20;      ↓

Novo ciclo

3\. Estratégia de trading



Ainda estamos definindo o modelo final.



Possíveis estratégias:



Estratégia sniper early entry



Buscar:



Market cap baixo:

$5k - $100k

Tokens novos.

Alto potencial de multiplicação.



Objetivo:



10x

50x

100x



Risco:



Alto.



Estratégia de scalping



Buscar:



Tokens já com liquidez.

Volume aumentando.

Pressão compradora.



Objetivo:



+10%

+20%

+30%



Várias operações pequenas.



Estratégia híbrida desejada



Misturar:



Pequenas operações frequentes.

Algumas apostas assimétricas em tokens novos.

4\. Stack utilizada



Backend:



Python

FastAPI

SQLAlchemy

PostgreSQL

Alembic



Ambiente:



Windows

Docker

Virtualenv

5\. Estrutura atual do projeto

solsniper-ai



├── apps



│

├── api

│   ├── main.py

│   └── src

│       ├── routes

│       ├── schemas

│       └── health.py

│



├── common

│   ├── database.py

│   ├── config.py

│   ├── clients

│   │    └── dexscreener.py

│   │

│   └── models

│        ├── token.py

│        ├── signal.py

│        └── \_\_init\_\_.py

│



├── worker

│   ├── main.py

│   ├── scout.py

│   └── analyzer.py

│

└── migrations

6\. O que já está funcionando

Banco PostgreSQL



Banco:



solsniper\_db



Tabelas atuais:



tokens

signals

alembic\_version

API FastAPI funcionando



Executada com:



uvicorn apps.api.main:app --reload



Swagger:



http://127.0.0.1:8000/docs



Endpoints existentes:



GET /tokens/



POST /tokens/

7\. Modelo Token criado



Tabela:



tokens



Campos:



id

address

symbol

name

liquidity

volume\_24h

risk\_score

created\_at

8\. Modelo Signal criado



Tabela:



signals



Campos:



id

token\_address

symbol

ai\_score

decision

created\_at

9\. Integração DexScreener



Já existe:



apps/common/clients/dexscreener.py



Conseguimos buscar dados reais.



Exemplo retornado:



{

"name":"Bonk",

"symbol":"BONK",

"liquidity":113980,

"volume\_24h":171000

}



Também conseguimos buscar:



Market Cap

FDV

Liquidez

Volume

Compras

Vendas

Alteração de preço

Idade do token

DEX

10\. Scanner atual



Arquivo:



apps/worker/scout.py



Responsável por:



Buscar pares Solana.

Filtrar tokens.

Extrair métricas.



Dados coletados:



{

address,

symbol,

name,

market\_cap,

liquidity,

volume\_24h,

buys,

sells,

price\_change,

age\_minutes,

dex

}

11\. Analyzer atual



Arquivo:



apps/worker/analyzer.py



Sistema de pontuação:



Exemplo:



Liquidez:



>=100k +25 pontos

>=30k +15 pontos



Volume:



>=200k +25

>=50k +15



Compradores:



buys > sells +25



Preço:



+50% +25



Resultado:



80+

BUY\_SIGNAL



60+

WATCH



abaixo

IGNORE

12\. Problemas atuais conhecidos



O scanner ainda precisa melhorar.



Problemas:



DexScreener retorna muitos tokens grandes como SOL/PUMP.

Falta filtro de meme coins pequenas.

Falta filtro por idade.

Falta análise de segurança.

Falta histórico.

Falta gerenciamento de posição.

13\. Próximas etapas planejadas

Fase 1 — Melhorar Scanner



Adicionar filtros:



Market cap mínimo/máximo.



Exemplo:



5k - 5 milhões

Idade:

<24 horas

Liquidez mínima:

>10k

Volume crescente.

Fase 2 — Paper Trading Engine



Criar simulação de carteira.



Novo modelo:



positions



Campos:



id



token\_address



symbol



entry\_price



amount\_usd



quantity



status



target\_profit



stop\_loss



exit\_price



profit\_loss



created\_at



closed\_at



Objetivo:



Simular:



Compra virtual



Monitoramento



Venda virtual

Fase 3 — Backtesting



Criar histórico:



Medir:



Taxa de acerto.

ROI.

Drawdown.

Melhor estratégia.

Fase 4 — Risk Engine



Adicionar:



Rug pull detection.

Liquidez.

Holder concentration.

Mint authority.

Freeze authority.

Segurança do contrato.

Fase 5 — Execução real



Somente depois dos testes:



Integração:



Solana RPC.

Jupiter Swap.

Wallet.



Executar:



BUY



SELL



Objetivo final do projeto



Criar um agente:



SolSniper AI



24/7



Monitora Solana



Encontra oportunidades



Analisa



Opera



Gerencia risco



Evolui o capital

Próxima tarefa imediata



Implementar:



Paper Trading Engine



Primeiro criar:



apps/common/models/position.py



Depois:



migration:



positions table



Depois criar:



apps/worker/trader.py



Responsável por:



Abrir posição simulada.

Controlar capital.

Fechar posição.

Registrar lucro/prejuízo.



\---



Esse é o estado atual do projeto e o roadmap.



\---



Eu recomendo enviar exatamente esse contexto para o Antigravity junto com o repositório. Assim ele entende que a próxima tarefa \*\*não é simplesmente criar uma tabela\*\*, mas continuar a construção de um bot de trading autônomo.

