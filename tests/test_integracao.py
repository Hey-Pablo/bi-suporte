"""
Testes de integridade da carga do BI de Suporte.

Execute com: python3 -m unittest discover -s tests

Requisitos:
- SQL Server com os scripts 01_carga.sql e 02_visoes.sql executados
- Variáveis de conexão: SQL_SERVER, SQL_DATABASE, SQL_USER, SQL_PASSWORD
  (ou use Trusted_Connection=yes para autenticação do Windows)
"""

import unittest
import os
import pyodbc


class TestIntegracaoBISuporte(unittest.TestCase):
    """Verificações de integridade dos dados e do modelo estrela."""

    @classmethod
    def setUpClass(cls):
        """Conecta ao SQL Server usando variáveis de ambiente."""
        cls.server = os.getenv('SQL_SERVER', 'localhost')
        cls.database = os.getenv('SQL_DATABASE', 'BiSuporteDemo')
        cls.uid = os.getenv('SQL_USER', '')
        cls.pwd = os.getenv('SQL_PASSWORD', '')

        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={cls.server};'
            f'DATABASE={cls.database};'
        )
        if cls.uid and cls.pwd:
            conn_str += f';UID={cls.uid};PWD={cls.pwd}'
        else:
            conn_str += ';Trusted_Connection=yes;'

        cls.conn = pyodbc.connect(conn_str)
        cls.cursor = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        """Fecha a conexão."""
        cls.cursor.close()
        cls.conn.close()

    def test_total_chamados(self):
        """Verifica que existem exatamente 1500 chamados."""
        self.cursor.execute('SELECT COUNT(*) FROM fato_chamados')
        total = self.cursor.fetchone()[0]
        self.assertEqual(total, 1500, 'O total de chamados deve ser 1500')

    def test_resolvidos_pendentes(self):
        """Verifica distribuição entre resolvidos e pendentes."""
        self.cursor.execute(
            "SELECT COUNT(*) FROM fato_chamados WHERE status = N'resoldo'"
        )
        resolvidos = self.cursor.fetchone()[0]

        self.cursor.execute(
            "SELECT COUNT(*) FROM fato_chamados WHERE status = N'aberto'"
        )
        pendentes = self.cursor.fetchone()[0]

        self.assertEqual(resolvidos, 1383, 'Deve haver 1383 chamados resolvidos')
        self.assertEqual(pendentes, 117, 'Deve haver 117 chamados abertos')
        self.assertEqual(resolvidos + pendentes, 1500, 'Total deve ser 1500')

    def test_filas_unicas(self):
        """Verifica que existem 50 filiais distintas."""
        self.cursor.execute('SELECT COUNT(DISTINCT filial) FROM fato_chamados')
        filiais = self.cursor.fetchone()[0]
        self.assertEqual(filiais, 50, 'Devem existir 50 filiais distintas')

    def test_categorias_validas(self):
        """Verifica que as categorias são as esperadas."""
        categorias_esperadas = {'Impressora', 'ERP', 'Rede', 'Acesso', 'Hardware'}
        self.cursor.execute('SELECT DISTINCT categoria FROM fato_chamados')
        categorias_encontradas = {row[0] for row in self.cursor.fetchall()}
        self.assertEqual(categorias_encontradas, categorias_esperadas)

    def test_prioridades_validas(self):
        """Verifica que as prioridades são as esperadas."""
        prioridades_esperadas = {'baixa', 'média', 'alta', 'crítica'}
        self.cursor.execute('SELECT DISTINCT prioridade FROM fato_chamados')
        prioridades_encontradas = {row[0] for row in self.cursor.fetchall()}
        self.assertEqual(prioridades_encontradas, prioridades_esperadas)

    def test_status_validos(self):
        """Verifica que o status é apenas aberto ou resolvido."""
        self.cursor.execute('SELECT DISTINCT status FROM fato_chamados')
        status_encontrados = {row[0] for row in self.cursor.fetchall()}
        self.assertEqual(status_encontrados, {'aberto', 'resolvido'})

    def test_data_abertura_valida(self):
        """Verifica que data_abertura está coerente com aberto_em."""
        self.cursor.execute('''
            SELECT COUNT(*) FROM fato_chamados
            WHERE CAST(aberto_em AS date) <> data_abertura
        ''')
        incoerentes = self.cursor.fetchone()[0]
        self.assertEqual(incoerentes, 0, 'data_abertura deve ser aberto_em convertido para date')

    def test_tempo_medio_resolucao(self):
        """Verifica cálculo do tempo médio de resolução."""
        self.cursor.execute('SELECT AVG(horas_resolucao) FROM fato_chamados')
        media = self.cursor.fetchone()[0]
        # Tempo médio esperado: ~40,72 horas
        self.assertGreater(media, 35, 'Tempo médio de resolução deve ser > 35h')
        self.assertLess(media, 50, 'Tempo médio de resolução deve ser < 50h')

    def test_resolvido_no_prazo_consistencia(self):
        """Verifica consistência do campo resolvido_no_prazo."""
        self.cursor.execute('''
            SELECT COUNT(*) FROM fato_chamados
            WHERE status = N'resolvido' AND resolvido_no_prazo = 0
              AND COALESCE(horas_resolucao, 9999) <= prazo_horas
        ''')
        inconsistentes = self.cursor.fetchone()[0]
        self.assertEqual(
            inconsistentes, 0,
            'Chamados resolvidos dentro do prazo devem ter resolvido_no_prazo = 1'
        )

    def test_visoes_criadas(self):
        """Verifica que todas as visões necessárias existem."""
        visoes = ['dim_filial', 'dim_categoria', 'dim_prioridade',
                  'dim_atendente', 'dim_data', 'fato_chamados']
        for vista in visoes:
            self.cursor.execute(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = ?",
                (vista,)
            )
            existe = self.cursor.fetchone()[0]
            self.assertEqual(existe, 1, f'A visão {vista} deve existir')

    def test_relacionamentos_modelo(self):
        """Verifica que todas as dimensões têm registros."""
        self.cursor.execute('SELECT COUNT(*) FROM dim_filial')
        self.assertGreater(self.cursor.fetchone()[0], 0, 'dim_filial deve ter registros')

        self.cursor.execute('SELECT COUNT(*) FROM dim_categoria')
        self.assertGreater(self.cursor.fetchone()[0], 0, 'dim_categoria deve ter registros')

        self.cursor.execute('SELECT COUNT(*) FROM dim_prioridade')
        self.assertGreater(self.cursor.fetchone()[0], 0, 'dim_prioridade deve ter registros')

        self.cursor.execute('SELECT COUNT(*) FROM dim_data')
        self.assertGreater(self.cursor.fetchone()[0], 0, 'dim_data deve ter registros')

    def test_tempo_medio_resolucao_conferencia(self):
        """Verifica tempo médio de resolução contra valores de confluência."""
        self.cursor.execute('SELECT AVG(horas_resolucao) FROM fato_chamados')
        media = self.cursor.fetchone()[0]
        # Valor de confluência: 40,720854 horas
        self.assertAlmostEqual(media, 40.72, places=2,
                               msg='Tempo médio deve ser ~40,72 horas')

    def test_sla_percentual(self):
        """Verifica cálculo do SLA percentual."""
        # Referência UTC fixa como em docs/conferencia.md
        self.cursor.execute('''
            SELECT 100.0 * SUM(CASE WHEN resolvido_no_prazo = 1 THEN 1 ELSE 0 END) /
                   NULLIF(SUM(CASE WHEN status = N'resolvido' OR
                       (status = N'aberto' AND DATEADD(hour, prazo_horas, aberto_em) < '2025-01-01T00:00:00')
                       THEN 1 ELSE 0 END), 0) AS sla_percentual
            FROM fato_chamados
        ''')
        sla = self.cursor.fetchone()[0]
        # Valor de confluência: 56,066667%
        self.assertAlmostEqual(sla, 56.07, places=1,
                               msg='SLA deve ser ~56,07%')

    def test_resolvidos_no_prazo(self):
        """Verifica número de resolvidos no prazo."""
        self.cursor.execute('''
            SELECT COUNT(*) FROM fato_chamados
            WHERE status = N'resolvido' AND resolvido_no_prazo = 1
        ''')
        resolvidos_no_prazo = self.cursor.fetchone()[0]
        # Valor de confluência: 841 resolvidos no prazo
        self.assertEqual(resolvidos_no_prazo, 841,
                         'Deve haver 841 chamados resolvidos no prazo')

    def test_abertos_vencidos(self):
        """Verifica número de chamados abertos vencidos na referência UTC fixa."""
        # Referência: 2025-01-01 00:00:00 UTC
        self.cursor.execute('''
            SELECT COUNT(*) FROM fato_chamados
            WHERE status = N'aberto' AND aberto_em <= DATEADD(hour, -prazo_horas, '2025-01-01T00:00:00')
        ''')
        abertos_vencidos = self.cursor.fetchone()[0]
        # Valor de confluência: 117 abertos vencidos
        self.assertEqual(abertos_vencidos, 117,
                         'Deve haver 117 chamados abertos vencidos')

    def test_dim_categoria_registros(self):
        """Verifica dimensão de categoria."""
        self.cursor.execute('SELECT COUNT(*) FROM dim_categoria')
        total = self.cursor.fetchone()[0]
        self.assertEqual(total, 5, 'dim_categoria deve ter 5 registros')

    def test_dim_prioridade_registros(self):
        """Verifica dimensão de prioridade."""
        self.cursor.execute('SELECT COUNT(*) FROM dim_prioridade')
        total = self.cursor.fetchone()[0]
        self.assertEqual(total, 4, 'dim_prioridade deve ter 4 registros')

    def test_dim_atendente_registros(self):
        """Verifica dimensão de atendente - único valor 'Não informado'."""
        self.cursor.execute('SELECT COUNT(*) FROM dim_atendente')
        total = self.cursor.fetchone()[0]
        self.assertEqual(total, 1, 'dim_atendente deve ter 1 registro')

    def test_horas_resolucao_calculadas(self):
        """Verifica que horas_resolucao é calculada corretamente na visão."""
        self.cursor.execute('''
            SELECT COUNT(*) FROM fato_chamados
            WHERE status = N'resolvido' AND horas_resolucao IS NULL
        ''')
        nulos = self.cursor.fetchone()[0]
        self.assertEqual(nulos, 0,
                         'Chamados resolvidos devem ter horas_resolucao calculada')

    def test_filial_contagem(self):
        """Verifica que há 50 filiais distintas."""
        self.cursor.execute('SELECT COUNT(DISTINCT filial) FROM fato_chamados')
        total = self.cursor.fetchone()[0]
        self.assertEqual(total, 50, 'Devem existir exatamente 50 filiais distintas')


if __name__ == '__main__':
    unittest.main()