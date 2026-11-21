# Modelo de Dados - Diagrama Estrela

## Diagrama MERME

```mermaid
erDiagram
    dim_data {
        date data PK "Chave de data"
    }
    
    dim_filial {
        nvarchar(100) filial PK "Nome da filial"
    }
    
    dim_categoria {
        nvarchar(100) categoria PK "Categoria do chamado"
    }
    
    dim_prioridade {
        nvarchar(20) prioridade PK "Nível de prioridade"
    }
    
    dim_atendente {
        nvarchar(100) atendente PK "Identificador do atendente"
    }
    
    fato_chamados {
        int id PK "ID único do chamado"
        nvarchar(100) filial FK "Relaciona com dim_filial"
        nvarchar(100) categoria FK "Relaciona com dim_categoria"
        nvarchar(20) prioridade FK "Relaciona com dim_prioridade"
        nvarchar(100) atendente FK "Relaciona com dim_atendente"
        date data_abertura FK "Relaciona com dim_data"
        datetime2 aberto_em "Timestamp de abertura (UTC)"
        datetime2 resolvido_em "Timestamp de resolução (UTC)"
        int prazo_horas "Prazo em horas"
        nvarchar(20) status "Status: aberto ou resolvido"
        bit reaberto "Flag de reabertura (sempre NULL na origem)"
        decimal horas_resolucao "Horas de resolução (calculado)"
        bit resolvido_no_prazo "1 se resolveu dentro do SLA"
    }
    
    dim_filial ||--o{ fato_chamados : "filial"
    dim_categoria ||--o{ fato_chamados : "categoria"
    dim_prioridade ||--o{ fato_chamados : "prioridade"
    dim_atendente ||--o{ fato_chamados : "atendente"
    dim_data ||--o{ fato_chamados : "data_abertura"
```

## Estrutura Estrela

O modelo segue a estrutura de **esquema estrela** (star schema), otimizado para consultas analíticas:

- **Fato central**: `fato_chamados` - contém as métricas e chaves estrangeiras
- **Dimensões**: 5 tabelas de dimensão fornecem atributos descritivos

### Detalhamento das Dimensões

| Dimensão | Atributos | Descrição |
|---|---|---|
| `dim_data` | `data` | Calendário contínuo (100.000 dias), cobertura completa dos anos presentes nos dados |
| `dim_filial` | `filial` | 50 filiais fictícias (`Filial 01` a `Filial 50`) |
| `dim_categoria` | `categoria` | 5 categorias: Impressora, ERP, Rede, Acesso, Hardware |
| `dim_prioridade` | `prioridade` | 4 níveis: baixa, média, alta, crítica |
| `dim_atendente` | `atendente` | Valor fixo "Não informado" (a origem não possui registro de atendente) |

### Métricas do Fato

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | int | Identificador único do chamado |
| `aberto_em` | datetime2 | Timestamp da abertura (UTC) |
| `resolvido_em` | datetime2 | Timestamp da resolução (pode ser NULL) |
| `prazo_horas` | int | Prazo máximo em horas para resolução |
| `status` | nvarchar | Valores: 'aberto' ou 'resolvido' |
| `horas_resolucao` | decimal | Duração em horas (calculada via SQL) |
| `resolvido_no_prazo` | bit | 1 se resolvido dentro do SLA, 0 caso contrário |

## Regras de Negócio no Modelo

1. **SLA (Service Level Agreement)**: Um chamado é considerado dentro do prazo se:
   - Estiver resolvido e `resolvido_em <= aberto_em + prazo_horas`

2. **Chamados vencidos**: No cálculo do SLA, consideram-se:
   - Chamados resolvidos (divididos entre dentro e fora do prazo)
   - Chamados abertos que ultrapassaram o prazo em relação à referência UTC

3. **Abertos fora do prazo**: Calculados como abertos cujo prazo já expirou na referência UTC fixa

## Relacionamentos

Todos os relacionamentos são **1:muitos** (1:N) da dimensão para o fato, com **filtro unidirecional** da dimensão para o fato, permitindo:
- Filtragem eficiente pelas dimensões
- Navegação livre das dimensões ao fato
- Navegação restrita do fato às dimensões

## Observações

- A origem do projeto 4 (`painel-chamados`) não possui informação de atendente nem reabertura
- Todos os timestamps estão em UTC
- O campo `reaberto` é sempre NULL, não aplicável à esta origem