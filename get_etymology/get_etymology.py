"""Wikipedia won't lie!"""

import requests
from bs4 import BeautifulSoup
import urllib
import logging

log = logging.getLogger(__name__)

def wiktionary_url(word: str) -> str:
    word = urllib.parse.quote(word.encode('utf-8'))
    return f"https://ru.wiktionary.org/wiki/{word}"

def scrap_wiktionary(word: str) -> str | None:
    page = requests.get(wiktionary_url(word))
    if page.status_code != 200:
        log.error(f'Error {page.status_code}')
        return
    soup = BeautifulSoup(page.text, "html.parser")
    etymology = soup.find(id="Этимология").find_next('p').text
    return etymology

def main() -> None:
    etymology = scrap_wiktionary(input())
    print(etymology)

if __name__ == '__main__':
    main()