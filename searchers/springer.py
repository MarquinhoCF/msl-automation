"""
Buscador para Springer Nature — Meta API v2 (gratuita com chave).
Cadastro e chave gratuita: https://dev.springernature.com/
Documentação: https://dev.springernature.com/docs/api-endpoints/meta-api/
"""
import time
import requests

from .base import BaseSearcher, Article


class SpringerSearcher(BaseSearcher):

    BASE_URL = "https://api.springernature.com/meta/v2/json"

    def buscar(self, search_string: dict, filtros: dict) -> list[Article]:
        api_key = self.config.get("api_key", "")
        if not api_key:
            print("    ⚠  Springer Nature: API key não configurada (SPRINGER_API_KEY no .env) → ignorando.")
            return []

        artigos: list[Article] = []
        start = 1  # Springer usa índice 1-based
        max_results = min(
            filtros.get("max_results_por_string", 100),
            self.config.get("max_results", 200),
        )

        # A API v2 aceita filtro de ano diretamente na query
        query = self._montar_query(
            search_string["string"],
            filtros.get("ano_inicio", 2015),
            filtros.get("ano_fim", 2025),
        )

        while start <= max_results:
            batch = min(50, max_results - start + 1)
            params = {
                "q": query,
                "s": start,
                "p": batch,
                "api_key": api_key,
            }

            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=30)
                if resp.status_code == 429:
                    print("    ⚠  Rate limit Springer. Aguardando 30s...")
                    time.sleep(30)
                    continue
                if resp.status_code in (401, 403):
                    print(f"    ✗  Springer: chave de API inválida ou sem acesso ({resp.status_code}).")
                    break
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"    ✗  Erro Springer Nature: {e}")
                break

            data = resp.json()
            records = data.get("records", [])
            if not records:
                break

            # Checar total disponível na primeira página
            result_meta = data.get("result", [{}])
            total_disponivel = int(result_meta[0].get("total", 0)) if result_meta else 0

            for rec in records:
                art = self._parse_record(rec, search_string["id"], filtros)
                if art:
                    artigos.append(art)

            start += len(records)

            # Parar se já buscamos tudo disponível
            if start > total_disponivel or len(records) < batch:
                break

            time.sleep(1)

        return artigos

    # ── helpers ──────────────────────────────────────────────────────────────

    def _montar_query(self, string: str, ano_inicio: int, ano_fim: int) -> str:
        """
        Springer Meta API v2 aceita operadores booleanos AND/OR e
        qualificadores de campo (keyword:, title:, doi:, year:).
        Aqui inserimos o filtro de ano diretamente na query.
        """
        # Normaliza aspas tipográficas → aspas retas
        q = string.replace("\u201c", '"').replace("\u201d", '"')
        return f"({q}) AND year:{ano_inicio}-{ano_fim}"

    def _parse_record(self, rec: dict, ss_id: str, filtros: dict) -> Article | None:
        # ── Ano ──
        pub_date = rec.get("publicationDate") or rec.get("coverDate") or ""
        ano = None
        if pub_date:
            try:
                ano = int(pub_date[:4])
            except (ValueError, IndexError):
                pass

        # Pós-filtragem de ano (segurança extra)
        if ano:
            if ano < filtros.get("ano_inicio", 2000):
                return None
            if ano > filtros.get("ano_fim", 2099):
                return None

        # ── Título ──
        titulo = self._limpar_texto(rec.get("title"))
        if not titulo:
            return None

        # ── Autores ──
        # Formato: [{"creator": "Sobrenome, N."}, ...]
        autores = [
            self._limpar_texto(c.get("creator", ""))
            for c in rec.get("creators", [])
            if c.get("creator")
        ]

        # ── DOI / URL ──
        doi = rec.get("doi") or self._doi_from_identifier(rec.get("identifier", ""))
        urls = rec.get("url", [])
        url = urls[0].get("value", "") if urls else (
            f"https://doi.org/{doi}" if doi else ""
        )

        # ── Veículo / tipo ──
        veiculo = self._limpar_texto(rec.get("publicationName"))
        content_type = (rec.get("contentType") or "article").lower()

        # ── Palavras-chave ──
        kws: list[str] = []
        raw_kw = rec.get("keyword", [])
        if isinstance(raw_kw, list):
            kws = [k for k in raw_kw if k]
        elif isinstance(raw_kw, str) and raw_kw:
            kws = [kw.strip() for kw in raw_kw.split(",") if kw.strip()]

        return Article(
            titulo=titulo,
            autores=autores,
            ano=ano,
            resumo=self._limpar_texto(rec.get("abstract")),
            doi=doi,
            url=url,
            fonte="Springer Nature",
            veiculo=veiculo,
            tipo_publicacao=content_type,
            string_busca_id=ss_id,
            palavras_chave=kws,
            idioma=rec.get("language"),
        )

    @staticmethod
    def _doi_from_identifier(identifier: str) -> str | None:
        """Extrai DOI do campo 'identifier' que vem no formato 'doi:10.xxxx/...'."""
        if identifier.startswith("doi:"):
            return identifier[4:]
        return None