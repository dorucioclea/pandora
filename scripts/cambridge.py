#!/usr/bin/env python

import sys
import requests
import json
from bs4 import BeautifulSoup
from models import Term, File
import utils
from utils import is_empty

NAME = 'cambridge'

headers = {
    'User-Agent': utils.CHROME_USER_AGENT,
    'Accept': 'text/html',
}


def stripped_text(node):
    if node is None:
        return None
    return node.get_text().strip()


def find_strip(container, tag, class_):
    node = container.find(tag, class_=class_)
    return stripped_text(node)


base = 'https://dictionary.cambridge.org'


def get_translations(data, text, src_lang):
    # TODO fix dictionary map for all languages
    dmap = {
        'ru': 'english-russian',
        'fr': 'english-french',
        'de': 'english-german',
    }

    txt = text.replace(' ', '-')
    for lang, dictionary in dmap.items():
        url = f'{base}/dictionary/{dictionary}/{txt}'

        resp = requests.get(url, headers=headers)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        for sense in soup.find_all('div', class_='sense-body'):
            phrase = sense.find('div', class_='phrase-block')
            if phrase: continue
            trans = sense.find('span', class_='trans')
            if trans:
                words = stripped_text(trans).split(',')
                words = [w for w in words if not is_empty(w)]
                for word in words:
                    term = Term(text=word, lang=lang, region=None)
                    data['translated_as'].append(term)

    return data


def get_data(text, lang):
    if lang != 'en':
        return None

    txt = text.replace(' ', '-')
    url = f'{base}/dictionary/english/{txt}'

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    data = {
        'audio': [],
        'visual': [],
        'tag': [],
        'transcription': [],
        'definition': [],
        'in': [],
        'collocation': [],
        'translated_as': [],
    }
    codes = {
        'C': 'countable',
        'U': 'uncountable',
        'S': 'singular',
    }
    posgram_found = False
    gram_found = False

    if utils.is_word(text):
        data['tag'].append(Term(text='word', lang=lang, region=None))

    soup = BeautifulSoup(resp.text, 'html.parser')
    page = soup.find('div', class_='page')
    for dictionary in page.find_all('div', class_='dictionary'):
        header = dictionary.find('div', class_='pos-header')
        body = dictionary.find('div', class_='pos-body')

        posgram = header.find('div', class_='posgram')
        if posgram and not posgram_found:
            pos = find_strip(posgram, 'span', class_='pos')
            term = Term(text=pos, lang=lang, region=None)
            data['tag'].append(term)
            posgram_found = True
        if not gram_found:
            for gram in body.find_all('span', class_='gram'):
                for gc in gram.find_all('span', class_='gc'):
                    code = stripped_text(gc)
                    if code in codes and not gram_found:
                        term = Term(text=codes[code], lang=lang, region=None)
                        data['tag'].append(term)
                        gram_found = True

        # parse pronunciations
        for dpron in header.find_all('span', class_='dpron-i'):
            region = find_strip(dpron, 'span', 'region')
            amp = header.find('amp-audio')
            for source in amp.find_all('source'):
                file = File(url=base + source.attrs['src'], region=region)
                data['audio'].append(file)

            ipa = find_strip(dpron, 'span', class_='ipa')
            if not is_empty(ipa):
                data['transcription'].append(
                    Term(text=ipa, lang=lang, region=region))

        for dblock in body.find_all('div', class_='def-block'):
            def_text = stripped_text(dblock.find('div', class_='def'))
            if not is_empty(def_text):
                data['definition'].append(
                    Term(text=def_text, lang=lang, region=None))
            img = dblock.find('amp-img')
            if img is not None:
                file = File(url=base + img.attrs['src'], region=None)
                data['visual'].append(file)
            for eg in dblock.find_all('span', 'eg'):
                term = Term(text=stripped_text(eg), lang=lang, region=None)
                data['in'].append(term)

    for dataset in page.find_all('div', class_='dataset'):
        for eg in dataset.find_all('span', class_='deg'):
            term = Term(text=stripped_text(eg), lang=lang, region=None)
            data['in'].append(term)
        cpegs = dataset.find('div', class_='cpegs')
        if cpegs:
            for lbb in cpegs.find_all('div', class_='lbb'):
                for a in lbb.find_all('a', class_='hdib'):
                    term = Term(text=stripped_text(a), lang=lang, region=None)
                    data['collocation'].append(term)

    get_translations(data, text, lang)

    return data


def find_audio(text, lang):
    data = get_data(text, lang)
    if data is None:
        return None
    return [a._asdict() for a in data['audio']]


def main():
    (text, lang) = utils.find_audio_args(sys.argv)
    result = get_data(text, lang)
    print(json.dumps(result, sort_keys=True, indent='  ', ensure_ascii=False))


if __name__ == '__main__':
    main()
