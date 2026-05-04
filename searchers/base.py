"""
Classe base para todos os buscadores de bases de dados.
Cada buscador específico herda desta classe.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Article:
    """Representa um artigo retornado por qualquer base de dados."""
    titulo: str
    autores: list[str]
    ano: Optional[int]
    resumo: str
    doi: Optional[str]
    url: Optional[str]
    fonte: str                      # Nome da base de dados
    veiculo: str                    # Revista / Conferência
    tipo_publicacao: str            # journal, conference, preprint, etc.
    string_busca_id: str            # ID da string que retornou este artigo
    palavras_chave: list[str] = field(default_factory=list)
    citacoes: Optional[int] = None
    idioma: Optional[str] = None

    # Campos do MSL preenchidos manualmente depois
    triagem_titulo_resumo: str = "Pendente"   # Aceito / Rejeitado / Pendente
    justificativa_triagem: str = ""
    triagem_texto_completo: str = "Pendente"
    justificativa_texto_completo: str = ""
    criterio_exclusao: str = ""
    qc1: str = ""
    qc2: str = ""
    qc3: str = ""
    qc4: str = ""
    notas: str = ""

    def to_dict(self) -> dict:
        return {
            "Título": self.titulo,
            "Autores": "; ".join(self.autores) if self.autores else "",
            "Ano": self.ano,
            "Resumo": self.resumo,
            "DOI": self.doi or "",
            "URL": self.url or "",
            "Fonte (Base)": self.fonte,
            "Veículo": self.veiculo,
            "Tipo": self.tipo_publicacao,
            "String de Busca": self.string_busca_id,
            "Palavras-chave": "; ".join(self.palavras_chave),
            "Citações": self.citacoes,
            "Idioma": self.idioma or "",
            "Triagem Título/Resumo": self.triagem_titulo_resumo,
            "Justificativa Triagem": self.justificativa_triagem,
            "Triagem Texto Completo": self.triagem_texto_completo,
            "Justificativa Texto Completo": self.justificativa_texto_completo,
            "Critério de Exclusão": self.criterio_exclusao,
            "QC1 - Formalização": self.qc1,
            "QC2 - Comparação Experimental": self.qc2,
            "QC3 - Métricas Quantitativas": self.qc3,
            "QC4 - Reprodutibilidade": self.qc4,
            "Notas": self.notas,
        }


class BaseSearcher(ABC):
    """Interface comum para todos os buscadores."""

    def __init__(self, config: dict):
        self.config = config
        self.nome = config.get("nome_display", "Desconhecido")

    @abstractmethod
    def buscar(self, search_string: dict, filtros: dict) -> list[Article]:
        """
        Realiza a busca na base de dados.

        Args:
            search_string: dict com 'id', 'descricao' e 'string'
            filtros: dict com ano_inicio, ano_fim, max_results_por_string, etc.

        Returns:
            Lista de Article
        """
        pass

    def _limpar_texto(self, texto: Optional[str]) -> str:
        if not texto:
            return ""
        return " ".join(str(texto).split())
