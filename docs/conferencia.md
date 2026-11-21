# Conferência

Após executar ambos os scripts, use a referência UTC fixa `2025-01-01 00:00:00`, sem filtros no Power BI. Os valores abaixo foram calculados independentemente a partir do JSON; devem ser confirmados no SQL Server e no relatório. O SLA considera todos os resolvidos e abertos vencidos, excluindo abertos ainda no prazo.

| Indicador | Esperado | Consulta SQL |
|---|---:|---|
| Total | 1500 | `SELECT COUNT(*) FROM dbo.fato_chamados;` |
| Resolvidos | 1383 | `SELECT COUNT(*) FROM dbo.fato_chamados WHERE status = N'resolvido';` |
| Pendentes | 117 | `SELECT COUNT(*) FROM dbo.fato_chamados WHERE status = N'aberto';` |
| Tempo médio (h) | 40,720854 | `SELECT AVG(horas_resolucao) FROM dbo.fato_chamados;` |
| SLA | 56,066667% | consulta abaixo |

```sql
DECLARE @referencia datetime2(3) = '2025-01-01T00:00:00';
SELECT 100.0 * SUM(CASE WHEN resolvido_no_prazo = 1 THEN 1 ELSE 0 END) /
       NULLIF(SUM(CASE WHEN status = N'resolvido' OR
           (status = N'aberto' AND DATEADD(hour, prazo_horas, aberto_em) < @referencia)
           THEN 1 ELSE 0 END), 0) AS sla_percentual
FROM dbo.fato_chamados;
```

A origem tem 841 resolvidos no prazo e 117 abertos vencidos nessa referência. Compare sem arredondar os valores intermediários; arredonde apenas a exibição.
