| cenário | insercao | intercalacao | rapida | hibrida | contagem | base | ordenar | melhor | escolher (s) | escolheu |
|---|---|---|---|---|---|---|---|---|---|---|
| aleatorio_grande | timeout(>120s) | 0.2967 | 0.3677 | 0.2916 | inviavel | **0.0841** | 0.0910 | base | 0.0024 | base |
| faixa_estreita | timeout(>120s) | 4.9410 | 0.8566 | 0.9782 | **0.1247** | 0.2407 | 0.1453 | contagem | 0.0195 | contagem |
| quase_ordenado | **0.0241** | 0.3393 | 0.5850 | 0.5374 | 0.0631 | 0.0926 | 0.0296 | insercao | 0.0039 | insercao |
| minuscula | 0.0508 | 0.1071 | 0.0948 | **0.0494** | 0.2047 | 0.2749 | 0.0496 | hibrida | 0.0004 | insercao |
| erro_duas_corridas | 7.8747 | 0.0294 | 0.0486 | 0.0419 | **0.0053** | 0.0054 | 8.1153 | contagem | 0.0005 | insercao |
| erro_trocas_distantes | 0.2403 | 0.0351 | 0.0515 | 0.0406 | **0.0051** | 0.0057 | 0.2391 | contagem | 0.0004 | insercao |
| erro_outlier | timeout(>120s) | 0.4724 | 0.1726 | 0.1626 | inviavel | **0.1104** | 0.1113 | base | 0.0040 | base |

**Pior razão (tempo / melhor do cenário) por método (timeout ou inviável = infinito):**

| insercao | intercalacao | rapida | hibrida | contagem | base | ordenar |
|---|---|---|---|---|---|---|
| inf | 39.62x | 24.25x | 22.27x | inf | 5.57x | 1519.57x |
