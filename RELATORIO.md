# Relatório — Projeto G2 EDA: ordenação adaptativa

**Autora:** Yara Fernandes Ribeiro (trabalho individual)

---

## 1. Resumo

O trabalho parte da ideia de que **nenhum método de ordenação ganha sempre**. Foram implementados seis métodos (inserção, intercalação, rápida com pivô aleatório, híbrida, contagem e base) e um **escolhedor** que decide, com custo baixo, qual deles aplicar a uma lista.

Em quatro cenários de teste, o `ordenar` (escolhedor + método escolhido) ficou entre **1,00x e 1,23x** do tempo do melhor método de cada cenário. Os métodos isolados tiveram desempenho muito mais irregular: a pior razão para a intercalação foi 39,6x, para a rápida 24,3x e para a híbrida 22,3x, e a inserção e a contagem não chegaram a terminar em pelo menos um cenário.

Também foram construídos três cenários adversariais em que o escolhedor **erra**. O pior é uma lista com uma única descida e cerca de n²/4 inversões, em que o `ordenar` ficou 1520x pior que o melhor método. As causas e possíveis correções estão na seção 8.

---

## 2. Problema e objetivo

Dada uma lista de inteiros, escolher automaticamente o algoritmo de ordenação mais adequado, sem gastar na decisão um tempo comparável ao da própria ordenação.

Objetivos específicos:

1. Implementar seis métodos corretos (inclusive com negativos, duplicatas, lista vazia e entrada de um elemento).
2. Projetar um escolhedor que use só informações baratas sobre a entrada.
3. Justificar os limites do escolhedor com um experimento, e não por intuição.
4. Medir os métodos e o `ordenar` em cenários que favorecem métodos diferentes.
5. Documentar os casos em que a heurística falha.

---

## 3. Métodos implementados

| Método | Complexidade | Memória extra | Estável | Quando brilha |
|---|---|---|---|---|
| Inserção | O(n + inversões), pior caso O(n²) | O(1) além da cópia | sim | listas minúsculas, já ordenadas ou quase ordenadas |
| Intercalação | O(n log n) | O(n) | sim (usa `<=`) | garantia de tempo; não depende da distribuição |
| Rápida | O(n log n) esperado | O(log n) de pilha | não | uso geral em memória |
| Híbrida | O(n log n) esperado | O(log n) de pilha | não | uso geral; evita a recursão profunda nas folhas |
| Contagem | O(n + k) | O(k) | n/a (inteiros) | faixa de valores k pequena frente a n |
| Base (LSD, base 256) | O(d · (n + 256)) | O(n) | sim | inteiros de até 64 bits, faixa grande |

Decisões de implementação relevantes:

- **Rápida com partição em 3 vias** (`<`, `==`, `>`). Sem isso, uma lista com todos os valores iguais, ou com poucos valores distintos, degeneraria para O(n²). Essa escolha é o que mantém a rápida competitiva na `faixa_estreita` (0,86 s contra 4,94 s da intercalação).
- **Recursão só no lado menor** e iteração no maior, o que limita a pilha a O(log n).
- **Híbrida** reutiliza o mesmo núcleo da rápida (`rapida_nucleo`) com `LIMIAR_HIBRIDA = 24`: partições com até 24 elementos vão para a inserção.
- **Contagem** desloca os valores pelo mínimo, o que permite negativos, e **recusa** faixas acima de 10⁷ com `MemoryError`, em vez de tentar alocar um vetor gigante. O escolhedor usa o mesmo teto (`MAX_FAIXA_CONTAGEM`).
- **Base** também desloca pelo mínimo e calcula o número de passadas a partir do `bit_length` da faixa. A distribuição por byte é estável, como o LSD exige.
- **Intercalação** usa índices em vez de `pop(0)`, que custaria O(n) por remoção.
- Todos os métodos devolvem **uma nova lista** e não alteram a entrada (verificado nos testes).

---

## 4. O escolhedor

### 4.1 Regras

O escolhedor mede apenas `n`, o mínimo, o máximo e a fração de descidas (`v[i-1] > v[i]`) em cerca de 1000 pares adjacentes espaçados. Aplica as regras em ordem:

1. `n <= 32` → **inserção**.
2. mínimo = máximo (todos iguais) → **inserção** (custo O(n)).
3. fração de descidas na amostra ≤ 5% → **inserção** (lista já ou quase ordenada).
4. faixa ≤ 0,5 · n e faixa ≤ 10⁷ → **contagem**.
5. faixa cabe em até 8 passadas de 8 bits (64 bits) → **base**.
6. caso contrário (chaves enormes) → **híbrida**.

A checagem de memória (regra 4) ocorre antes de qualquer alocação da contagem.

### 4.2 Custo da decisão

O tempo gasto só em `escolher` aparece na coluna própria da tabela de resultados:

| cenário | escolher (s) | % do tempo de `ordenar` |
|---|---|---|
| aleatorio_grande | 0,0024 | 2,7% |
| faixa_estreita | 0,0195 | 13,4% |
| quase_ordenado | 0,0039 | 13,0% |
| minuscula | 0,0004 | 0,8% |

A parte principal do custo são as duas passadas nativas de `min` e `max` sobre a lista. Ela é proporcionalmente maior quando o método escolhido é muito rápido (contagem e inserção em lista quase ordenada) e desprezível nos demais.

---

## 5. Metodologia

**Dados.** Todos os geradores usam `random.Random(42)`, então os cenários são idênticos entre execuções. As medições não dependem do acaso dos dados.

**Cenários do trabalho:**

| Cenário | Descrição | Método esperado |
|---|---|---|
| `aleatorio_grande` | 100 000 inteiros aleatórios em (0, 10¹²) | base |
| `faixa_estreita` | 1 000 000 inteiros em [0, 100] | contagem |
| `quase_ordenado` | 200 000 elementos ordenados + 1% de trocas locais (distância ≤ 10) | inserção |
| `minuscula` | 5000 listas de 20 elementos em [0, 1000] | inserção ou híbrida |

**Cenários extras (`--extras`)**, desenhados para enganar o escolhedor:

| Cenário | Descrição |
|---|---|
| `erro_duas_corridas` | `[0,2,4,…,1,3,5,…]`, n = 20 000: uma única descida, cerca de n²/4 inversões |
| `erro_trocas_distantes` | ordenada + 1% de trocas entre posições aleatórias, n = 20 000 |
| `erro_outlier` | n = 200 000, quase tudo em [0, 100] e um único valor 10⁹ |

**Medição.** Para cada par (cenário, método):

- o método roda em **processo separado**, com limite de tempo de 120 s (acima disso é registrado `timeout`);
- `MemoryError` vira `inviavel`;
- a cópia da lista é feita **fora** do cronômetro (`time.perf_counter`);
- são feitas 5 repetições e o resultado é a **mediana**;
- `ordenar` (decisão + método) e `escolher` (só a decisão) são medidos como linhas à parte.

---

## 6. Calibração dos limites

Os limites do escolhedor vêm de `python Medicoes.py --calibrar`. Os números abaixo foram obtidos ao repetir o experimento (Python 3.12, Linux). Os tempos absolutos dependem da máquina, mas a forma das curvas e os pontos de cruzamento são o que importa.

### 6.1 Inserção × híbrida (aleatório) → `LIMITE_MINUSCULA = 32`

| n | inserção (µs) | híbrida (µs) |
|---|---|---|
| 8 | 1,7 | 1,4 |
| 16 | 3,5 | 3,5 |
| 24 | 7,1 | 7,2 |
| 32 | 10,4 | 10,3 |
| 48 | 26,3 | 19,0 |
| 64 | 36,3 | 25,8 |
| 96 | 98,6 | 43,9 |
| 128 | 144,3 | 61,3 |

Até n = 32 os dois empatam. A partir de 48 a híbrida abre vantagem crescente. Daí o limite em 32.

### 6.2 Limiar da híbrida (n = 100 000) → `LIMIAR_HIBRIDA = 24`

| T | 1 | 8 | 16 | 24 | 32 | 48 | 64 |
|---|---|---|---|---|---|---|---|
| tempo (s) | 0,2335 | 0,2334 | 0,2437 | **0,2177** | 0,2310 | 0,2384 | 0,2215 |

A curva é praticamente plana: a diferença entre o melhor e o pior valor é de cerca de 10%, e essa diferença não é monotônica, o que sugere ruído. O valor 24 foi o menor tempo observado, mas a escolha é **pouco sensível**, e qualquer T entre 8 e 64 serviria.

### 6.3 Contagem × base × híbrida por faixa (n = 200 000) → `FATOR_FAIXA = 0,5`

| faixa | contagem (s) | base (s) | híbrida (s) |
|---|---|---|---|
| 100 | **0,0113** | 0,0195 | 0,1194 |
| 1 000 | **0,0132** | 0,0535 | 0,1986 |
| 10 000 | **0,0130** | 0,0807 | 0,3265 |
| 100 000 | **0,0261** | 0,0627 | 0,4789 |
| 800 000 | **0,0752** | 0,1063 | 0,4336 |
| 3 200 000 | 0,2238 | **0,0724** | 0,4562 |

O cruzamento entre contagem e base fica entre 4·n e 16·n. O fator 0,5·n, portanto, é **conservador**: dentro dele a contagem sempre vence com folga, e o escolhedor desperdiça pouco ao usar a base entre 0,5·n e 4·n. Um fator maior poderia render um pouco mais, mas só foi medido com n = 200 000. Mantê-lo baixo também protege a memória.

### 6.4 Base × híbrida por número de bits (n = 100 000) → `PASSADAS_MAX_BASE = 8`

| bits | base (s) | híbrida (s) |
|---|---|---|
| 8 | **0,0089** | 0,0697 |
| 16 | **0,0245** | 0,2264 |
| 24 | **0,0314** | 0,1887 |
| 32 | **0,0779** | 0,2122 |
| 40 | **0,0841** | 0,2367 |
| 48 | **0,0658** | 0,2678 |
| 64 | **0,0925** | 0,1966 |

A base vence a híbrida em todos os tamanhos testados, até 64 bits (8 passadas). O limite de 8 passadas está dentro da região medida. **Acima de 64 bits não há medição**: enviar chaves gigantes (por exemplo, 10³⁰) para a híbrida é uma decisão de projeto, coberta por teste de corretude (`test_regras`), mas não por experimento de desempenho.

---

## 7. Resultados

Tempos em segundos (mediana de 5 execuções, limite de 120 s por método). `ordenar` = decisão + método escolhido.

| cenário | insercao | intercalacao | rapida | hibrida | contagem | base | ordenar | melhor | escolheu |
|---|---|---|---|---|---|---|---|---|---|
| aleatorio_grande | timeout | 0,2967 | 0,3677 | 0,2916 | inviável | **0,0841** | 0,0910 | base | base |
| faixa_estreita | timeout | 4,9410 | 0,8566 | 0,9782 | **0,1247** | 0,2407 | 0,1453 | contagem | contagem |
| quase_ordenado | **0,0241** | 0,3393 | 0,5850 | 0,5374 | 0,0631 | 0,0926 | 0,0296 | insercao | insercao |
| minuscula | 0,0508 | 0,1071 | 0,0948 | **0,0494** | 0,2047 | 0,2749 | 0,0496 | hibrida | insercao |

### 7.1 Razão em relação ao melhor método (quanto mais perto de 1, melhor)

| cenário | intercalação | rápida | híbrida | contagem | base | **ordenar** |
|---|---|---|---|---|---|---|
| aleatorio_grande | 3,53x | 4,37x | 3,47x | inviável | 1,00x | **1,08x** |
| faixa_estreita | 39,62x | 6,87x | 7,84x | 1,00x | 1,93x | **1,17x** |
| quase_ordenado | 14,07x | 24,25x | 22,27x | 2,61x | 3,84x | **1,23x** |
| minuscula | 2,17x | 1,92x | 1,00x | 4,14x | 5,57x | **1,00x** |

A inserção ficou em timeout (> 120 s) em dois cenários e a contagem foi inviável em um. Por isso a pior razão desses dois métodos é infinita.

### 7.2 Análise por cenário

**Aleatorio_grande:** A faixa (10¹²) torna a contagem impossível: ela recusa a execução em vez de estourar a memória. A inserção, quadrática, não termina. A base (4 passadas de 8 bits, ~0,084 s) é cerca de 3,5x mais rápida que a intercalação e a híbrida. O escolhedor acertou e custou só 2,7% do tempo total.

**Faixa_estreita:** Com só 101 valores distintos em 1 milhão de elementos, a contagem faz uma passada de contagem e uma de escrita, e termina em 0,125 s. A diferença entre os comparativos é grande: a intercalação leva 4,94 s (39,6x). A rápida se sai bem (0,86 s) graças à partição em 3 vias. O escolhedor acertou, mas pagou 13% de overhead, porque a decisão (≈ 0,02 s) é relevante diante de um método que leva ≈ 0,12 s.

**Quase_ordenado:** Com 1% de trocas locais, o número de inversões é pequeno e a inserção roda em tempo quase linear (0,024 s). É um cenário em que os métodos "de n log n" ficam 14x a 24x atrás. O escolhedor identificou a ordem pela amostra de descidas e acertou, com overhead de 23%.

**Minuscula:** A diferença entre inserção (0,0508) e híbrida (0,0494) é de cerca de 3%, ou seja, um empate técnico. A híbrida em listas de 20 elementos já executa só a inserção (o limiar é 24), então a diferença vem apenas do custo extra de chamada. O `ordenar` (0,0496) ficou colado no melhor. Contagem e base são 4x a 5x piores aqui, porque o custo fixo (vetor de contagem, 256 baldes por passada) domina em listas minúsculas.

### 7.3 Pior razão por método (os 4 cenários do trabalho)

| método | pior razão | cenário do pior caso |
|---|---|---|
| insercao | ∞ (timeout) | aleatorio_grande, faixa_estreita |
| contagem | ∞ (inviável) | aleatorio_grande |
| intercalacao | 39,62x | faixa_estreita |
| rapida | 24,25x | quase_ordenado |
| hibrida | 22,27x | quase_ordenado |
| base | 5,57x | minuscula |
| **ordenar** | **1,23x** | quase_ordenado |

Esta é a principal conclusão: cada método sozinho tem um cenário em que vai muito mal, e o `ordenar` não tem. A tabela geral gerada por `Medicoes.py` (`Resultados_para_Analise/tabela.md`) traz a mesma comparação, mas incluindo os cenários extras.

---

## 8. Cenários em que o escolhedor erra

Executados com `python Medicoes.py --extras`.

| cenário | melhor método | melhor (s) | escolheu | `ordenar` (s) | razão |
|---|---|---|---|---|---|
| erro_duas_corridas | contagem (base empata: 0,0054) | 0,0053 | insercao | 8,1153 | **1519,6x** |
| erro_trocas_distantes | contagem (base: 0,0057) | 0,0051 | insercao | 0,2391 | **47,0x** |
| erro_outlier | base | 0,1104 | base | 0,1113 | 1,01x |

### 8.1 `erro_duas_corridas`

A lista `[0,2,4,…,1,3,5,…]` tem **uma única descida** (no ponto onde as duas corridas se encontram), mas cerca de n²/4 inversões. A amostra de pares adjacentes mede a fração de descidas, e essa fração é ~0, então o escolhedor conclui "quase ordenada" e escolhe a inserção, cujo custo é proporcional às inversões: 7,87 s contra 0,005 s dos métodos que não dependem da ordem.

**Causa:** a quantidade medida (descidas adjacentes) é um indicador fraco do que a inserção realmente custa (inversões totais).

### 8.2 `erro_trocas_distantes`

Com 1% de trocas entre posições **aleatórias** (e não locais), cada troca cria poucas descidas adjacentes, então a fração fica abaixo de 5% e a inserção é escolhida. Só que os elementos trocados ficam longe do lugar certo, e a inserção paga caro (0,24 s, 47x o melhor). O contraste com `quase_ordenado` é instrutivo: o mesmo 1% de trocas é inofensivo quando as trocas são locais e custoso quando são distantes.

### 8.3 `erro_outlier`

Um único valor 10⁹ no meio de dados em [0, 100] estoura o teto de memória da contagem, que seria o método ideal para quase todos os elementos. O escolhedor então vai para a base, que é a melhor opção viável (0,1104 s). Na prática, **o escolhedor não erra aqui**: a razão é 1,01x. O cenário mostra a fragilidade da contagem diante de outliers, e não uma falha da decisão. Uma melhoria possível seria tratar o outlier separadamente e usar a contagem no restante.

### 8.4 Como corrigir (não implementado)

- **Estimar inversões, não descidas.** Amostrar pares aleatórios (i < j) e contar a fração com `v[i] > v[j]`. Em `erro_duas_corridas` essa fração é ≈ 25%, o que descartaria a inserção. Em `quase_ordenado` seria ≈ 0, e a inserção seria mantida.
- **Comparar elementos a distâncias maiores**, por exemplo `v[i]` com `v[i + d]` para vários d, para detectar deslocamentos longos.
- **Limitar o risco da inserção**: abandonar a inserção e cair em outro método se o número de deslocamentos ultrapassar um orçamento (algo como c · n).

Esse ajuste custaria um pouco mais na decisão (mais acessos aleatórios), mas ainda com custo fixo, independente de n, como o restante do escolhedor.

---

## 9. Corretude e testes

`Suite_de_testes.py` tem 6 testes e todos passam (verificado com Python 3.12):

| Teste | O que verifica |
|---|---|
| `test_casos_de_borda_em_cada_metodo` | cada um dos 6 métodos em 9 casos de borda (vazia, 1 elemento, todos iguais, ordenada, invertida, negativos, só negativos, mista, grande) produz o mesmo resultado que `sorted` **sem alterar a entrada** |
| `test_ordenar_casos_de_borda` | `ordenar` nos mesmos casos |
| `test_ordenar_aleatorios_variados` | 30 listas aleatórias (n de 33 a 5000, faixas de ±5 a ±10¹²) |
| `test_regras` | cada regra do escolhedor com uma entrada típica |
| `test_faixa_gigante_nunca_escolhe_contagem` | proteção de memória no escolhedor |
| `test_contagem_recusa_faixa_gigante` | a contagem levanta `MemoryError` com faixa 10¹² |

---

## 10. Limitações e ameaças à validade

- **Uma máquina e um ambiente.** Os tempos absolutos dependem do hardware e da versão do Python. Os limites do escolhedor foram calibrados numa configuração, e os pontos de cruzamento podem se deslocar em outra.
- **Um tamanho por cenário.** Cada cenário usa um único n. Não há curva de crescimento por n, então as complexidades teóricas não foram verificadas empiricamente.
- **Python puro.** Métodos implementados em laços Python pagam o custo do interpretador, enquanto `min`, `max` e `sorted` são nativos. Isso favorece algoritmos com poucos laços (contagem, base) em relação a outros em C e é parte do motivo pelo qual a base vence a híbrida mesmo com 64 bits. Em C, os resultados poderiam ser diferentes.
- **Comparação com `sorted` do Python.** O `sorted` nativo (Timsort) não está nas tabelas. Ele serve como oráculo nos testes, mas não como concorrente nas medições.
- **Só inteiros.** A contagem e a base dependem de chaves inteiras. O escolhedor não trata `float` ou `str`.
- **Mediana de 5 repetições.** É um número pequeno. Diferenças abaixo de ~5% (como `minuscula`, inserção × híbrida) não devem ser interpretadas como vitória de um método.
- **Heurística de ordem fraca.** Mostrado na seção 8.

---

## 11. Conclusão

O experimento confirma a hipótese central: **não existe método melhor em todos os cenários**. A base domina em inteiros aleatórios grandes, a contagem em faixa estreita, a inserção em listas quase ordenadas, e métodos de uso geral como a intercalação ficam de 14x a 40x atrás do melhor quando a estrutura dos dados é favorável a outro método.

Um escolhedor de custo baixo (entre 1% e 13% do tempo total nos cenários medidos) resolveu isso: o `ordenar` ficou a no máximo 1,23x do melhor método em todos os cenários do trabalho, sem nunca estourar tempo nem memória.

Os limites vieram de experimentos de calibração, e dois deles (o fator de faixa e o limiar da híbrida) se mostraram conservadores ou pouco sensíveis, o que é um bom sinal de robustez. Em contrapartida, a medida de ordenação do escolhedor (fração de descidas adjacentes) pode ser enganada por listas com poucas descidas e muitas inversões, com custo de até três ordens de grandeza. Trocá-la por uma estimativa de inversões por pares aleatórios é o próximo passo natural.

---

## 12. Como reproduzir

```bash
python Suite_de_testes.py       
python Medicoes.py              
python Medicoes.py --extras      
python Medicoes.py --calibrar    
```

Arquivos gerados: `Resultados_para_Analise/resultados.csv` e `Resultados_para_Analise/tabela.md`.