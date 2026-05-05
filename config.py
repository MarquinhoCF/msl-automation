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
# STRINGS DE BUSCA  — baseadas na metodologia Kitchenham (quasi-gold standard)
# (Não sensível — edite aqui mesmo)
#
# QUASI-GOLD STANDARD (artigos que TODA string deve recuperar):
#   - Konovalenko & Hvattum (2024) — DVRP + PPO
#   - Kavuk et al. (2022)          — despacho ultrarrápido + DRL
#   - Hildebrandt et al. (2023)    — revisão SDVRP + RL
#   - Zou et al. (2022)            — entrega de comida + DDQN
#   - Wang et al. (2018)           — alocação de motoristas + DRL
#   - Joe & Lau (2020)             — DVRP + DRL + clientes estocásticos
#   - Turan et al. (2020)          — mobilidade urbana + PPO
#
# MAPEAMENTO POR BASE:
#   SS1  → Scopus, Web of Science  (string completa — 4 blocos AND)
#   SS2  → Crossref, Semantic Scholar  (sensível — 2 blocos AND, ampla cobertura)
#   SS3  → Scopus/WoS alternativa balanceada  (3 blocos AND)
#   SS4  → IEEE Xplore, ACM DL  (foco DVRP + RL)
#   SS5  → IEEE Xplore, ACM DL  (foco despacho/alocação + RL — complementar a SS4)
#   SS6  → Semantic Scholar, arXiv  (foco PPO/Policy Gradient + logística)
#   SS7  → Todas as bases  (Pickup and Delivery + RL)
#   SS8  → Todas as bases  (simulação de eventos discretos + RL + logística)
# ---------------------------------------------------------------------------
SEARCH_STRINGS = [
    # ------------------------------------------------------------------
    # SS1 — String COMPLETA (4 blocos AND)
    # Indicada para: Scopus, Web of Science
    # Balanceia todos os conceitos do trabalho; valide com o quasi-gold standard
    # ------------------------------------------------------------------
    {
        "id": "SS1",
        "descricao": "String completa — Última Milha + RL + Roteamento/Despacho + Estocástico",
        "string": (
            '("last-mile delivery" OR "last mile delivery" OR "last-mile logistics" '
            'OR "final mile delivery" OR "food delivery") '
            'AND ("reinforcement learning" OR "deep reinforcement learning" '
            'OR "proximal policy optimization" OR "PPO" OR "policy gradient" '
            'OR "deep Q-learning" OR "DQN" OR "Markov decision process" OR "MDP") '
            'AND ("vehicle routing" OR "dynamic vehicle routing" OR "DVRP" '
            'OR "driver allocation" OR "order dispatching" OR "delivery dispatching" '
            'OR "rider assignment" OR "courier allocation") '
            'AND ("stochastic" OR "stochastic demand" OR "dynamic" OR "uncertainty")'
        ),
    },

    # ------------------------------------------------------------------
    # SS2 — String SENSÍVEL / ampla (2 blocos AND)
    # Indicada para: Crossref, Semantic Scholar (bases sem suporte a queries longas)
    # Alta revocação, menor precisão — complementa SS1
    # ------------------------------------------------------------------
    {
        "id": "SS2",
        "descricao": "Sensível — Última Milha + RL (2 blocos AND)",
        "string": (
            '("last-mile delivery" OR "last mile delivery" OR "final mile delivery" '
            'OR "food delivery logistics") '
            'AND ("reinforcement learning" OR "deep reinforcement learning" '
            'OR "proximal policy optimization")'
        ),
    },

    # ------------------------------------------------------------------
    # SS3 — String BALANCEADA (3 blocos AND)
    # Indicada para: Scopus/WoS como alternativa à SS1; Springer Nature
    # ------------------------------------------------------------------
    {
        "id": "SS3",
        "descricao": "Balanceada — Última Milha + RL + Roteamento/Despacho (3 blocos AND)",
        "string": (
            '("last-mile delivery" OR "last mile delivery" OR "food delivery logistics") '
            'AND ("reinforcement learning" OR "deep reinforcement learning" '
            'OR "Markov decision process") '
            'AND ("vehicle routing" OR "driver allocation" OR "order dispatching")'
        ),
    },

    # ------------------------------------------------------------------
    # SS4 — Foco em DVRP + RL
    # Indicada para: IEEE Xplore, ACM Digital Library
    # ------------------------------------------------------------------
    {
        "id": "SS4",
        "descricao": "DVRP Estocástico + RL (IEEE/ACM)",
        "string": (
            '("dynamic vehicle routing" OR "DVRP" OR "stochastic vehicle routing" '
            'OR "stochastic dynamic vehicle routing" OR "SDVRP") '
            'AND ("reinforcement learning" OR "deep reinforcement learning" '
            'OR "proximal policy optimization" OR "PPO")'
        ),
    },

    # ------------------------------------------------------------------
    # SS5 — Foco em Despacho/Alocação + RL (complementar a SS4)
    # Indicada para: IEEE Xplore, ACM Digital Library
    # ------------------------------------------------------------------
    {
        "id": "SS5",
        "descricao": "Despacho/Alocação de motoristas + RL (IEEE/ACM)",
        "string": (
            '("order dispatching" OR "driver allocation" OR "rider assignment" '
            'OR "delivery dispatching" OR "courier allocation") '
            'AND ("reinforcement learning" OR "deep reinforcement learning" '
            'OR "Markov decision process") '
            'AND ("stochastic" OR "dynamic")'
        ),
    },

    # ------------------------------------------------------------------
    # SS6 — Foco em PPO / Policy Gradient + Logística
    # Indicada para: Semantic Scholar, arXiv (forte cobertura de preprints DRL)
    # ------------------------------------------------------------------
    {
        "id": "SS6",
        "descricao": "PPO/Policy Gradient + Logística/Roteamento",
        "string": (
            '("proximal policy optimization" OR "PPO" OR "policy gradient" '
            'OR "actor-critic" OR "SAC" OR "soft actor-critic") '
            'AND ("vehicle routing" OR "logistics" OR "delivery" OR "dispatching" '
            'OR "last-mile")'
        ),
    },

    # ------------------------------------------------------------------
    # SS7 — Pickup and Delivery + RL
    # Indicada para: todas as bases
    # Cobre a dimensão PDP do trabalho, frequentemente indexada separadamente
    # ------------------------------------------------------------------
    {
        "id": "SS7",
        "descricao": "Pickup and Delivery Problem + RL",
        "string": (
            '("pickup and delivery" OR "pickup-and-delivery" OR "PDP") '
            'AND ("reinforcement learning" OR "deep reinforcement learning" '
            'OR "Markov decision process")'
        ),
    },

    # ------------------------------------------------------------------
    # SS8 — Simulação de Eventos Discretos + RL + Logística
    # Indicada para: todas as bases
    # Cobre a contribuição metodológica do simulador do trabalho
    # ------------------------------------------------------------------
    {
        "id": "SS8",
        "descricao": "Simulação de Eventos Discretos + RL + Logística",
        "string": (
            '("discrete event simulation" OR "simulation environment" OR "SimPy") '
            'AND ("reinforcement learning") '
            'AND ("logistics" OR "delivery" OR "routing" OR "vehicle routing")'
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