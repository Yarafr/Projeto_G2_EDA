import random
import unittest
import DadosParaMetodos as D
from Escolhedor import METODOS, ordenar, escolher
from Metodos.Contagem import contagem


class TestMetodos(unittest.TestCase):
    def test_casos_de_borda_em_cada_metodo(self):
        for nome, f in METODOS.items():
            for caso, v in D.CASOS_BORDA.items():
                with self.subTest(metodo=nome, caso=caso):
                    entrada = list(v)
                    self.assertEqual(f(entrada), sorted(v))
                    self.assertEqual(entrada, v)       # não altera a entrada

    def test_ordenar_casos_de_borda(self):
        for caso, v in D.CASOS_BORDA.items():
            with self.subTest(caso=caso):
                self.assertEqual(ordenar(list(v)), sorted(v))

    def test_ordenar_aleatorios_variados(self):
        r = random.Random(7)
        for _ in range(30):
            n = r.choice([33, 100, 1000, 5000])
            hi = r.choice([5, 1000, 10**6, 10**12])
            v = [r.randint(-hi, hi) for _ in range(n)]
            self.assertEqual(ordenar(v), sorted(v))


class TestEscolher(unittest.TestCase):
    def test_faixa_gigante_nunca_escolhe_contagem(self):
        r = random.Random(3)
        v = [r.randint(0, 10**12) for _ in range(5000)]
        self.assertNotEqual(escolher(v), "contagem")
        v = [r.randint(0, 1) * 10**9 for _ in range(200)]
        self.assertNotEqual(escolher(v), "contagem")

    def test_contagem_recusa_faixa_gigante(self):
        with self.assertRaises(MemoryError):
            contagem([0, 10**12])

    def test_regras(self):
        r = random.Random(5)
        self.assertEqual(escolher([3, 1, 2]), "insercao")            
        self.assertEqual(escolher(list(range(1000))), "insercao")     
        self.assertEqual(escolher([4] * 1000), "insercao")            
        v = [r.randint(0, 100) for _ in range(5000)]
        self.assertEqual(escolher(v), "contagem")                     
        v = [r.randint(0, 10**9) for _ in range(5000)]
        self.assertEqual(escolher(v), "base")                        
        v = [r.randint(0, 10**30) for _ in range(5000)]
        self.assertEqual(escolher(v), "hibrida")                      


if __name__ == "__main__":
    unittest.main(verbosity=2)