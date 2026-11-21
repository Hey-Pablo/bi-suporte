#!/usr/bin/env python3
"""
Gera o diagrama MERME do modelo estrela como imagem PNG.

Use: python tools/gerar_modelo.py

Requer: pip install matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Configuração do estilo
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Modelo Estrela - BI de Suporte\n(1.500 chamados, 5 dimensões)', fontsize=14, fontweight='bold', pad=20)

# Dimensões - posicionadas no topo
dim_width = 2.5
dim_height = 0.8
dim_y = 8.5

dimensoes = [
    ('dim_data', 'dim_data', dim_y, 1.0),
    ('dim_filial', 'dim_filial', dim_y, 3.5),
    ('dim_categoria', 'dim_categoria', dim_y, 6.0),
    ('dim_prioridade', 'dim_prioridade', dim_y, 8.5),
    ('dim_atendente', 'dim_atendente', dim_y, 11.0),
]

# Fato - posicionado centralizado
fato_x = 7.0
fato_y = 5.0
fato_width = 3.5
fato_height = 2.5

# Desenhar dimensões
for nome, titulo, y, x in dimensoes:
    rect = patches.Rectangle((x - dim_width/2, y - dim_height/2), dim_width, dim_height,
                               linewidth=2,edgecolor='#2E86AB', facecolor='#E8F4F8',
                               boxstyle='Round,pad=0.1')
    ax.add_patch(rect)
    ax.text(x, y, titulo, ha='center', va='center', fontsize=10, fontweight='bold')

# Desenhar fato central
fato_rect = patches.Rectangle((fato_x - fato_width/2, fato_y - fato_height/2), fato_width, fato_height,
                              linewidth=2, edgecolor='#1B4965', facecolor='#D4E3F7',
                              boxstyle='Round,pad=0.1')
ax.add_patch(fato_rect)
ax.text(fato_x, fato_y, 'fato_chamados', ha='center', va='center', fontsize=11, fontweight='bold')

# Campos do fato
campos_fato = [
    'id (PK)', 'filial (FK)', 'categoria (FK)', 'prioridade (FK)',
    'ativo (FK)', 'data_abertura (FK)', 'aberto_em', 'resolvido_em',
    'prazo_horas', 'status', 'horas_resolucao', 'resolvido_no_prazo'
]
for i, campo in enumerate(campos_fato):
    y_pos = fato_y - fato_height/2 + 0.3 + i * 0.25
    if y_pos > fato_y + fato_height/2 - 0.3:
        break
    ax.text(fato_x + fato_width/2 + 0.3, y_pos, f'• {campo}', fontsize=8, va='center')

# Desenhar linhas de conexão
conexoes = [
    ('dim_filial', 'filial'),
    ('dim_categoria', 'categoria'),
    ('dim_prioridade', 'prioridade'),
    ('dim_atendente', 'ativo'),
    ('dim_data', 'data_abertura'),
]

for dim, campo in conexoes:
    if dim == 'dim_filial':
        x1, y1 = 3.5, dim_y
    elif dim == 'dim_categoria':
        x1, y1 = 6.0, dim_y
    elif dim == 'dim_prioridade':
        x1, y1 = 8.5, dim_y
    elif dim == 'dim_atendente':
        x1, y1 = 11.0, dim_y
    else:  # dim_data
        x1, y1 = 1.0, dim_y

    x2 = fato_x + fato_width/2
    y2 = fato_y + fato_height/2 - 0.3

    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#1B4965', lw=1.5))

# Legenda
legenda_y = 2.0
ax.text(7.0, legenda_y, 'Relacionamentos 1:N (dimensão → fato)', ha='center', fontsize=9,
        style='italic', color='#666666')

# Salvar
plt.tight_layout()
plt.savefig('docs/modelo.png', dpi=150, bbox_inches='tight', facecolor='white')
print('Diagrama salvo em docs/modelo.png')