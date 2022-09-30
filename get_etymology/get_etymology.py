"""Wikipedia won't lie!"""

import asyncio
import aiofiles
import aiohttp
import urllib
from bs4 import BeautifulSoup
import logging
import pathlib

import platform
if platform.system()=='Windows': # i hate windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG,
                    datefmt='%d-%m-%Y %H:%M:%S')
log = logging.getLogger(__name__)

async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    log.info(f"Fetching from {url}")
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()
    
def wiktionary_url(word: str) -> str:
    word = urllib.parse.quote(word.encode('utf-8')).lower()
    return f"https://ru.wiktionary.org/wiki/{word}"

def get_etymology_on_wiktionary_page(page: str) -> str:
    soup = BeautifulSoup(page, "html.parser")
    etymology = soup.find(id="Этимология").find_next('p').text
    return etymology

async def write_to_file(word: str, etymology: str):
    async with aiofiles.open(pathlib.Path(__file__).parent/'outp.md', 'a', encoding='utf-8') as outp:
        log.info(f'Writing {word} etymology to file')
        await outp.write(f'*Этимология слова {word}.*\n{etymology}\n')

async def get_etymology(session: aiohttp.ClientSession, word: str) -> None:
    url = wiktionary_url(word)
    try:
        page = await fetch(session, url)
    except (aiohttp.ClientError) as exc:
        log.error(f'Cannot get word {word} from Wiktionary: Error {exc.status}')
    else:
        log.info(f'Getting etymology for {word}')
        etymology = get_etymology_on_wiktionary_page(page)
        await write_to_file(word, etymology)

async def scrap(words: set[str]) -> list:
    async with aiohttp.ClientSession() as session:
        log.info(f'Scraping {words}')
        tasks = set(get_etymology(session, word) for word in words)
        return await asyncio.gather(*tasks)

def get_words() -> set[str]:
    words: set[str] = set()
    with open(pathlib.Path(__file__).parent/'inp.md', 'r', encoding='utf8') as inp:
        for line in inp:
            words.update(word for word in line.split())
    return words

if __name__ == '__main__':
    asyncio.run(scrap(get_words()))