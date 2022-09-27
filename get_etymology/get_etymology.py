"""Wikipedia won't lie!"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import urllib
import logging

import platform
if platform.system()=='Windows': # i hate windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)

async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    log.info(f"Fetching from {url}")
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()
    
def wiktionary_url(word: str) -> str:
    word = urllib.parse.quote(word.encode('utf-8'))
    return f"https://ru.wiktionary.org/wiki/{word}"

def get_etymology_on_wiktionary_page(page: str) -> str:
    soup = BeautifulSoup(page, "html.parser")
    etymology = soup.find(id="Этимология").find_next('p').text
    return etymology

async def get_etymology(session: aiohttp.ClientSession, word: str) -> str:
    url = wiktionary_url(word)
    try:
        page = await fetch(session, url)
    except (aiohttp.ClientError) as exc:
        log.error(f'Cannot get word {word} from Wiktionary: Error {exc.status}')
        return ''
    else:
        log.info(f'Got etymology for {word}')
        etymology = get_etymology_on_wiktionary_page(page)
        print(f'*Этимология слова {word}.*', etymology)
        return etymology

async def scrap(words: list[str]) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [get_etymology(session, word) for word in words]
        return await asyncio.gather(*tasks)

def main() -> None:
    asyncio.run(scrap(input().split()))

if __name__ == '__main__':
    main()