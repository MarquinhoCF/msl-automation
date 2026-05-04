# 📚 MSL Automation — Entrega de Última Milha + Aprendizado por Reforço

Automação para o **Mapeamento Sistemático da Literatura (MSL)** da sua dissertação de mestrado, 
construída com base no artigo *"Entrega de Última Milha sob Incerteza"* (SBPO 2026).

---

## 🗂️ Estrutura do Projeto

```
msl_automation/
├── main.py                  ← Orquestrador principal (ponto de entrada)
├── config.py                ← Configurações: tema, strings, filtros, bases
├── deduplication.py         ← Deduplicação por DOI e similaridade de título
├── exporter.py              ← Exportação para Excel (MSL completo) e CSV
├── searchers/
│   ├── __init__.py
│   ├── base.py              ← Contrato base: Article + BaseSearcher
│   ├── semantic_scholar.py  ← Semantic Scholar (gratuito, sem chave)
│   ├── arxiv.py             ← arXiv (gratuito, sem chave)
│   ├── ieee.py              ← IEEE Xplore (requer chave gratuita)
│   ├── crossref.py          ← Crossref (gratuito, sem chave)
│   ├── scopus.py            ← Scopus (requer chave institucional CAPES)
│   └── springer.py          ← Springer (requer chave Premium)
├── results/                 ← Saídas geradas: Excel, CSV, JSON
├── logs/                    ← Log detalhado de cada execução
├── .env                     ← Chaves de API (NÃO versionar)
└── .env.example             ← Modelo do .env
```

---

## Instalação

1. Clone o repositório:

```bash
git clone git@github.com:MarquinhoCF/msl-automation.git
```

2. Crie um ambiente virtual (opcional, mas recomendado):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

3. Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

4. Configure as chaves de API no arquivo `.env` (copie o modelo `.env.example`):

```bash
cp .env.example .env
```

5. Edite o `.env` com suas chaves e preferências (veja detalhes abaixo).

```dotenv
# Semantic Scholar (opcional — sem chave o limite é menor)
SEMANTIC_SCHOLAR_API_KEY=

# IEEE Xplore (obrigatória para usar esta base)
# Obtenha em: https://developer.ieee.org/
IEEE_API_KEY=sua_chave_aqui
IEEE_ATIVO=true

# Scopus (requer acesso institucional UFLA/CAPES)
# Obtenha em: https://dev.elsevier.com/
SCOPUS_API_KEY=sua_chave_aqui
SCOPUS_ATIVO=true

# Springer (requer acesso Premium)
SPRINGER_API_KEY=sua_chave_aqui
SPRINGER_ATIVO=true

# Crossref — informe seu e-mail para entrar na "Polite Pool" (mais rápido)
CROSSREF_EMAIL=seu@email.com

# Diretório e prefixo dos arquivos de saída
OUTPUT_DIRETORIO=results
OUTPUT_PREFIXO=msl_ultima_milha
```

---

## 🔑 Onde obter chaves de API

| Base | Link | Observação |
|------|------|------------|
| **IEEE Xplore** | https://developer.ieee.org/ | Gratuito, 200 req/dia |
| **Scopus** | https://dev.elsevier.com/ | Requer acesso institucional (UFLA/CAPES) |
| **Springer** | https://dev.springernature.com/ | Requer acesso Premium |
| **Semantic Scholar** | https://www.semanticscholar.org/product/api | Opcional (melhora o rate limit) |
| **Crossref** | https://www.crossref.org/education/retrieve-metadata/rest-api/ | Gratuito, informe seu e-mail para melhor performance |

---

## 🚀 Como Usar

### Rodar tudo (bases ativas + todas as strings)
```bash
python main.py
```

### Testar sem fazer buscas reais
```bash
python main.py --dry-run
```

### Escolher bases específicas
```bash
python main.py --bases semantic_scholar arxiv crossref
```

### Escolher strings específicas
```bash
python main.py --strings SS1 SS2 SS3
```

### Combinar filtros
```bash
python main.py --bases semantic_scholar --strings SS1 SS4 SS7
```

---

## ⚙️ Configurando o `config.py`

Todas as configurações de conteúdo (não sensíveis) ficam em `config.py`. Você não precisa mexer no código dos buscadores para adaptar o MSL ao seu tema.

### 1. Contexto da dissertação

```python
DISSERTATION = {
    "titulo": "Seu título aqui",
    "objetivo_geral": "Descreva o objetivo...",
    "hipotese": "Enuncie a hipótese...",
}
```

### 2. Questões de pesquisa

Adicione ou edite entradas na lista `RESEARCH_QUESTIONS`:

```python
RESEARCH_QUESTIONS = [
    {
        "id": "RQ1",
        "questao": "Quais algoritmos de AR têm sido aplicados ao DVRP?",
    },
    # Adicione quantas RQs precisar
]
```

### 3. Strings de busca

Cada string é um dicionário com três chaves obrigatórias: `id`, `descricao` e `string`.

```python
SEARCH_STRINGS = [
    {
        "id": "SS1",
        "descricao": "AR + Roteamento Dinâmico de Veículos",
        "string": (
            '("reinforcement learning" OR "deep reinforcement learning") '
            'AND ("dynamic vehicle routing" OR "DVRP")'
        ),
    },
    # Adicione novas strings aqui
    {
        "id": "SS9",
        "descricao": "Meu novo tema",
        "string": '("meu termo A") AND ("meu termo B")',
    },
]
```

**Dicas para escrever boas strings de busca:**
- Use `OR` para sinônimos e variações do mesmo conceito: `"last-mile" OR "last mile"`
- Use `AND` para combinar conceitos distintos obrigatórios
- Use aspas para garantir que frases sejam buscadas literalmente
- Mantenha o campo `id` único (SS1, SS2, SS3...)

### 4. Filtros globais

```python
FILTERS = {
    "ano_inicio":             2015,     # Publicações a partir deste ano
    "ano_fim":                2025,     # Publicações até este ano
    "idiomas":                ["en", "pt"],
    "max_results_por_string": 100,      # Limite por combinação string/base
    "tipos_publicacao": [
        "journal article",
        "conference paper",
        "preprint",
        "book chapter",
    ],
    "campos_busca": ["title", "abstract", "keywords"],
}
```

### 5. Ativar e desativar bases

No `config.py`, o flag `ativo` de cada base pode ser definido diretamente ou via `.env`:

```python
DATABASES = {
    "semantic_scholar": {"ativo": True,  ...},   # Gratuito, sempre recomendado
    "arxiv":            {"ativo": True,  ...},   # Gratuito, sempre recomendado
    "crossref":         {"ativo": True,  ...},   # Gratuito, recomendado
    "ieee":             {"ativo": False, ...},   # Requer chave — ative via .env
    "scopus":           {"ativo": False, ...},   # Requer chave institucional
    "springer":         {"ativo": False, ...},   # Requer acesso Premium
}
```

Para ativar via `.env` sem editar o `config.py`:

```dotenv
IEEE_ATIVO=true
SCOPUS_ATIVO=true
```

### 6. Critérios de inclusão, exclusão e qualidade

Edite as listas diretamente no `config.py`. Elas são exportadas automaticamente para a aba **Protocolo MSL** do Excel:

```python
INCLUSION_CRITERIA = [
    "IC1: O estudo aborda Aprendizado por Reforço aplicado a roteamento...",
    "IC2: ...",
]

EXCLUSION_CRITERIA = [
    "EC1: Estudo duplicado...",
    "EC2: ...",
]

QUALITY_CRITERIA = [
    "QC1: O estudo apresenta formalização clara do problema...",
    "QC2: ...",
]
```

---

## 🔬 Desenvolvendo Novos Buscadores

Todos os buscadores herdam da classe `BaseSearcher` definida em `searchers/base.py`. Para adicionar suporte a uma nova base de dados, siga os passos abaixo.

### Passo 1 — Entenda o contrato base (`searchers/base.py`)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class Article:
    titulo: str
    autores: list[str]
    ano: Optional[int]
    resumo: str
    doi: Optional[str]
    url: Optional[str]
    fonte: str               # Nome da base (ex: "PubMed")
    veiculo: str             # Revista ou conferência
    tipo_publicacao: str     # "journal article", "conference paper", etc.
    string_busca_id: str     # ID da string que gerou este resultado
    palavras_chave: list[str]
    citacoes: Optional[int]
    idioma: Optional[str]
    # ... campos de triagem MSL preenchidos manualmente depois

class BaseSearcher(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.nome = config.get("nome_display", "Desconhecido")

    @abstractmethod
    def buscar(self, search_string: dict, filtros: dict) -> list[Article]:
        pass

    def _limpar_texto(self, texto: Optional[str]) -> str:
        if not texto:
            return ""
        return " ".join(str(texto).split())
```

**Seu buscador precisa:**
1. Herdar de `BaseSearcher`
2. Implementar o método `buscar(self, search_string, filtros) -> list[Article]`
3. Retornar uma lista de objetos `Article` (nunca dicts)

### Passo 2 — Crie o arquivo do buscador

Crie `searchers/meu_buscador.py`:

```python
import requests
from .base import BaseSearcher, Article

class MeuBuscador(BaseSearcher):
    BASE_URL = "https://api.minhabase.org/search"

    def buscar(self, search_string: dict, filtros: dict) -> list[Article]:
        artigos = []
        params = {
            "query":   search_string["string"],
            "from":    filtros["ano_inicio"],
            "until":   filtros["ano_fim"],
            "limit":   filtros["max_results_por_string"],
            "apikey":  self.config.get("api_key", ""),
        }

        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
        except requests.RequestException as e:
            print(f"  Erro na requisição: {e}")
            return []

        for item in dados.get("results", []):
            artigo = Article(
                titulo         = self._limpar_texto(item.get("title")),
                autores        = item.get("authors", []),
                ano            = item.get("year"),
                resumo         = self._limpar_texto(item.get("abstract")),
                doi            = item.get("doi"),
                url            = item.get("url"),
                fonte          = self.nome,
                veiculo        = item.get("venue", ""),
                tipo_publicacao= item.get("type", ""),
                string_busca_id= search_string["id"],
                palavras_chave = item.get("keywords", []),
                citacoes       = item.get("citation_count"),
                idioma         = item.get("language"),
            )
            artigos.append(artigo)

        return artigos
```

**Boas práticas:**
- Sempre use `self._limpar_texto()` para normalizar strings antes de preencher `Article`
- Trate todos os erros de rede com `try/except` e retorne `[]` em caso de falha
- Respeite o campo `filtros["max_results_por_string"]` para limitar os resultados
- Prefira `timeout=30` nas chamadas HTTP para evitar travamentos

### Passo 3 — Registre o buscador em dois lugares

**Em `searchers/__init__.py`**, exporte a nova classe:

```python
from .meu_buscador import MeuBuscador
```

**Em `main.py`**, adicione ao mapa de buscadores:

```python
from searchers import MeuBuscador   # adicione este import

SEARCHER_MAP = {
    "semantic_scholar": SemanticScholarSearcher,
    "arxiv":            ArxivSearcher,
    "ieee":             IEEESearcher,
    "crossref":         CrossrefSearcher,
    "scopus":           ScopusSearcher,
    "springer":         SpringerSearcher,
    "minha_base":       MeuBuscador,    # ← adicione aqui
}
```

### Passo 4 — Registre a base em `config.py`

```python
DATABASES = {
    # ... bases existentes ...
    "minha_base": {
        "ativo":        _bool("MINHA_BASE_ATIVO", False),
        "nome_display": "Minha Base",
        "api_key":      _str("MINHA_BASE_API_KEY"),
        "max_results":  _int("MINHA_BASE_MAX_RESULTS", 100),
    },
}
```

E no `.env`:

```dotenv
MINHA_BASE_ATIVO=true
MINHA_BASE_API_KEY=sua_chave
```

### Passo 5 — Teste com dry-run e depois com uma string

```bash
# Confira se o plano de execução inclui sua nova base
python main.py --dry-run --bases minha_base

# Execute somente com a SS1 para validar antes de rodar tudo
python main.py --bases minha_base --strings SS1
```

---

## 📊 Saída — Arquivo Excel

O Excel gerado em `results/` contém 4 abas:

| Aba | Conteúdo |
|-----|----------|
| Protocolo MSL | Tema, objetivo, hipótese, RQs, strings, critérios IC/EC/QC |
| Busca Bruta | Todos os artigos coletados, com duplicatas |
| Sem Duplicatas | Artigos deduplicados + colunas para triagem manual |
| Resumo | Contagens por base, por string e estatísticas gerais |

---

## Fluxo de Triagem MSL

```
1. Execute main.py
        ↓
2. Abra o Excel → aba "Sem Duplicatas"
   Preencha "Triagem Título/Resumo": Aceito / Rejeitado / Pendente
        ↓
3. Artigos Aceitos → leitura do texto completo
   Preencha "Triagem Texto Completo" + "Critério de Exclusão"
        ↓
4. Aceitos na etapa 3 → avaliação de qualidade
   Preencha QC1 – QC4
        ↓
5. Extraia dados para responder RQ1 – RQ5
```