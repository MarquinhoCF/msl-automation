"""
Buscador para IEEE Xplore (requer chave de API gratuita).
Cadastro: https://developer.ieee.org/
Documentação: https://developer.ieee.org/docs/read/IEEE_Xplore_API_Overview
"""
import time
import requests

from .base import BaseSearcher, Article


class IEEESearcher(BaseSearcher):

    BASE_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

    def buscar(self, search_string: dict, filtros: dict) -> list[Article]:
        api_key = self.config.get("api_key", "")
        if not api_key or api_key == "SUA_CHAVE_IEEE_AQUI":
            print("    ⚠  IEEE Xplore: chave de API não configurada em config.py → ignorando.")
            return []

        artigos = []
        start = 1
        max_results = filtros.get("max_results_por_string", 200)

        while start <= max_results:
            batch = min(25, max_results - start + 1)
            params = {
                "apikey": api_key,
                "querytext": search_string["string"],
                "start_record": start,
                "max_records": batch,
                "start_year": filtros.get("ano_inicio", 2015),
                "end_year": filtros.get("ano_fim", 2025),
                "format": "json",
                "sortfield": "relevance",
                "sortorder": "desc",
            }

            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=30)
                if resp.status_code == 429:
                    print("    ⚠  Rate limit IEEE. Aguardando 30s...")
                    time.sleep(30)
                    continue
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"    ✗  Erro IEEE Xplore: {e}")
                break

            data = resp.json()
            articles = data.get("articles", [])
            if not articles:
                break

            for a in articles:
                autores_raw = a.get("authors", {}).get("authors", []) or []
                autores = [au.get("full_name", "") for au in autores_raw]

                kw_raw = a.get("index_terms", {})
                kws = []
                for src in kw_raw.values():
                    kws.extend(src.get("terms", []))

                ano_str = str(a.get("publication_year", "") or "")
                try:
                    ano = int(ano_str)
                except ValueError:
                    ano = None

                artigos.append(Article(
                    titulo=self._limpar_texto(a.get("title")),
                    autores=autores,
                    ano=ano,
                    resumo=self._limpar_texto(a.get("abstract")),
                    doi=a.get("doi"),
                    url=a.get("html_url") or a.get("pdf_url"),
                    fonte="IEEE Xplore",
                    veiculo=self._limpar_texto(a.get("publication_title")),
                    tipo_publicacao=a.get("content_type", "").lower(),
                    string_busca_id=search_string["id"],
                    palavras_chave=kws,
                    citacoes=a.get("citing_paper_count"),
                ))

            start += len(articles)
            if len(articles) < batch:
                break
            time.sleep(1)

        return artigos
