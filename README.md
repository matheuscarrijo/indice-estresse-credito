# Índice de Desconforto de Crédito

Este repositório contém o código e a documentação para a construção de um **índice** que captura o nível de desconforto de crédito das famílias brasileiras.

## 1. Motivação

O projeto surge no contexto de:

- Crescente debate público sobre **endividamento das famílias**
- Políticas recentes como o **Programa Desenrola**
- Interesse em criar uma métrica análoga ao "índice de desconforto econômico" tradicional (inflação + desemprego), mas focada em **crédito**

## 2. Estrutura do Índice

O índice é composto por **três dimensões**, cada uma com dados disponíveis na planilha [data/estatisticas-monetarias-e-de-credito/tabelas-estatisticas-monetarias-e-de-credito.xlsx](data/estatisticas-monetarias-e-de-credito/tabelas-estatisticas-monetarias-e-de-credito.xlsx). Para mais informações sobre os dados, ver a seção 9 abaixo.

### 2.1. Comprometimento de renda com dívida

- Código SGS: `29034`
- Conceito: Comprometimento de renda - Relação entre o valor correspondente aos pagamentos esperados para o serviço da dívida com o Sistema Financeiro Nacional e a renda mensal das famílias, em média móvel trimestral, ajustado sazonalmente.
- Para mais informações sobre a série: [https://dadosabertos.bcb.gov.br/dataset/29034-comprometimento-de-renda-das-familias-com-o-servico-da-divida-com-o-sistema-financeiro-nacion](https://dadosabertos.bcb.gov.br/dataset/29034-comprometimento-de-renda-das-familias-com-o-servico-da-divida-com-o-sistema-financeiro-nacion)

### 2.2. Inadimplência da carteira de crédito (90+ dias)

- Código SGS: `21112`
- Conceito: Percentual da carteira de crédito livre do Sistema Financeiro Nacional com pelo menos uma parcela com atraso superior a 90 dias. Não inclui operações referenciadas em taxas regulamentadas, operações vinculadas a recursos do BNDES ou quaisquer outras lastreadas em recursos compulsórios ou governamentais.
- Para mais informações sobre a série: [https://dadosabertos.bcb.gov.br/dataset/21112-inadimplencia-da-carteira-de-credito-com-recursos-livres---pessoas-fisicas---total](https://dadosabertos.bcb.gov.br/dataset/21112-inadimplencia-da-carteira-de-credito-com-recursos-livres---pessoas-fisicas---total)

### 2.3. Qualidade do crédito (composição do crédito "caro")

Mede a fração do crédito livre de pessoa física alocada em modalidades consideradas mais onerosas.

Componentes:

- Cheque especial (código SGS: `20573`)
- Crédito pessoal não consignado (código SGS: `20574`)
- Cartão de crédito rotativo (código SGS: `20587`)
- Cartão de crédito parcelado (código SGS: `20588`)

Métrica:

- Participação dessas modalidades no total de crédito livre para pessoa física (código SGS: `20570`), expressa como **fração [0, 1]** (e.g., 0,21 = 21% do crédito livre PF alocado em modalidades onerosas)

## 3. Construção do Índice

### 3.1. Métodos de Normalização

Como as três séries têm escalas distintas, cada componente é normalizado antes da agregação. O índice é produzido em **duas versões paralelas** — uma por método — para comparação.

#### 3.1.1. Min-Max

$$
x^{norm}_t = \frac{x_t - \min_\tau(x)}{\max_\tau(x) - \min_\tau(x)}
$$

onde $\min_\tau$ e $\max_\tau$ denotam o mínimo e o máximo calculados sobre a janela de referência $\tau$ (ver seção 3.2). O resultado indica **qual fração do range da janela o valor atual representa**: 0 corresponde ao mínimo da janela e 1 ao máximo.

| | |
|---|---|
| **Prós** | Simples; interpretável como proporção do range histórico; linearidade |
| **Contras** | Sensível a outliers; extremos da pandemia (mínimos artificiais por moratórias e transferências emergenciais) podem distorcer a escala, comprimindo o restante da série |

#### 3.1.2. Rank Percentil

$$
x^{norm}_t = \frac{|\{s \in \tau : x_s \leq x_t\}|}{|\tau|}
$$

O numerador conta quantas observações da janela de referência $\tau$ são menores ou iguais ao valor atual; $|\tau|$ é o tamanho da janela. O resultado é diretamente o **percentil empírico** de $x_t$ na distribuição da janela: um valor de 0,8 significa que 80% das observações da janela foram iguais ou inferiores ao nível atual.

| | |
|---|---|
| **Prós** | Totalmente robusto a outliers; interpretável diretamente como percentil histórico |
| **Contras** | Não-linear: perde informação sobre a magnitude das diferenças entre observações |

### 3.2. Janelas de Normalização

Os parâmetros $\min_\tau$, $\max_\tau$ e a distribuição de referência de cada componente são calculados sobre uma **janela temporal** $\tau$, sem viés de lookahead — em cada período $t$, a janela usa apenas observações disponíveis até $t$.

O índice é produzido em duas variantes de janela:

#### 3.2.1. Janela Expansiva

A janela cresce a partir do início da amostra (mar-2011): $\tau = \{1, \ldots, t\}$. Os primeiros anos do histórico são utilizados como período de aquecimento; o índice é exibido a partir de **jan-2014** (~34 meses de aquecimento).

#### 3.2.2. Janela Móvel (60 meses)

A janela cobre os 60 meses imediatamente anteriores a cada período: $\tau = \{t-59, \ldots, t\}$. A série começa naturalmente em **mar-2016** (quando o primeiro bloco de 60 observações fica disponível). Esta variante é mais sensível a mudanças de regime recentes, pois o nível de estresse é sempre calibrado em relação aos últimos 5 anos.

### 3.3. Agregação

Após normalização, o índice é calculado como média simples dos três componentes:

$$
\text{Índice}_t = \frac{1}{3} (C_t + I_t + Q_t)
$$

onde:

- $C_t$: comprometimento de renda (normalizado)
- $I_t$: inadimplência (normalizada)
- $Q_t$: qualidade do crédito (normalizada)

O índice é produzido em **quatro versões paralelas**: dois métodos de normalização (3.1.1 e 3.1.2) × duas janelas (3.2.1 e 3.2.2), com pesos iguais (1/3) em todas.

### 3.4. Representação Base 100

Além das versões normalizadas [0–1], os componentes brutos e os índices compostos são também expressos em **base 100**, facilitando a comparação da dinâmica relativa entre séries com magnitudes distintas.

$$
x^{base100}_t = \frac{x_t}{x_{t_0}} \times 100
$$

onde $t_0$ é a primeira observação válida de cada série. Um valor de 120 indica que a série cresceu 20% em relação à base.

A transformação é aplicada a:

- **Componentes brutos** (C, I, Q): $t_0$ = mar-2011 (início da amostra), permitindo visualizar qual componente variou mais em termos relativos ao longo de todo o período.
- **Índices compostos**: $t_0$ é o primeiro valor não-NaN de cada variante de janela (jan-2014 para expansiva; mar-2016 para móvel 60m).

Diferente das versões normalizadas, a escala base 100 **não tem limites fixos** — o eixo Y é livre, refletindo a magnitude real das variações relativas.

## 4. Horizonte Temporal

Os dados brutos cobrem **mar-2011 a jan-2026** (179 observações mensais), determinado pela série mais curta disponível na planilha — SGS 29034 (comprometimento de renda), que é publicada com maior defasagem que as demais. O horizonte visível de cada variante do índice é:

| Variante | Início da série exibida |
|---|---|
| Janela Expansiva | jan-2014 |
| Janela Móvel (60m) | mar-2016 |

## 5. Como Reproduzir

**Pré-requisitos:** Python 3.9+ com as dependências listadas em `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Execução** a partir do diretório raiz do projeto:

```bash
python main.py
```

O script carrega os dados, constrói os três componentes e as quatro versões do índice (2 métodos × 2 janelas), salva os CSVs em `outputs/data/` e as figuras em `outputs/figures/`.

## 6. Estrutura do Repositório

```
├── data/
│   ├── estatisticas-monetarias-e-de-credito/
│   │   └── tabelas-estatisticas-monetarias-e-de-credito.xlsx   # fonte primária (BCB)
│   └── sgs-estatisticas-de-credito-endividamento-das-familias/
│       ├── tabelas-estatisticas-de-credito-endividamento-das-familias.csv
│       ├── metodologia.md
│       └── alreracoes-metodologicas/                           # boxes metodológicos do BCB
├── src/
│   ├── load_data.py     # carrega as séries do Excel
│   ├── normalize.py     # funções de normalização (min-max e rank percentil, expansiva e móvel)
│   ├── build_index.py   # constrói componentes C, I, Q e agrega o índice
│   └── plot.py          # gera as figuras
├── outputs/
│   ├── data/            # series_raw.csv, components_raw.csv, index_expanding.csv, index_rolling.csv
│   └── figures/
│       ├── general/     # componentes brutos (não normalizados)
│       ├── expanding/   # figuras da janela expansiva
│       └── rolling/     # figuras da janela móvel 60m
├── main.py              # ponto de entrada
├── requirements.txt
└── README.md
```

## 7. Outputs Gerados

**Dados (`outputs/data/`):**

- **`series_raw.csv`** — séries brutas carregadas do Excel
- **`components_raw.csv`** — componentes C, I, Q antes da normalização
- **`index_expanding.csv`** — componentes normalizados e índice agregado (janela expansiva, a partir de jan-2014)
- **`index_rolling.csv`** — componentes normalizados e índice agregado (janela móvel 60m, a partir de mar-2016)

**Figuras (`outputs/figures/`):**

Organizadas em subpastas por tipo de janela de normalização.

`general/`:

| Arquivo | Conteúdo |
|---|---|
| `components_raw.png` | Componentes C, I, Q em valores brutos (não normalizados) |
| `components_base100.png` | C, I, Q sobrepostos em base 100 (Mar-2011 = 100) |

`expanding/` — janela expansiva:

| Arquivo | Conteúdo |
|---|---|
| `index_comparison.png` | Min-Max e Rank Percentil sobrepostos |
| `components_minmax.png` | Componentes normalizados por Min-Max |
| `components_percentile.png` | Componentes normalizados por Rank Percentil |
| `index_minmax.png` | Índice Min-Max isolado |
| `index_percentile.png` | Índice Rank Percentil isolado |
| `index_comparison_base100.png` | Min-Max e Rank Percentil sobrepostos — base 100 |
| `index_minmax_base100.png` | Índice Min-Max isolado — base 100 |
| `index_percentile_base100.png` | Índice Rank Percentil isolado — base 100 |

`rolling/` — janela móvel 60m:

| Arquivo | Conteúdo |
|---|---|
| `index_comparison.png` | Min-Max e Rank Percentil sobrepostos |
| `components_minmax.png` | Componentes normalizados por Min-Max |
| `components_percentile.png` | Componentes normalizados por Rank Percentil |
| `index_minmax.png` | Índice Min-Max isolado |
| `index_percentile.png` | Índice Rank Percentil isolado |
| `index_comparison_base100.png` | Min-Max e Rank Percentil sobrepostos — base 100 |
| `index_minmax_base100.png` | Índice Min-Max isolado — base 100 |
| `index_percentile_base100.png` | Índice Rank Percentil isolado — base 100 |

## 8. Observações

- O índice não tem pretensão de precisão estrutural (não é modelo causal)
- O foco é **sinalização agregada e comunicação**
- Simplicidade e transparência são prioritárias sobre sofisticação desnecessária

## 9. Estrutura e Fontes de Dados

### 9.1. Fonte principal (construção do índice)

O arquivo **[`data/estatisticas-monetarias-e-de-credito/tabelas-estatisticas-monetarias-e-de-credito.xlsx`](data/estatisticas-monetarias-e-de-credito/tabelas-estatisticas-monetarias-e-de-credito.xlsx)** é a **fonte primária** para a construção do índice.

- Obtido em: [https://www.bcb.gov.br/estatisticas/estatisticasmonetariascredito](https://www.bcb.gov.br/estatisticas/estatisticasmonetariascredito)
- Trata-se de uma **compilação oficial do Banco Central do Brasil** de um subconjunto selecionado de séries temporais do Sistema Gerenciador de Séries Temporais (SGS).
- Reúne, em uma única planilha, as principais séries necessárias para o índice.
- As observações mais recentes são marcadas com `*` na planilha, indicando **dados preliminares** sujeitos a revisão. Essas observações são incluídas no índice sem tratamento especial.

**Identificação das séries dentro da planilha:** em cada aba, a **linha 7** contém o cabeçalho `SGS` com o número identificador de cada série no sistema SGS/BCB. Exemplo: a série **29034** está na célula **D7** da aba **`Tab 27`**.

### 9.2. Fontes auxiliares (conferência e metodologia)

As demais pastas em `data/` contêm dados obtidos **diretamente do SGS** ([https://www3.bcb.gov.br/sgspub](https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries)), série a série, e servem como **referência auxiliar**:

| Pasta | Finalidade |
|---|---|
| [`data/sgs-estatisticas-de-credito-endividamento-das-familias/`](data/sgs-estatisticas-de-credito-endividamento-das-familias/) | Dados brutos e documentação de metodologia da série de endividamento das famílias, obtidos diretamente da fonte (SGS/BCB) |

Estas pastas são úteis para:

1. **Conferência de consistência**: verificar se os dados da planilha principal estão alinhados com os dados brutos da fonte primária.
2. **Sanamento de dúvidas metodológicas**: cada pasta contém documentação sobre a construção das séries (ex.: `metodologia.md`), alterações metodológicas históricas e notas técnicas.
3. **Horizonte temporal estendido**: os dados do SGS podem cobrir períodos mais longos do que os disponíveis na planilha compilada.

---
