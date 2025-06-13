import os, sys, gc, logging, requests
from typing import TypedDict, List

from dotenv import load_dotenv
from langchain_google_community import GoogleSearchAPIWrapper
from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    CacheMode,
)
from crawl4ai.async_logger import AsyncLogger, LogLevel


# Logging --------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)



load_dotenv()

class WebFinder:
    def url_finder(self, query: str, num_results: int = 5):
        try:
            return GoogleSearchAPIWrapper().results(query, num_results=num_results)
        except Exception as e:
            log.error(f"Error en búsqueda de Google: {e}")
            return []

    async def crawl_urls(self, urls: list[str]):
        # Crear logger completamente silencioso
        quiet_logger = AsyncLogger(
            verbose=False,
            log_level=LogLevel.CRITICAL   
        )        
        # Configuración para evitar cachés y logs
        cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS, 
            stream=False,
            verbose=False,
            log_console=False
        )
        
        gc.collect()
        out: list[str] = []
        
        try:
            # Redirigir stdout temporalmente para capturar cualquier output
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            # Crear un buffer silencioso
            from io import StringIO
            devnull = StringIO()
            sys.stdout = devnull
            sys.stderr = devnull
            
            async with AsyncWebCrawler(
                logger=quiet_logger,
                verbose=False,
                headless=True
            ) as crawler:
                results = await crawler.arun_many(urls, config=cfg)
                for r in results:
                    if r.success and r.markdown:
                        # Limpiar el markdown de caracteres problemáticos
                        clean_markdown = r.markdown.replace('\x00', '').strip()
                        if clean_markdown:
                            out.append(clean_markdown)
                    
        except Exception as e:
            log.error(f"Error en crawling: {e}")
        finally:
            # Restaurar stdout/stderr
            sys.stdout = original_stdout  
            sys.stderr = original_stderr
            gc.collect()
        
        return out

    async def find_and_crawl(self, query: str, num_results: int = 5):
        search_results = self.url_finder(query, num_results)
        urls = [r["link"] for r in search_results if "link" in r]
        if not urls:
            return []
        return await self.crawl_urls(urls)

if __name__ == "__main__":
    import asyncio
    
    async def test_search():
        finder = WebFinder()
        results = await finder.find_and_crawl("Python programming", num_results=2)
        print("\nResultados encontrados:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Resultado {i} ---")
            print(result[:500] + "..." if len(result) > 500 else result)
    
    asyncio.run(test_search())
    
    
    