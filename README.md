# BI de Suporte

> **Status: em desenvolvimento.** O código entra aos poucos; abaixo está o planejamento do projeto.

## O que é

Relatório em Power BI sobre a operação de suporte fictícia, com modelo estrela no SQL Server, medidas DAX documentadas e cinco páginas: visão geral, prazo e pendências, filiais, atendentes e detalhe do chamado.

## O que prova

Power BI e SQL Server juntos: modelagem dimensional, Power Query, DAX e validação dos números.

## Stack

SQL Server, Power Query, Power BI Desktop e DAX.

## Estrutura

```
bi-suporte/
├─ sql/
│  ├─ 01_carga.sql          # dados do projeto 4
│  └─ 02_visoes.sql         # fato_chamados e dimensões
├─ powerbi/                 # arquivo do relatório (.pbip ou .pbix)
├─ docs/
│  ├─ perguntas.md          # as 10 perguntas que o relatório responde
│  ├─ modelo.png
│  ├─ medidas.md            # cada medida DAX com explicação
│  └─ conferencia.md        # número do painel ao lado da consulta SQL
└─ README.md
```

## Plano

1. Escreva 10 perguntas de negócio, como "quais filiais concentram chamados fora do prazo?".
2. Carregue os chamados no SQL Server e crie as visões: fato e dimensões de data, filial, categoria, prioridade e atendente.
3. Power Query: tipos, tabela calendário e colunas de apoio.
4. Modelo estrela com relacionamentos de um para muitos.
5. Medidas: total, resolvidos, pendentes, tempo médio de resolução, percentual no prazo, reabertos e variação contra o mês anterior.
6. Páginas com segmentações, dica de ferramenta personalizada e detalhamento (drill-through).
7. Conferência: 5 números do relatório batidos com consulta SQL.
8. Publicação: arquivo no repositório, GIF de navegação e PDF exportado.

## Como deve funcionar

- Abrir o arquivo e atualizar carrega os dados do SQL Server.
- Cada uma das 10 perguntas tem resposta visível em uma página.
- Clicar em uma filial filtra as demais visualizações.
- A tabela de conferência mostra painel e SQL com o mesmo valor.

## Prazo

1 a 2 semanas.

## Autor

Pablo Dilio · [Portfólio](https://hey-pablo.github.io/pablo-dilio-portfolio/) · [LinkedIn](https://www.linkedin.com/in/pablo-dilio-4063991b2)
