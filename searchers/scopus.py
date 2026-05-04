"""
Buscador para Scopus (requer chave de API — acesso institucional CAPES).
Cadastro: https://dev.elsevier.com/
Documentação: https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl

ATENÇÃO: Acesse preferencialmente dentro da rede da sua universidade (VPN ou
laboratório) para que a chave institucional funcione corretamente.
"""
import time
import requests

from .base import BaseSearcher, Article


class ScopusSearcher(BaseSearcher):

    BASE_URL = "https://api.elsevier.com/content/search/scopus"

    def buscar(self, search_string: dict, filtros: dict) -> list[Article]:
        api_key = self.config.get("api_key", "")
        if not api_key or api_key == "SUA_CHAVE_SCOPUS_AQUI":
            print("    ⚠  Scopus: chave de API não configurada em config.py → ignorando.")
            return []

        headers = {
            "X-ELS-APIKey": api_key,
            "Accept": "application/json",
        }

        artigos = []
        start = 0
        max_results = filtros.get("max_results_por_string", 200)

        # Scopus usa sintaxe própria: TITLE-ABS-KEY(...)
        scopus_query = self._adaptar_query(
            search_string["string"],
            filtros.get("ano_inicio", 2015),
            filtros.get("ano_fim", 2025),
        )

        while start < max_results:
            batch = min(25, max_results - start)
            params = {
                "query": scopus_query,
                "start": start,
                "count": batch,
                "field": "dc:title,dc:creator,prism:coverDate,dc:description,"
                         "prism:doi,prism:url,prism:publicationName,subtypeDescription,"
                         "authkeywords,citedby-count",
            }

            try:
                resp = requests.get(self.BASE_URL, params=params, headers=headers, timeout=30)
                if resp.status_code == 429:
                    print("    ⚠  Rate limit Scopus. Aguardando 30s...")
                    time.sleep(30)
                    continue
                if resp.status_code == 401:
                    print("    ✗  Scopus: chave de API inválida ou sem acesso institucional.")
                    break
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"    ✗  Erro Scopus: {e}")
                break

            entries = (
                resp.json()
                .get("search-results", {})
                .get("entry", [])
            )
            if not entries:
                break

            for e in entries:
                data_raw = e.get("prism:coverDate", "")
                try:
                    ano = int(data_raw[:4]) if data_raw else None
                except ValueError:
                    ano = None

                if ano:
                    if ano < filtros.get("ano_inicio", 2000):
                        continue
                    if ano > filtros.get("ano_fim", 2099):
                        continue

                kw_raw = e.get("authkeywords", "") or ""
                kws = [k.strip() for k in kw_raw.split("|") if k.strip()]

                artigos.append(Article(
                    titulo=self._limpar_texto(e.get("dc:title")),
                    autores=[self._limpar_texto(e.get("dc:creator"))],
                    ano=ano,
                    resumo=self._limpar_texto(e.get("dc:description")),
                    doi=e.get("prism:doi"),
                    url=e.get("prism:url"),
                    fonte="Scopus",
                    veiculo=self._limpar_texto(e.get("prism:publicationName")),
                    tipo_publicacao=self._limpar_texto(e.get("subtypeDescription")).lower(),
                    string_busca_id=search_string["id"],
                    palavras_chave=kws,
                    citacoes=e.get("citedby-count"),
                ))

            start += len(entries)
            if len(entries) < batch:
                break
            time.sleep(1)

        return artigos

    def _adaptar_query(self, string: str, ano_inicio: int, ano_fim: int) -> str:
        """Envolve a string em TITLE-ABS-KEY e adiciona filtro de data."""
        inner = string.replace('"', '"').replace('"', '"')
        return (
            f"TITLE-ABS-KEY({inner}) "
            f"AND PUBYEAR > {ano_inicio - 1} AND PUBYEAR < {ano_fim + 1}"
        )
