"""Wikipedia won't lie!"""

import asyncio
import logging
import pathlib
import platform
import urllib

import aiofiles
import aiohttp
import regex
from bs4 import BeautifulSoup

if platform.system() == 'Windows':  # i hate windows
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
    word = urllib.parse.quote(word.lower().encode('utf-8'))
    return f"https://ru.wiktionary.org/wiki/{word}"


def parse_etymology(page: str) -> str:
    soup = BeautifulSoup(page, "html.parser")

    language = soup.find(id="Русский")
    if not language:
        return ''
    
    text: list[str] = []
    
    tags = language.find_all_next()
    for tag in tags:
        
        if tag.name == 'h1':
            break
        
        if tag.name == 'h3' and tag.find(id=regex.compile("^Этимология")):
            text_begins = True
            for text_tag in tag.find_next_siblings():
                if text_tag.name in ['p', 'ul']:
                    text.append(f"{'-' if text_begins else ''} {text_tag.text}")
                    text_begins = False
                else:
                    break
    
    return ''.join(text)


async def write_to_file(word: str, etymology: str):
    async with aiofiles.open(pathlib.Path(__file__).parent/'scrappedetymologies.md', 'a', encoding='utf-8') as outp:
        log.info(f'Writing {word} etymology to file')
        await outp.write(f'## Этимология слова {word}\n{etymology}\n')


async def get_etymology(session: aiohttp.ClientSession, word: str) -> None:
    url = wiktionary_url(word)
    try:
        page = await fetch(session, url)
    except aiohttp.ClientError as exc:
        log.error(f'Cannot get word {word} from Wiktionary: Error {exc.status}')
    except Exception as exc:
        log.error(f'Unexpected error when processing {word}: {exc}')
    else:
        log.info(f'Getting etymology for {word}')
        etymology = parse_etymology(page)
        if etymology:
            await write_to_file(word, etymology)


async def scrap(words: set[str]) -> list:
    async with aiohttp.ClientSession() as session:
        log.info(f'Scraping {words}')
        tasks = set(get_etymology(session, word) for word in words)
        return await asyncio.gather(*tasks)


def read_words(filename='input.md') -> set[str]:
    words: set[str] = set()
    with open(pathlib.Path(__file__).parent/filename, 'r', encoding='utf8') as inp:
        for line in inp:
            words_ = regex.findall(r'\p{L}+', line)
            words.update(words_)
    return words


if __name__ == '__main__':
    asyncio.run(scrap(read_words('input.md')))
