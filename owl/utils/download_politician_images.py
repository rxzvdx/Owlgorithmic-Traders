import os
import re
import requests
from urllib.parse import quote

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw_data')
PROFILE_PICS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'profile_pics')
LOG_FILE = os.path.join(PROFILE_PICS_DIR, 'download_log.txt')

os.makedirs(PROFILE_PICS_DIR, exist_ok=True)

# Helper to extract unique names from all FD.txt files
def extract_unique_names():
    names = set()
    for year_folder in os.listdir(RAW_DATA_DIR):
        year_path = os.path.join(RAW_DATA_DIR, year_folder)
        if not os.path.isdir(year_path):
            continue
        for file in os.listdir(year_path):
            if file.endswith('FD.txt'):
                with open(os.path.join(year_path, file), encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split('\t')
                        if len(parts) >= 3:
                            first = parts[2].strip()
                            last = parts[1].strip()
                            if first and last:
                                # Remove honorifics and extra whitespace
                                name = re.sub(r'^(Hon\.|Mr\.|Ms\.|Mrs\.|Dr\.|Rep\.|Sen\.|Sr\.|Jr\.|Honorable|Sr|Jr|Miss|Sir|Madam|Madame|Mx)\.?\s*', '', f"{first} {last}").strip()
                                names.add(name)
    return sorted(names)

# Helper to query Wikidata for a photo URL
def get_wikidata_image_url(name):
    # Step 1: Search for the person on Wikidata
    search_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={quote(name)}&language=en&format=json&type=item&limit=1"
    headers = {'User-Agent': 'OwlPoliticianImageBot/1.0 (contact: youremail@example.com)'}
    resp = requests.get(search_url, headers=headers)
    if not resp.ok:
        return None
    results = resp.json().get('search', [])
    if not results:
        return None
    entity_id = results[0]['id']
    # Step 2: Get the entity's claims (properties)
    entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    resp = requests.get(entity_url, headers=headers)
    if not resp.ok:
        return None
    entity = resp.json()['entities'][entity_id]
    claims = entity.get('claims', {})
    # P18 is the property for image
    if 'P18' not in claims:
        return None
    image_name = claims['P18'][0]['mainsnak']['datavalue']['value']
    # Construct the Wikimedia Commons URL
    commons_name = image_name.replace(' ', '_')
    md5 = __import__('hashlib').md5(commons_name.encode('utf-8')).hexdigest()
    url = f"https://upload.wikimedia.org/wikipedia/commons/{md5[0]}/{md5[0:2]}/{commons_name}"
    return url

def download_image(url, out_path):
    resp = requests.get(url, headers={'User-Agent': 'OwlPoliticianImageBot/1.0 (contact: youremail@example.com)'})
    if resp.ok and resp.headers.get('content-type', '').startswith('image/'):
        with open(out_path, 'wb') as f:
            f.write(resp.content)
        return True
    return False

def main():
    names = extract_unique_names()
    print(f"Found {len(names)} unique names.")
    found, not_found = 0, 0
    with open(LOG_FILE, 'w', encoding='utf-8') as log:
        for name in names:
            filename = name.replace(' ', '_') + '.jpg'
            out_path = os.path.join(PROFILE_PICS_DIR, filename)
            if os.path.exists(out_path):
                print(f"Already exists: {filename}")
                continue
            url = get_wikidata_image_url(name)
            if url:
                print(f"Downloading {name} -> {filename}")
                if download_image(url, out_path):
                    log.write(f"SUCCESS: {name} -> {url}\n")
                    found += 1
                else:
                    print(f"Failed to download image for {name}")
                    log.write(f"FAILED_DOWNLOAD: {name} -> {url}\n")
                    not_found += 1
            else:
                print(f"No image found for {name}")
                log.write(f"NO_IMAGE: {name}\n")
                not_found += 1
    print(f"Done. {found} images downloaded, {not_found} not found or failed.")

if __name__ == '__main__':
    main() 