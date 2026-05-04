# =============================================================================
# CONFIGURAÇÃO DO MAPEAMENTO SISTEMÁTICO DA LITERATURA (MSL)
# =============================================================================
# Baseado no artigo: "Entrega de Última Milha sob Incerteza: Simulação e
# Solução com Aprendizado por Reforço e Heurísticas" (SBPO 2026)
#
# ⚙️  Configurações sensíveis (chaves de API, e-mail) ficam no arquivo .env.
#     Copie .env.example → .env e preencha antes de executar.
#     Todas as demais configurações podem ser editadas diretamente aqui.
# =============================================================================

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega o .env do mesmo diretório deste arquivo (ou de qualquer pai)
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)


def _bool(key: str, default: bool = False) -> bool:
    """Lê variável de ambiente como booleano (true/false, 1/0, yes/no)."""
    val = os.getenv(key, str(default)).strip().lower()
    return val in ("true", "1", "yes", "on")


def _int(key: str, default: int) -> int:
    """Lê variável de ambiente como inteiro."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def _str(key: str, default: str = "") -> str:
    """Lê variável de ambiente como string; retorna None se vazia."""
    val = os.getenv(key, default).strip()
    return val if val else None


# ---------------------------------------------------------------------------
# CONTEXTO DA DISSERTAÇÃO
# (Não sensível — edite aqui mesmo)
# ---------------------------------------------------------------------------
DISSERTATION = {
    "titulo": "Aprendizado por Reforço aplicado ao Roteamento Dinâmico de Veículos na Entrega de Última Milha",
    "objetivo_geral": (
        "Investigar sistematicamente o uso de técnicas de Aprendizado por Reforço "
        "no problema de Entrega de Última Milha (especialmente variantes dinâmicas "
        "e estocásticas do VRP), comparando com abordagens heurísticas e metaheurísticas."
    ),
    "hipotese": (
        "Agentes de Aprendizado por Reforço Profundo, especialmente algoritmos Policy "
        "Gradient como PPO e SAC, superam heurísticas clássicas em cenários de alta "
        "demanda e incerteza estocástica no contexto de entrega de última milha."
    ),
}

# ---------------------------------------------------------------------------
# QUESTÕES DE PESQUISA
# (Não sensível — edite aqui mesmo)
# ---------------------------------------------------------------------------
RESEARCH_QUESTIONS = [
    {
        "id": "RQ1",
        "questao": "Quais algoritmos de Aprendizado por Reforço têm sido aplicados ao problema de Roteamento Dinâmico de Veículos (DVRP)?",
    },
    {
        "id": "RQ2",
        "questao": "Como o problema de Entrega de Última Milha tem sido formalizado como Processo de Decisão de Markov na literatura?",
    },
    {
        "id": "RQ3",
        "questao": "Quais métricas de desempenho são utilizadas para comparar agentes de AR com heurísticas em problemas de roteamento?",
    },
    {
        "id": "RQ4",
        "questao": "Quais são as abordagens de simulação utilizadas como ambiente de treinamento para agentes de AR em problemas logísticos?",
    },
    {
        "id": "RQ5",
        "questao": "Quais são os principais desafios e limitações reportados na aplicação de AR a problemas de DVRP/PDP estocástico?",
    },
]

# ---------------------------------------------------------------------------
# STRINGS DE BUSCA
# (Não sensível — edite aqui mesmo)
# ---------------------------------------------------------------------------
SEARCH_STRINGS = [
    {
        "id": "SS1",
        "descricao": "AR + Roteamento Dinâmico de Veículos",
        "string": (
            '("reinforcement learning" OR "deep reinforcement learning") '
            'AND ("dynamic vehicle routing" OR "DVRP" OR "vehicle routing problem")'
        ),
    },
    {
        "id": "SS2",
        "descricao": "AR + Entrega de Última Milha",
        "string": (
            '("reinforcement learning" OR "deep reinforcement learning") '
            'AND ("last-mile delivery" OR "last mile delivery" OR "last-mile logistics")'
        ),
    },
    {
        "id": "SS3",
        "descricao": "PPO/Policy Gradient + Logística/Roteamento",
        "string": (
            '("proximal policy optimization" OR "PPO" OR "policy gradient" OR "actor-critic") '
            'AND ("vehicle routing" OR "logistics" OR "delivery" OR "dispatching")'
        ),
    },
    {
        "id": "SS4",
        "descricao": "MDP + Logística/Roteamento",
        "string": (
            '("Markov decision process" OR "MDP") '
            'AND ("vehicle routing" OR "last-mile" OR "order dispatching" OR "driver allocation")'
        ),
    },
    {
        "id": "SS5",
        "descricao": "DVRP Estocástico + Inteligência Artificial",
        "string": (
            '("stochastic dynamic vehicle routing" OR "SDVRP") '
            'AND ("machine learning" OR "reinforcement learning" OR "artificial intelligence")'
        ),
    },
    {
        "id": "SS6",
        "descricao": "Pickup and Delivery + AR",
        "string": (
            '("pickup and delivery" OR "PDP") '
            'AND ("reinforcement learning" OR "deep reinforcement learning")'
        ),
    },
    {
        "id": "SS7",
        "descricao": "Despacho de pedidos + AR Profundo",
        "string": (
            '("order dispatching" OR "ride dispatching" OR "driver dispatching") '
            'AND ("deep reinforcement learning" OR "DQN" OR "PPO" OR "DDQN")'
        ),
    },
    {
        "id": "SS8",
        "descricao": "Simulação de Eventos Discretos + AR + Logística",
        "string": (
            '("discrete event simulation" OR "simulation environment") '
            'AND ("reinforcement learning") '
            'AND ("logistics" OR "delivery" OR "routing")'
        ),
    },
]

# ---------------------------------------------------------------------------
# CRITÉRIOS DE INCLUSÃO, EXCLUSÃO E QUALIDADE
# (Não sensível — edite aqui mesmo)
# ---------------------------------------------------------------------------
INCLUSION_CRITERIA = [
    "IC1: O estudo aborda Aprendizado por Reforço (clássico ou profundo) aplicado a problemas de roteamento de veículos ou logística de entrega.",
    "IC2: O problema envolve decisões dinâmicas ou estocásticas (demanda dinâmica, chegada estocástica de pedidos).",
    "IC3: É um estudo primário (artigo de conferência, periódico ou preprint com contribuição original).",
    "IC4: O estudo foi publicado entre 2015 e 2025.",
    "IC5: Está escrito em inglês ou português.",
]

EXCLUSION_CRITERIA = [
    "EC1: Estudo duplicado ou versão mais antiga de outro estudo já incluído.",
    "EC2: Não é estudo primário (ex.: prefácio, editorial, MSL/RSL, livro didático).",
    "EC3: Aborda exclusivamente VRP estático sem componente dinâmico/estocástico.",
    "EC4: Usa apenas heurísticas clássicas sem componente de aprendizado de máquina.",
    "EC5: Fora do idioma inglês ou português.",
    "EC6: Texto completo não disponível.",
    "EC7: Publicado antes de 2015.",
]

QUALITY_CRITERIA = [
    "QC1: O estudo apresenta formalização clara do problema (ex.: como PDM/MDP).",
    "QC2: O estudo realiza comparação experimental com baseline (heurística ou outro algoritmo).",
    "QC3: O estudo reporta métricas quantitativas de desempenho (ex.: tempo de entrega, distância, custo).",
    "QC4: O ambiente/simulador utilizado é descrito com detalhes suficientes para reprodutibilidade.",
]

# ---------------------------------------------------------------------------
# FILTROS  (valores-padrão sobrescritos pelo .env)
# ---------------------------------------------------------------------------
FILTERS = {
    "ano_inicio":               2015,
    "ano_fim":                  2025,
    "idiomas":                  ["en", "pt"],
    "max_results_por_string":   100,
    "tipos_publicacao": [
        "journal article",
        "conference paper",
        "preprint",
        "book chapter",
    ],
    "campos_busca": ["title", "abstract", "keywords"],
}

# ---------------------------------------------------------------------------
# BASES DE DADOS  (chaves de API e flags lidas do .env)
# ---------------------------------------------------------------------------
DATABASES = {
    "semantic_scholar": {
        "ativo":        _bool("SEMANTIC_SCHOLAR_ATIVO", True),
        "nome_display": "Semantic Scholar",
        "api_key":      _str("SEMANTIC_SCHOLAR_API_KEY"),   # opcional
        "max_results":  _int("SEMANTIC_SCHOLAR_MAX_RESULTS", 100),
    },
    "arxiv": {
        "ativo":        _bool("ARXIV_ATIVO", True),
        "nome_display": "arXiv",
        "api_key":      None,                               # não requer chave
        "max_results":  _int("ARXIV_MAX_RESULTS", 100),
    },
    "ieee": {
        "ativo":        _bool("IEEE_ATIVO", False),
        "nome_display": "IEEE Xplore",
        "api_key":      _str("IEEE_API_KEY"),               # obrigatória se ativo=true
        "max_results":  _int("IEEE_MAX_RESULTS", 200),
    },
    "scopus": {
        "ativo":        _bool("SCOPUS_ATIVO", False),
        "nome_display": "Scopus",
        "api_key":      _str("SCOPUS_API_KEY"),             # obrigatória se ativo=true
        "max_results":  _int("SCOPUS_MAX_RESULTS", 200),
    },
    "springer": { # Springer precisa de acesso Premium para buscas via API
        "ativo":        _bool("SPRINGER_ATIVO", False),
        "nome_display": "Springer",
        "api_key":      _str("SPRINGER_API_KEY"),           # obrigatória se ativo=true
        "max_results":  _int("SPRINGER_MAX_RESULTS", 200),
    },
    "crossref": {
        "ativo":        _bool("CROSSREF_ATIVO", True),
        "nome_display": "Crossref",
        "api_key":      None,                               # não requer chave
        "max_results":  _int("CROSSREF_MAX_RESULTS", 100),
        "email":        _str("CROSSREF_EMAIL"),             # recomendado (Polite Pool)
    },
}

# ---------------------------------------------------------------------------
# SAÍDA
# ---------------------------------------------------------------------------
OUTPUT = {
    "diretorio":       os.getenv("OUTPUT_DIRETORIO", "results"),
    "prefixo_arquivo": os.getenv("OUTPUT_PREFIXO", "msl_ultima_milha"),
    "formato_excel":   _bool("OUTPUT_FORMATO_EXCEL", True),
    "formato_csv":     _bool("OUTPUT_FORMATO_CSV", True),
    "log_detalhado":   _bool("OUTPUT_LOG_DETALHADO", True),
}

# ---------------------------------------------------------------------------
# Validação rápida na inicialização
# ---------------------------------------------------------------------------
def _validar():
    avisos = []
    if DATABASES["ieee"]["ativo"] and not DATABASES["ieee"]["api_key"]:
        avisos.append("⚠  IEEE_ATIVO=true mas IEEE_API_KEY não está definida no .env")
    if DATABASES["scopus"]["ativo"] and not DATABASES["scopus"]["api_key"]:
        avisos.append("⚠  SCOPUS_ATIVO=true mas SCOPUS_API_KEY não está definida no .env")
    if DATABASES["crossref"]["ativo"] and not DATABASES["crossref"]["email"]:
        avisos.append("ℹ  CROSSREF_EMAIL não definido — buscas usarão a fila padrão (mais lenta)")
    for msg in avisos:
        print(msg)

_validar()