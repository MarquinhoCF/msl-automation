"""
Buscador para Crossref (API gratuita, sem chave).
Documentação: https://api.crossref.org/swagger-ui/index.html
Dica: informar e-mail no config activa a 'Polite Pool' (mais rápida e estável).
"""
import time
import requests

from .base import BaseSearcher, Article


class CrossrefSearcher(BaseSearcher):

    BASE_URL = "https://api.crossref.org/works"

    def buscar(self, search_string: dict, filtros: dict) -> list[Article]:
        email = self.config.get("email", "")
        headers = {}
        if email:
            headers["User-Agent"] = f"MSL-Automation/1.0 (mailto:{email})"

        artigos = []
        offset = 0
        max_results = filtros.get("max_results_por_string", 100)

        while offset < max_results:
            batch = min(20, max_results - offset)
            params = {
                "query": search_string["string"],
                "rows": batch,
                "offset": offset,
                "filter": (
                    f"from-pub-date:{filtros.get('ano_inicio', 2015)},"
                    f"until-pub-date:{filtros.get('ano_fim', 2025)}"
                ),
                "select": "title,author,published,abstract,DOI,URL,container-title,type,is-referenced-by-count",
            }

            try:
                resp = requests.get(self.BASE_URL, params=params, headers=headers, timeout=30)
                if resp.status_code == 429:
                    print("    ⚠  Rate limit Crossref. Aguardando 30s...")
                    time.sleep(30)
                    continue
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"    ✗  Erro Crossref: {e}")
                break

            items = resp.json().get("message", {}).get("items", [])
            if not items:
                break

            for item in items:
                titulo_raw = item.get("title", [])
                titulo = self._limpar_texto(titulo_raw[0] if titulo_raw else "")
                if not titulo:
                    continue

                autores_raw = item.get("author", [])
                autores = [
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in autores_raw
                ]

                pub = item.get("published", {})
                date_parts = pub.get("date-parts", [[None]])[0]
                ano = date_parts[0] if date_parts else None

                container = item.get("container-title", [])
                veiculo = container[0] if container else ""

                artigos.append(Article(
                    titulo=titulo,
                    autores=autores,
                    ano=ano,
                    resumo=self._limpar_texto(item.get("abstract", "")),
                    doi=item.get("DOI"),
                    url=item.get("URL"),
                    fonte="Crossref",
                    veiculo=self._limpar_texto(veiculo),
                    tipo_publicacao=item.get("type", "").lower(),
                    string_busca_id=search_string["id"],
                    citacoes=item.get("is-referenced-by-count"),
                ))

            offset += len(items)
            if len(items) < batch:
                break
            time.sleep(1)

        return artigos
