import datetime as dt
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def instante(valor):
    return dt.datetime.fromisoformat(valor.replace('Z', '+00:00'))

class DadosTest(unittest.TestCase):
    def test_carga_reproduz_origem(self):
        dados = json.loads((ROOT / 'sql/chamados.json').read_text())
        sql = (ROOT / 'sql/01_carga.sql').read_text()
        linhas = re.findall(r"^\((\d+), N'([^']*)', N'([^']*)', N'([^']*)', N'([^']*)', (NULL|N'[^']*'), (\d+), N'([^']*)'\)[,;]$", sql, re.M)
        self.assertEqual(len(linhas), len(dados))
        for linha, c in zip(linhas, dados):
            data = lambda x: x.replace('T', ' ').replace('Z', '')
            resolvido = 'NULL' if c['resolvido_em'] is None else "N'" + data(c['resolvido_em']) + "'"
            self.assertEqual(linha, (str(c['id']), c['filial'], c['categoria'], c['prioridade'], data(c['aberto_em']), resolvido, str(c['prazo_horas']), c['status']))
        self.assertEqual(len({c['id'] for c in dados}), len(dados))

    def test_conferencia(self):
        dados = json.loads((ROOT / 'sql/chamados.json').read_text())
        referencia = instante('2025-01-01T00:00:00Z')
        resolvidos = [c for c in dados if c['status'] == 'resolvido']
        abertos = [c for c in dados if c['status'] == 'aberto']
        horas = lambda c: (instante(c['resolvido_em']) - instante(c['aberto_em'])).total_seconds() / 3600
        no_prazo = sum(horas(c) <= c['prazo_horas'] for c in resolvidos)
        vencidos = sum((referencia - instante(c['aberto_em'])).total_seconds() > c['prazo_horas'] * 3600 for c in abertos)
        self.assertEqual((len(dados), len(resolvidos), len(abertos), no_prazo, vencidos), (1500, 1383, 117, 841, 117))
        self.assertAlmostEqual(sum(map(horas, resolvidos)) / len(resolvidos), 40.720854, places=6)
        self.assertAlmostEqual(100 * no_prazo / (len(resolvidos) + vencidos), 56.066667, places=5)

if __name__ == '__main__':
    unittest.main()
