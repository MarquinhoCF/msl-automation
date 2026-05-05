import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime

# Garante que o diretório raiz está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as cfg
from searchers import (
    SemanticScholarSearcher,
    ArxivSearcher,
    IEEESearcher,
    CrossrefSearcher,
    ScopusSearcher,
    SpringerSearcher
)
from searchers.base import Article
from deduplication import deduplicate, aplicar_filtros
from exporter import exportar_excel


# Mapeamento base_id -> classe
SEARCHER_MAP = {
    "semantic_scholar": SemanticScholarSearcher,
    "arxiv":            ArxivSearcher,
    "ieee":             IEEESearcher,
    "crossref":         CrossrefSearcher,
    "scopus":           ScopusSearcher,
    "springer":         SpringerSearcher, 
}

class Logger:
    def __init__(self, log_dir: str):
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(log_dir, f"msl_log_{ts}.txt")
        self._f = open(self.path, "w", encoding="utf-8")

    def log(self, msg: str):
        print(msg)
        self._f.write(msg + "\n")
        self._f.flush()

    def close(self):
        self._f.close()


# Funções auxiliares

def salvar_csv(artigos: list[Article], caminho: str):
    if not artigos:
        return
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=artigos[0].to_dict().keys())
        writer.writeheader()
        for art in artigos:
            writer.writerow(art.to_dict())


def salvar_json(artigos: list[Article], caminho: str):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump([art.to_dict() for art in artigos], f, ensure_ascii=False, indent=2)


def barra_progresso(atual: int, total: int, label: str = "", largura: int = 40):
    pct = atual / total if total else 0
    preenchido = int(largura * pct)
    barra = "█" * preenchido + "░" * (largura - preenchido)
    print(f"\r  [{barra}] {atual}/{total} {label}", end="", flush=True)

def main():
    parser = argparse.ArgumentParser(
        description="MSL Automation — Entrega de Última Milha + AR"
    )
    parser.add_argument(
        "--bases", nargs="+", default=None,
        help="Bases a usar (ex: semantic_scholar arxiv ieee crossref scopus). "
             "Padrão: todas as ativas em config.py"
    )
    parser.add_argument(
        "--strings", nargs="+", default=None,
        help="IDs das strings de busca a usar (ex: SS1 SS3). Padrão: todas."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Exibe o plano de execução sem realizar buscas."
    )
    parser.add_argument(
        "--no-dedup", action="store_true",
        help="Pula a etapa de deduplicação."
    )
    args = parser.parse_args()

    os.makedirs(cfg.OUTPUT["diretorio"], exist_ok=True)
    logger = Logger("logs")
    inicio = datetime.now()

    logger.log("=" * 70)
    logger.log("  MSL AUTOMATION - Entrega de Última Milha + Aprendizado por Reforço")
    logger.log(f"  Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}")
    logger.log("=" * 70)

    # Valida seleção de bases
    bases_selecionadas = args.bases or [
        k for k, v in cfg.DATABASES.items() if v.get("ativo", False)
    ]
    bases_invalidas = [b for b in bases_selecionadas if b not in cfg.DATABASES]
    if bases_invalidas:
        logger.log(f"\n Bases inválidas: {bases_invalidas}")
        logger.log(f"  Opções válidas: {list(cfg.DATABASES.keys())}")
        sys.exit(1)

    # Seleção das strings de busca
    strings_disponiveis = {ss["id"]: ss for ss in cfg.SEARCH_STRINGS}
    strings_selecionadas_ids = args.strings or list(strings_disponiveis.keys())
    strings_selecionadas = [strings_disponiveis[sid] for sid in strings_selecionadas_ids
                            if sid in strings_disponiveis]

    # Log do plano de execução
    total_buscas = len(bases_selecionadas) * len(strings_selecionadas)
    logger.log(f"\n  PLANO DE EXECUÇÃO")
    logger.log(f"   Bases ativas  : {', '.join(bases_selecionadas)}")
    logger.log(f"   Strings       : {', '.join(strings_selecionadas_ids)}")
    logger.log(f"   Total de buscas: {total_buscas}")
    logger.log(f"   Filtros       : {cfg.FILTERS['ano_inicio']}-{cfg.FILTERS['ano_fim']}, "
               f"max {cfg.FILTERS['max_results_por_string']} por string/base")
    logger.log("")

    if args.dry_run:
        logger.log("  Modo DRY-RUN - nenhuma busca foi realizada.")
        logger.log("\nStrings que seriam buscadas:")
        for ss in strings_selecionadas:
            logger.log(f"\n  [{ss['id']}] {ss['descricao']}")
            logger.log(f"  -> {ss['string']}")
        logger.close()
        return

    # Execução das buscas
    todos_artigos: list[Article] = []
    busca_num = 0

    for base_id in bases_selecionadas:
        base_cfg = cfg.DATABASES[base_id]
        SearcherClass = SEARCHER_MAP.get(base_id)
        if not SearcherClass:
            logger.log(f"\n⚠  Buscador para '{base_id}' não implementado — ignorando.")
            continue

        searcher = SearcherClass(base_cfg)
        logger.log(f"\n{'─'*60}")
        logger.log(f"  BASE: {base_cfg['nome_display']}")
        logger.log(f"{'─'*60}")

        for ss in strings_selecionadas:
            busca_num += 1
            logger.log(f"\n  [{busca_num}/{total_buscas}] {ss['id']} — {ss['descricao']}")
            logger.log(f"  String: {ss['string'][:80]}{'...' if len(ss['string']) > 80 else ''}")

            try:
                t0 = time.time()
                resultados = searcher.buscar(ss, cfg.FILTERS)
                elapsed = time.time() - t0
                logger.log(f"  ✓ {len(resultados)} artigos encontrados ({elapsed:.1f}s)")
                todos_artigos.extend(resultados)
            except Exception as e:
                logger.log(f"  ✗ Erro inesperado: {e}")
                import traceback
                traceback.print_exc()

    # Filtragem e deduplicação
    logger.log(f"\n{'='*60}")
    logger.log(f"  PÓS-PROCESSAMENTO")
    logger.log(f"{'='*60}")
    logger.log(f"  Total bruto: {len(todos_artigos)} artigos")

    artigos_filtrados = aplicar_filtros(todos_artigos, cfg.FILTERS)
    logger.log(f"  Após filtros de ano/idioma: {len(artigos_filtrados)}")

    if args.no_dedup:
        artigos_finais = artigos_filtrados
        logger.log("  Deduplicação: IGNORADA (--no-dedup)")
    else:
        artigos_finais = deduplicate(artigos_filtrados)
        removidos = len(artigos_filtrados) - len(artigos_finais)
        logger.log(f"  Após deduplicação: {len(artigos_finais)} artigos "
                   f"({removidos} duplicatas removidas)")

    # Exportar resultados
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefixo = cfg.OUTPUT["prefixo_arquivo"]
    dir_out = cfg.OUTPUT["diretorio"]

    logger.log(f"\n{'='*60}")
    logger.log(f"  EXPORTANDO RESULTADOS")
    logger.log(f"{'='*60}")

    # Excel
    if cfg.OUTPUT.get("formato_excel", True):
        caminho_xlsx = os.path.join(dir_out, f"{prefixo}_{ts}.xlsx")
        config_dict = {
            "DISSERTATION": cfg.DISSERTATION,
            "RESEARCH_QUESTIONS": cfg.RESEARCH_QUESTIONS,
            "SEARCH_STRINGS": cfg.SEARCH_STRINGS,
            "INCLUSION_CRITERIA": cfg.INCLUSION_CRITERIA,
            "EXCLUSION_CRITERIA": cfg.EXCLUSION_CRITERIA,
            "QUALITY_CRITERIA": cfg.QUALITY_CRITERIA,
        }
        try:
            exportar_excel(
                artigos_brutos=todos_artigos,
                artigos_dedup=artigos_finais,
                config_dict=config_dict,
                caminho_saida=caminho_xlsx,
            )
        except Exception as e:
            logger.log(f"  ✗ Erro ao exportar Excel: {e}")
            import traceback; traceback.print_exc()

    # CSV (backup)
    if cfg.OUTPUT.get("formato_csv", True):
        caminho_csv = os.path.join(dir_out, f"{prefixo}_{ts}.csv")
        salvar_csv(artigos_finais, caminho_csv)
        logger.log(f"    CSV salvo em: {caminho_csv}")

    # JSON (backup completo)
    caminho_json = os.path.join(dir_out, f"{prefixo}_{ts}_bruto.json")
    salvar_json(todos_artigos, caminho_json)
    logger.log(f"    JSON bruto salvo em: {caminho_json}")

    # Relatório final
    fim = datetime.now()
    duracao = (fim - inicio).seconds
    logger.log(f"\n{'='*60}")
    logger.log(f"    CONCLUÍDO em {duracao//60}min {duracao%60}s")
    logger.log(f"  Artigos para triagem: {len(artigos_finais)}")
    logger.log(f"{'='*60}")
    logger.close()


if __name__ == "__main__":
    main()
