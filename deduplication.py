import re
from difflib import SequenceMatcher
from searchers.base import Article


def _normalizar(texto: str) -> str:
    """Remove pontuação, lowercase e espaços extras para comparação."""
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _similaridade(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def deduplicate(artigos: list[Article], threshold: float = 0.92) -> list[Article]:
    """
    Remove duplicatas baseando-se em:
    1. DOI idêntico (caso exista)
    2. Similaridade do título normalizado ≥ threshold

    Retorna lista sem duplicatas, mantendo o primeiro encontrado.
    """
    vistos_doi: set[str] = set()
    titulos_normalizados: list[str] = []
    unicos: list[Article] = []

    for art in artigos:
        # Deduplicação por DOI
        if art.doi:
            doi_clean = art.doi.strip().lower()
            if doi_clean in vistos_doi:
                continue
            vistos_doi.add(doi_clean)

        # Deduplicação por título
        titulo_norm = _normalizar(art.titulo)
        if not titulo_norm:
            unicos.append(art)
            continue

        duplicado = False
        for t in titulos_normalizados:
            if _similaridade(titulo_norm, t) >= threshold:
                duplicado = True
                break

        if not duplicado:
            titulos_normalizados.append(titulo_norm)
            unicos.append(art)

    return unicos


def aplicar_filtros(artigos: list[Article], filtros: dict) -> list[Article]:
    """
    Aplica filtros básicos automáticos (ano, idioma).
    Critérios de inclusão/exclusão são aplicados manualmente na planilha.
    """
    ano_inicio = filtros.get("ano_inicio", 2015)
    ano_fim = filtros.get("ano_fim", 2025)
    idiomas = [i.lower() for i in filtros.get("idiomas", [])]

    resultado = []
    for art in artigos:
        # Filtro de ano
        if art.ano is not None:
            if art.ano < ano_inicio or art.ano > ano_fim:
                continue
        # Filtro de idioma (quando disponível)
        if idiomas and art.idioma:
            if art.idioma.lower() not in idiomas:
                continue
        resultado.append(art)

    return resultado
