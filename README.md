# BI de Suporte

> **Status: em desenvolvimento.** Carga, visões e roteiro disponíveis; relatório Power BI ainda não foi montado.

## Problema e solução

O projeto reúne chamados fictícios do [painel de chamados](https://github.com/Hey-Pablo/painel-chamados) em um modelo estrela para analisar volume, prazos e filiais. SQL Server fornece carga e visões; Power BI Desktop oferece modelo, DAX e visualizações. Nenhum dado de cliente é usado.

## Como executar

1. Em SQL Server, crie um banco de demonstração dedicado e execute `sql/01_carga.sql`, seguido de `sql/02_visoes.sql`, usando uma ferramenta que entenda `GO`. A carga substitui a tabela `dbo.chamados` desse banco.
2. Siga [o roteiro de Power BI](docs/roteiro-powerbi.md) para montar o relatório e [a conferência](docs/conferencia.md) para comparar os números.
3. Teste localmente a integridade da carga com `python3 -m unittest discover -s tests`.

## Estrutura e decisões

- `sql/chamados.json`: cópia dos 1.500 registros fictícios do projeto 4; `01_carga.sql` contém os mesmos registros para execução sem importação externa.
- `sql/02_visoes.sql`: fato e dimensões, com data de abertura como chave temporal.
- `docs/perguntas.md`, `medidas.md`, `conferencia.md` e `roteiro-powerbi.md`: perguntas, fórmulas, comparação e montagem.
- `tests/`: verificações locais da carga e das regras sobre os dados.

O SLA segue o painel de origem: resolvidos no prazo divididos por resolvidos mais abertos vencidos. Os horários são UTC. Atendente e reabertura não existem na origem e são representados como não informados, não como eventos fictícios.

## Limitações e próximos passos

SQL Server e Power BI Desktop não foram executados nesta VPS. É preciso executar os scripts, criar e validar o relatório, publicar GIF ou vídeo e exportar PDF. A carga é uma fotografia estática, não uma integração automática. A IA auxiliou na implementação e documentação; a revisão técnica e a validação no ambiente de destino continuam necessárias.

## Autor

Pablo Dilio · [Portfólio](https://hey-pablo.github.io/pablo-dilio-portfolio/) · [LinkedIn](https://www.linkedin.com/in/pablo-dilio-4063991b2)
