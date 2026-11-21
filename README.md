# BI de Suporte

> **Demonstração:** em breve

> **Link da demonstração no README:** em breve (após o Pablo montar o relatório e exportar GIF/PDF)

## Problema e Solução

O projeto transforma dados fictícios de chamados de suporte em um relatório de Business Intelligence pronto para análise. A partir de 1.500 chamados de 50 filiais, o modelo estrela no SQL Server expõe indicadores operacionais como SLA, tempo médio de resolução e volume por categoria ou filial. Power BI Desktop consome as visões e entrega um relatório com cinco páginas: visão geral, prazos e pendências, filiais, atendentes e detalhe por chamado.

**Problema:** Equipes de suporte precisam de visibilidade em tempo real sobre volume de chamados, cumprimento de prazos e gargalos por filial ou categoria. Sem BI, essa análise exige consultas SQL dissertáveis.

**Solução:** Modelo dimensional com esquema estrela, carga automatizada e relatório Power BI com medidas DAX documentadas. Todo o processamento está no SQL Server; nenhum dado de cliente real é utilizado.

## Como Executar

### Pré-requisitos

- SQL Server 2019+ (Developer ou Express) - testado em Docker
- Power BI Desktop (última versão)
- 500 MB de espaço livre

### Passo 1: Preparar o Banco SQL Server

```bash
# Com SQL Server em Docker (opcional)
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Mudar@123" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest
```

No SQL Server (via SSMS, Azure Data Studio ou sqlcmd):

```sql
-- Criar banco de demonstração dedicado
CREATE DATABASE BiSuporteDemo;
GO
USE BiSuporteDemo;
GO

-- Executar scripts de carga
:r sql/01_carga.sql
GO
:r sql/02_visoes.sql
GO

-- Verificar carga
SELECT COUNT(*) AS total_chamados FROM fato_chamados;
```

### Passo 2: Construir o Modelo no Power BI Desktop

Siga o [roteiro detalhado em docs/roteiro-powerbi.md](docs/roteiro-powerbi.md):

1. Conectar ao SQL Server → selecionar as 6 visões
2. Configurar tabela de datas → marcar como data
3. Criar relacionamentos 1:N (dimensões → fato)
4. Implementar medidas DAX conforme [docs/medidas.md](docs/medidas.md)

### Passo 3: Validar os Resultados

Compare os cinco indicadores principais com [docs/conferencia.md](docs/conferencia.md). Valores esperados:

| Indicador | Valor |
|---|---|
| Total chamados | 1.500 |
| Resolvidos | 1.383 |
| Pendentes | 117 |
| Tempo médio (h) | 40,72 |
| SLA (%) | 56,07% |

### Executar Testes Locais

```bash
# Testes de integridade da carga
python3 -m unittest discover -s tests
```

## Estrutura

```
bi-suporte/
├─ sql/
│  ├─ 01_carga.sql          # Tabela chamados e 1.500 registros fictícios
│  └─ 02_visoes.sql         # Modelo estrela: fato e 5 dimensões
├─ docs/
│  ├─ perguntas.md          # 10 perguntas de negócio atendidas
│  ├─ modelo.md             # Diagrama MERME e documentação do modelo
│  ├─ medidas.md            # Fórmulas DAX e exemplos
│  ├─ conferencia.md        # Valores esperados x consultas SQL
│  └─ roteiro-powerbi.md    # Guia de montagem no Power BI Desktop
├─ tests/
│  └─ test_integracao.py    # Verificações de integridade
├─ powerbi/                  # (a ser criado no Windows)
│  ├─ bi-suporte.pbix       # Arquivo do relatório
│  └─ (esquemas JSON exportados)
└─ README.md                 # Este arquivo
```

## Decisões Técnicas

### Modelo Estrela

Escolhi o **esquema estrela** por ser a estrutura mais eficiente para consultas analíticas e para a própria experiência do Power BI. A separação entre fato e dimensões:

- Permite filtragem rápida (índices nas chaves)
- Facilita a adição de novas dimensões sem impactar métricas
- Compatível com drill-through nativo do Power BI

### Tabela de Dados

A tabela `dim_data` contém datas contínuas para permitir:
- Séries temporais completas (sem buracos)
- Análise de tendências mensais
- Cálculo de variação contra o mês anterior

### Referência UTC Fixa

Para a conferência dos números, fixamos uma referência UTC (`2025-01-01 00:00:00`). Isso garante:
- Reprodutibilidade dos testes
- Comparação justa entre Power BI e SQL
- Estabilidade mesmo que novos dados forem adicionados

### Atendente como Dimensão Fixa

A origem (`painel-chamados`) não possui informação de atendente. Criei `dim_atendente` com valor estático "Não informado" para manter a consistência do modelo e permitir futuras evoluções.

## Limitações

- **Não há dados reais**: todos são fictícios, gerados com semente fixa
- **Atendente não informado**: a origem não registra quem atendeu cada chamado
- **Reabertura não existe**: campo `reaberto` é sempre NULL
- **Power BI Desktop requer Windows**: a construção e validação do `.pbix` precisa ser feita no PC do Pablo

> **Status:** .pbix pendente - SQL e visões prontos, relatório a ser montado no Power BI Desktop
- **SQL Server não está na VPS**: instalação manual ou Docker necessária

## Próximos Passos

1. **Instalar SQL Server** - Pablo testa no Windows com SSMS
2. **Criar o relatório no Power BI Desktop** - seguir roteiro-powerbi.md
3. **Exportar PDF** - relatório completo com todos os filtros
4. **Gravar GIF ou vídeo** - navegação pelas 5 páginas (máximo 2 minutos)
5. **Colocar .pbix no repositório** - arquivo do relatório
6. **Atualizar README** - inserir link da demonstração quando publicado

## Checklist para o Pablo (Windows)

### SQL Server

- [ ] Instalar SQL Server Developer/Express ou usar Docker
- [ ] Executar `sql/01_carga.sql` (cria tabela e insere 1.500 registros)
- [ ] Executar `sql/02_visoes.sql` (cria modelo estrela)
- [ ] Verificar: `SELECT COUNT(*) FROM fato_chamados` → resultado 1500

### Power BI Desktop

- [ ] Instalar Power BI Desktop (gratuito)
- [ ] Conectar ao SQL Server → importar as 6 visões
- [ ] Configurar `dim_data` como tabela de datas
- [ ] Criar relacionamentos (1:N dimensões → fato)
- [ ] Implementar as 7 medidas DAX em [medidas.md](docs/medidas.md)
- [ ] Criar página **Visão geral** (cartões + gráfico)
- [ ] Criar página **Prazo e pendências** (SLA, tempo médio)
- [ ] Criar página **Filiais** (top 10, abertos vencidos)
- [ ] Criar página **Atendentes** (volume, avisos)
- [ ] Criar página **Detalhe** (tabela + drill-through)
- [ ] Adicionar segmentações de data, filial, categoria, prioridade
- [ ] Habilitar interações de filtro entre páginas
- [ ] Criar página de dica de ferramenta (opcional)

### Conferência

- [ ] Comparar valores no Power BI com [conferencia.md](docs/conferencia.md)
- [ ] Sem filtros: valores exatamente como na tabela
- [ ] Com filtro de data: todos os indicadores atualizam
- [ ] Com filtro de filial: números batem com query SQL correspondente

### Publicação

- [ ] Salvar arquivo `bi-suporte.pbix`
- [ ] Exportar **PDF** do relatório completo
- [ ] Gravar **GIF** ou **vídeo** (máximo 2 minutos)
- [ ] Subir `.pbix` e PDF/GIF para o repositório
- [ ] Atualizar README com link da demonstração

### Testes no PC

```powershell
# No diretório do projeto
python -m unittest discover -s tests
# Resultado esperado: Ok (22 testes)
```

## Estrutura de Dados

### Tabela base (do projeto 4)

| Campo | Tipo | Descrição |
|---|---|---|
| id | int | ID único (1-1500) |
| filial | nvarchar(100) | Nome da filial (50 filiais distintas) |
| categoria | nvarchar(100) | Impressora, ERP, Rede, Acesso, Hardware, NF-e |
| prioridade | nvarchar(20) | baixa, média, alta, crítica |
| aberto_em | datetime2 | Timestamp da abertura (UTC) |
| resolvido_em | datetime2 | Timestamp da resolução (NULL se aberto) |
| prazo_horas | int | Prazo máximo em horas |
| status | nvarchar(20) | 'aberto' ou 'resolvido' |

## Referências

- Dados origem: [painel-chamados](../painel-chamados) - 1.500 chamados fictícios

## Autor

Pablo Dilio · [Portfólio](https://hey-pablo.github.io/pablo-dilio-portfolio/) · [LinkedIn](https://www.linkedin.com/in/pablo-dilio-4063991b2)