"""
Buscador para Semantic Scholar.
Sem chave → endpoint padrão (100 resultados/req, 1 req/s).
Com chave gratuita → endpoint bulk (até 10k resultados).
Cadastre sua chave em: https://www.semanticscholar.org/product/api
"""
import time
import requests
from .base import BaseSearcher, Article

class SemanticScholarSearcher(BaseSearcher):
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    BULK_URL = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    FIELDS   = "title,authors,year,abstract,externalIds,url,venue,publicationTypes,openAccessPdf,citationCount"

    def buscar(self, search_string, filtros):
        api_key = self.config.get("api_key")
        headers = {"User-Agent": "MSL-Automation/1.0"}
        if api_key:
            headers["x-api-key"] = api_key
            return self._bulk(search_string, filtros, headers)
        return self._padrao(search_string, filtros, headers)

    def _padrao(self, ss, filtros, headers):
        artigos, offset = [], 0
        max_r = min(filtros.get("max_results_por_string", 100), 100)
        while offset < max_r:
            batch  = min(100, max_r - offset)
            params = {"query": ss["string"], "fields": self.FIELDS, "limit": batch, "offset": offset}
            resp   = self._get(self.BASE_URL, params, headers)
            if resp is None: break
            papers = resp.json().get("data", [])
            if not papers: break
            for p in papers:
                art = self._parse(p, ss["id"], filtros)
                if art: artigos.append(art)
            offset += len(papers)
            if len(papers) < batch: break
            time.sleep(1)
        return artigos

    def _bulk(self, ss, filtros, headers):
        artigos, token = [], None
        max_r = filtros.get("max_results_por_string", 100)
        while len(artigos) < max_r:
            params = {"query": ss["string"], "fields": self.FIELDS, "limit": min(1000, max_r - len(artigos))}
            if token: params["token"] = token
            resp = self._get(self.BULK_URL, params, headers)
            if resp is None: break
            data   = resp.json()
            papers = data.get("data", [])
            token  = data.get("token")
            for p in papers:
                art = self._parse(p, ss["id"], filtros)
                if art: artigos.append(art)
            if not token or not papers: break
            time.sleep(1)
        return artigos

    def _get(self, url, params, headers):
        for t in range(3):
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=30)
                if resp.status_code == 429:
                    espera = 60 * (t + 1)
                    print(f"\n    ⚠  Rate limit S2. Aguardando {espera}s...")
                    time.sleep(espera); continue
                if resp.status_code in (401, 403):
                    print(f"\n    ⚠  Semantic Scholar acesso negado ({resp.status_code}). "
                          "Configure api_key gratuita em config.py")
                    return None
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                print(f"\n    ✗  Erro S2 (tentativa {t+1}): {e}")
                time.sleep(5)
        return None

    def _parse(self, p, ss_id, filtros):
        ano = p.get("year")
        if ano:
            if ano < filtros.get("ano_inicio", 2000): return None
            if ano > filtros.get("ano_fim", 2099):    return None
        autores  = [a.get("name","") for a in (p.get("authors") or [])]
        ids      = p.get("externalIds") or {}
        doi      = ids.get("DOI")
        pdf      = (p.get("openAccessPdf") or {}).get("url")
        url      = p.get("url") or pdf or f"https://www.semanticscholar.org/paper/{p.get('paperId','')}"
        tipos    = p.get("publicationTypes") or []
        tipo     = tipos[0].lower() if tipos else "unknown"
        return Article(
            titulo=self._limpar_texto(p.get("title")), autores=autores, ano=ano,
            resumo=self._limpar_texto(p.get("abstract")), doi=doi, url=url,
            fonte="Semantic Scholar", veiculo=self._limpar_texto(p.get("venue")),
            tipo_publicacao=tipo, string_busca_id=ss_id, citacoes=p.get("citationCount"),
        )
