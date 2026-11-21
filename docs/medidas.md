# Medidas DAX

As medidas usam `fato_chamados` e a data de abertura. As datas da origem são UTC. Defina uma tabela desconectada `Referencia` com uma única linha `2025-01-01 00:00:00` para reprodução. Para análise operacional, substitua-a por uma referência UTC atualizada. A referência não aplica um corte histórico: os dados devem estar completos até ela.

```DAX
Total = COUNTROWS(fato_chamados)
Resolvidos = CALCULATE([Total], fato_chamados[status] = "resolvido")
Pendentes = CALCULATE([Total], fato_chamados[status] = "aberto")
Tempo médio (h) = COALESCE(AVERAGE(fato_chamados[horas_resolucao]), 0)
No prazo = CALCULATE([Total], fato_chamados[resolvido_no_prazo] = 1)
Abertos vencidos =
VAR ReferenciaUTC = SELECTEDVALUE(Referencia[InstanteUTC])
RETURN IF(ISBLANK(ReferenciaUTC), BLANK(),
    CALCULATE([Total], FILTER(fato_chamados,
        fato_chamados[status] = "aberto" &&
        fato_chamados[aberto_em] + fato_chamados[prazo_horas] / 24 < ReferenciaUTC)))
SLA % = IF(ISBLANK([Abertos vencidos]), BLANK(), DIVIDE([No prazo], [Resolvidos] + [Abertos vencidos], 0))
Total mês anterior = CALCULATE([Total], DATEADD(dim_data[data], -1, MONTH))
Variação mensal % = DIVIDE([Total] - [Total mês anterior], [Total mês anterior])
```

Formate percentuais como porcentagem. O prazo exato conta dentro do prazo; abertos ainda no prazo ficam fora do denominador. Sem mês anterior, a variação fica em branco. A origem não registra reabertura nem atendente: `reaberto` é nulo e atendente é “Não informado”. Não há medida válida de reabertos; zero significaria falsamente que o evento foi medido.
