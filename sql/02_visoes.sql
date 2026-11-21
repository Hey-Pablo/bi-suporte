-- Execute após 01_carga.sql. As datas estão em UTC.
CREATE OR ALTER VIEW dbo.dim_filial AS SELECT DISTINCT filial FROM dbo.chamados;
GO
CREATE OR ALTER VIEW dbo.dim_categoria AS SELECT DISTINCT categoria FROM dbo.chamados;
GO
CREATE OR ALTER VIEW dbo.dim_prioridade AS SELECT DISTINCT prioridade FROM dbo.chamados;
GO
CREATE OR ALTER VIEW dbo.dim_atendente AS SELECT CAST(N'Não informado' AS nvarchar(100)) AS atendente;
GO
-- Calendário contínuo, anos completos que abrangem as aberturas.
CREATE OR ALTER VIEW dbo.dim_data AS
WITH n AS (SELECT TOP (100000) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS dia FROM sys.all_objects a CROSS JOIN sys.all_objects b),
limites AS (SELECT DATEFROMPARTS(YEAR(MIN(aberto_em)),1,1) inicio, DATEFROMPARTS(YEAR(MAX(aberto_em)),12,31) fim FROM dbo.chamados)
SELECT DATEADD(day, CONVERT(int,n.dia), l.inicio) AS data
FROM n CROSS JOIN limites l WHERE n.dia <= DATEDIFF(day,l.inicio,l.fim);
GO
CREATE OR ALTER VIEW dbo.fato_chamados AS
SELECT id, filial, categoria, prioridade, CAST(N'Não informado' AS nvarchar(100)) atendente,
 CAST(aberto_em AS date) data_abertura, aberto_em, resolvido_em, prazo_horas, status,
 CAST(NULL AS bit) reaberto,
 CASE WHEN status = N'resolvido' THEN DATEDIFF_BIG(millisecond, aberto_em, resolvido_em) / 3600000.0 END horas_resolucao,
 CASE WHEN status = N'resolvido' AND resolvido_em <= DATEADD(hour,prazo_horas,aberto_em) THEN 1 ELSE 0 END resolvido_no_prazo
FROM dbo.chamados;
GO
