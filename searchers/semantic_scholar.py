"""
Buscador para Semantic Scholar.
Sem chave → endpoint padrão (100 resultados/req, 1 req/s).
Com chave gratuita → endpoint bulk (até 10k resultados).
Cadastre sua chave em: https://www.semanticscholar.org/product/api

NOTA: A API do S2 NÃO suporta operadores booleanos (AND/OR/parênteses).
      Este módulo expande automaticamente queries complexas em combinações
      simples e deduplica os resultados pelo paperId.
"""
import re
import time
import itertools
import requests
from .base import BaseSearcher, Article

class SemanticScholarSearcher(BaseSearcher):
    BASE_URL     = "https://api.semanticscholar.org/graph/v1/paper/search"
    BULK_URL     = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    FIELDS       = "title,authors,year,abstract,externalIds,url,venue,publicationTypes,openAccessPdf,citationCount"
    MIN_INTERVAL = 1.05   # segundos entre requisições (margem sobre o limite de 1 req/s)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ultimo_request = 0.0

    def buscar(self, search_string, filtros):
        api_key = self.config.get("api_key")
        headers = {"User-Agent": "MSL-Automation/1.0"}
        if api_key:
            headers["x-api-key"] = api_key

        sub_queries = self._expandir_query(search_string["string"])
        print(f"\n    ℹ  Query expandida em {len(sub_queries)} sub-query(ies) para S2.")

        vistos  = {}          # paperId → Article  (deduplicação)
        metodo  = self._bulk if api_key else self._padrao

        for sq in sub_queries:
            ss_parcial = {"id": search_string["id"], "string": sq}
            for art in metodo(ss_parcial, filtros, headers):
                chave = art.doi or art.titulo or ""
                if chave and chave not in vistos:
                    vistos[chave] = art

        return list(vistos.values())

    def _expandir_query(self, query: str, max_sub_queries: int = 50) -> list[str]:
        """
        Expande query booleana em sub-queries simples para a API do S2.

        Estratégia "âncora + variações" (crescimento linear):
        - Âncora: primeira opção de cada grupo → 1 query
        - Para cada grupo, varia suas opções mantendo os demais na âncora

        Exemplo com 3 grupos [A1,A2], [B1,B2,B3], [C1,C2]:
        Âncora:  A1 B1 C1
        Var G1:  A2 B1 C1
        Var G2:  A1 B2 C1 | A1 B3 C1
        Var G3:  A1 B1 C2
        Total: 6 queries  (vs 12 no produto cartesiano)

        Se mesmo assim ultrapassar max_sub_queries, trunca com aviso.
        """
        grupos = re.findall(r'\(([^)]+)\)', query)

        if not grupos:
            limpa = re.sub(r'\b(AND|OR|NOT)\b', '', query).strip()
            return [limpa] if limpa else [query]

        # Cada grupo → lista de termos
        opcoes = []
        for grupo in grupos:
            termos = [t.strip() for t in re.split(r'\bOR\b', grupo) if t.strip()]
            opcoes.append(termos)

        ancora = [termos[0] for termos in opcoes]   # primeiro termo de cada grupo

        queries = set()
        queries.add(' '.join(ancora))               # query âncora

        for i, termos in enumerate(opcoes):
            for termo in termos[1:]:                # pula o [0], já está na âncora
                variacao = ancora.copy()
                variacao[i] = termo
                queries.add(' '.join(variacao))

        queries = list(queries)

        if len(queries) > max_sub_queries:
            print(f"\n    ⚠  {len(queries)} sub-queries geradas; truncando para {max_sub_queries}.")
            queries = queries[:max_sub_queries]

        return queries

    def _padrao(self, ss, filtros, headers):
        artigos, offset = [], 0
        max_r = min(filtros.get("max_results_por_string", 100), 100)
        while offset < max_r:
            batch  = min(100, max_r - offset)
            params = {"query": ss["string"], "fields": self.FIELDS,
                      "limit": batch, "offset": offset}
            resp   = self._get(self.BASE_URL, params, headers)
            if resp is None:
                break
            papers = resp.json().get("data", [])
            if not papers:
                break
            for p in papers:
                art = self._parse(p, ss["id"], filtros)
                if art:
                    artigos.append(art)
            offset += len(papers)
            if len(papers) < batch:
                break
        return artigos

    def _bulk(self, ss, filtros, headers):
        artigos, token = [], None
        max_r = filtros.get("max_results_por_string", 100)
        while len(artigos) < max_r:
            params = {"query": ss["string"], "fields": self.FIELDS,
                      "limit": min(1000, max_r - len(artigos))}
            if token:
                params["token"] = token
            resp = self._get(self.BULK_URL, params, headers)
            if resp is None:
                break
            data   = resp.json()
            papers = data.get("data", [])
            token  = data.get("token")
            for p in papers:
                art = self._parse(p, ss["id"], filtros)
                if art:
                    artigos.append(art)
            if not token or not papers:
                break
        return artigos

    def _esperar_rate_limit(self):
        agora     = time.monotonic()
        decorrido = agora - self._ultimo_request
        if decorrido < self.MIN_INTERVAL:
            time.sleep(self.MIN_INTERVAL - decorrido)
        self._ultimo_request = time.monotonic()

    def _get(self, url, params, headers):
        for tentativa in range(3):
            self._esperar_rate_limit()
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=30)

                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 10 * (tentativa + 1)))
                    print(f"\n    ⚠  Rate limit S2. Aguardando {retry_after}s...")
                    time.sleep(retry_after)
                    continue

                if resp.status_code in (401, 403):
                    print(f"\n    ⚠  Semantic Scholar acesso negado ({resp.status_code}). "
                          "Verifique a api_key em config.py")
                    return None

                resp.raise_for_status()
                return resp

            except requests.RequestException as e:
                espera = 5 * (tentativa + 1)
                print(f"\n    ✗  Erro S2 (tentativa {tentativa + 1}): {e}. Aguardando {espera}s...")
                time.sleep(espera)

        return None

    def _parse(self, p, ss_id, filtros):
        ano = p.get("year")
        if ano:
            if ano < filtros.get("ano_inicio", 2000): return None
            if ano > filtros.get("ano_fim", 2099):    return None
        autores = [a.get("name", "") for a in (p.get("authors") or [])]
        ids     = p.get("externalIds") or {}
        doi     = ids.get("DOI")
        pdf     = (p.get("openAccessPdf") or {}).get("url")
        url     = p.get("url") or pdf or f"https://www.semanticscholar.org/paper/{p.get('paperId','')}"
        tipos   = p.get("publicationTypes") or []
        tipo    = tipos[0].lower() if tipos else "unknown"
        return Article(
            titulo=self._limpar_texto(p.get("title")), autores=autores, ano=ano,
            resumo=self._limpar_texto(p.get("abstract")), doi=doi, url=url,
            fonte="Semantic Scholar", veiculo=self._limpar_texto(p.get("venue")),
            tipo_publicacao=tipo, string_busca_id=ss_id, citacoes=p.get("citationCount"),
        )