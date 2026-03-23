import json
import sys
from bs4 import BeautifulSoup
import requests

def clean_src(url):
    """Remove query parameters from image URL."""
    if '?' in url:
        return url.split('?')[0]
    return url

def extract_song_info(item):
    """Extract song data from a <section class="Music__item"> element."""
    # Jacket image
    img = item.find('img', class_='Music__item__thumb')
    jacket = img['src'] if img else ''

    # Song name
    name_tag = item.find('h3', class_='Music__item__title')
    name_span = name_tag.find('span') if name_tag else None
    name = name_span.text.strip() if name_span else ''

    # Unit
    unit_tag = item.find('p', class_='Music__item__unit')
    unit = unit_tag.text.strip() if unit_tag else ''

    # Credits: lyrics, music, arrangement
    lyrics = music = arrangement = ''
    creator_blocks = item.find_all('p', class_='Music__item__creator')
    for block in creator_blocks:
        label_span = block.find('span', class_='Music__item__label')
        value_span = block.find('span', class_='Music__item__value')
        if not label_span or not value_span:
            continue
        label = label_span.text.strip().rstrip(':')
        value = value_span.text.strip()
        if 'Lyrics' in label:
            lyrics = value
        elif 'Music' in label:
            music = value
        elif 'Arrangement' in label:
            arrangement = value

    return {
        'jacket': jacket,
        'name': name,
        'unit': unit,
        'lyrics': lyrics,
        'music': music,
        'arrangement': arrangement
    }

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    categories = soup.find_all('article', class_='Music__category')
    songs = []

    for cat in categories:
        # Determine category type (original / cover)
        title_tag = cat.find('h3', class_='Music__category__title')
        cat_name = title_tag.text.strip() if title_tag else ''
        # Assume "Original Songs" or "Cover Songs" – use as is for output
        cat_type = 'original' if 'Original' in cat_name else 'cover' if 'Cover' in cat_name else cat_name

        items = cat.find_all('section', class_='Music__item')
        for item in items:
            song = extract_song_info(item)
            song['type'] = cat_type
            songs.append(song)

    return songs

def main():
    x = requests.get('https://www.hololive-dreams.com/en/music')
    x = x.content
    songs = parse_html(x)
    output = {
        'total': len(songs),
        'songs': songs
    }
    outputdtb = json.dumps(output, indent=2, ensure_ascii=False)
    with open("output.json", "a") as f:
      f.write(outputdtb)

if __name__ == '__main__':
    main()
