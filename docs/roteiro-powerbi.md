# Montagem no Power BI Desktop

1. Em um banco SQL Server dedicado, execute `sql/01_carga.sql` e depois `sql/02_visoes.sql` no SSMS ou Azure Data Studio, com suporte a `GO`. A carga substitui `dbo.chamados`; não use banco com dados importantes.
2. Em **Obter dados > SQL Server**, informe servidor e banco local, sem salvar credenciais no repositório. Selecione as seis visões, modo Importar, e abra **Transformar dados**.
3. No Power Query, confira `data` e `data_abertura` como data; timestamps como data/hora UTC; `id` e `prazo_horas` como inteiros; `horas_resolucao` como decimal. Preserve nulos. Carregue as tabelas.
4. No modelo, marque `dim_data` como tabela de datas usando `data`. Crie relações 1:* de `dim_data[data]` para `fato_chamados[data_abertura]` e de cada dimensão filial, categoria, prioridade e atendente para a coluna correspondente da fato. Use filtro unidirecional da dimensão para a fato.
5. Crie uma tabela desconectada `Referencia = SELECTCOLUMNS({1}, "InstanteUTC", DATE(2025,1,1))` e as medidas de [medidas.md](medidas.md). Confira a referência antes de atualizar os números.
6. Crie páginas: **Visão geral** (cartões, tendência mensal, categoria); **Prazo e pendências** (SLA, tempo, prioridade e vencidos); **Filiais** (ranking e vencidos); **Atendentes** (volume, com aviso de origem não informada); **Detalhe** (tabela por ID). Adicione segmentações de data, filial, categoria e prioridade e verifique interações de filtro.
7. Em Detalhe, coloque `fato_chamados[id]` no campo de drill-through. Inclua botão de voltar. Na página Filiais, permita navegação até um chamado por uma tabela de IDs. Crie uma página de dica de ferramenta com cartões de SLA e tempo; habilite-a nas propriedades e associe-a aos gráficos.
8. Compare os cinco indicadores com [conferencia.md](conferencia.md), inclusive sem filtros e com filtros de filial/data. Salve o `.pbix` somente após validar. Gere GIF ou vídeo e PDF depois da revisão visual.

Este repositório não contém `.pbix`; execução no SQL Server, atualização e conferência visual dependem do computador com Power BI Desktop.
