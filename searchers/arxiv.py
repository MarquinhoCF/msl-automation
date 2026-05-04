"""
Buscador para arXiv (API gratuita, sem autenticação).
Documentação: https://arxiv.org/help/api/
"""
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from .base import BaseSearcher, Article

NS = "http://www.w3.org/2005/Atom"


class ArxivSearcher(BaseSearcher):

    BASE_URL = "http://export.arxiv.org/api/query"

    def buscar(self, search_string: dict, filtros: dict) -> list[Article]:
        artigos = []
        start = 0
        max_results = filtros.get("max_results_por_string", 100)

        # arXiv usa sintaxe própria; ajusta a string para all: (all fields)
        query = self._adaptar_query(search_string["string"])

        while start < max_results:
            batch = min(50, max_results - start)
            params = {
                "search_query": query,
                "start": start,
                "max_results": batch,
                "sortBy": "relevance",
                "sortOrder": "descending",
            }

            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=30)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"    ✗  Erro arXiv: {e}")
                break

            root = ET.fromstring(resp.content)
            entries = root.findall(f"{{{NS}}}entry")
            if not entries:
                break

            for entry in entries:
                ano = self._extrair_ano(entry)
                if ano:
                    if ano < filtros.get("ano_inicio", 2000):
                        continue
                    if ano > filtros.get("ano_fim", 2099):
                        continue

                titulo = (entry.findtext(f"{{{NS}}}title") or "").strip().replace("\n", " ")
                resumo = (entry.findtext(f"{{{NS}}}summary") or "").strip().replace("\n", " ")
                url = entry.findtext(f"{{{NS}}}id") or ""
                doi_tag = entry.find(f"{{{NS}}}doi")
                doi = doi_tag.text if doi_tag is not None else None

                autores = [
                    (a.findtext(f"{{{NS}}}name") or "")
                    for a in entry.findall(f"{{{NS}}}author")
                ]

                cats = [
                    c.get("term", "")
                    for c in entry.findall(f"{{{NS}}}category")
                ]

                artigos.append(Article(
                    titulo=titulo,
                    autores=autores,
                    ano=ano,
                    resumo=resumo,
                    doi=doi,
                    url=url,
                    fonte="arXiv",
                    veiculo="arXiv preprint",
                    tipo_publicacao="preprint",
                    string_busca_id=search_string["id"],
                    palavras_chave=cats,
                ))

            start += len(entries)
            if len(entries) < batch:
                break
            time.sleep(3)  # arXiv pede pelo menos 3s entre requisições

        return artigos

    def _adaptar_query(self, string: str) -> str:
        """Converte string booleana genérica para sintaxe arXiv."""
        # arXiv: all:"frase" para busca no título+resumo+tudo
        # Remove aspas duplas extras e adapta
        query = string.replace('"', '"').replace('"', '"')
        # Troca termos de campo genéricos por 'all:'
        # A API do arXiv aceita AND/OR diretamente
        return f"all:{query}"

    def _extrair_ano(self, entry) -> int | None:
        published = entry.findtext(f"{{{NS}}}published") or ""
        if published:
            try:
                return datetime.fromisoformat(published[:10]).year
            except ValueError:
                pass
        return None
