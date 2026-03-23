import json
import sys
import requests
from bs4 import BeautifulSoup

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
        title_tag = cat.find('h3', class_='Music__category__title')
        cat_name = title_tag.text.strip() if title_tag else ''
        cat_type = 'original' if 'Original' in cat_name else 'cover' if 'Cover' in cat_name else cat_name

        items = cat.find_all('section', class_='Music__item')
        for item in items:
            song = extract_song_info(item)
            song['type'] = cat_type
            songs.append(song)

    return songs

def main():
    try:
        response = requests.get('https://www.hololive-dreams.com/en/music')
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"Error fetching page: {e}", file=sys.stderr)
        sys.exit(1)

    songs = parse_html(html)
    output = {
        'total': len(songs),
        'songs': songs
    }
    output_json = json.dumps(output, indent=2, ensure_ascii=False)

    # Write once, overwrite the file
    with open("output.json", "w", encoding='utf-8') as f:
        f.write(output_json)

if __name__ == '__main__':
    main()
