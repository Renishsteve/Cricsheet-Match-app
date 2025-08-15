# src/scraper/download_and_extract_cricsheet.py
import os, re, argparse, requests, zipfile, io
from urllib.parse import urljoin

def find_json_zip_links(html):
    # find hrefs which include 'json' and end with .zip
    return re.findall(r'href=["\']([^"\']*?json[^"\']*?\.zip)["\']', html, flags=re.I)

def download_and_extract(url, out_dir):
    print("Downloading:", url)
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    print(f"Found {len(z.namelist())} files in zip — extracting to {out_dir} ...")
    os.makedirs(out_dir, exist_ok=True)
    z.extractall(out_dir)
    print("Extract done.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--downloads-page", default="https://cricsheet.org/downloads/")
    parser.add_argument("--which", default="all", help="match set to download (all, test, odi, t20, ipl, etc.)")
    parser.add_argument("--out-dir", default="data/raw")
    args = parser.parse_args()

    print("Fetching downloads page...")
    r = requests.get(args.downloads_page, timeout=30)
    r.raise_for_status()
    hrefs = find_json_zip_links(r.text)
    if not hrefs:
        print("No JSON zip links found on the downloads page. Try opening the page in a browser to download manually.")
        return

    # normalize urls and choose candidate
    full_urls = [urljoin(args.downloads_page, h) for h in hrefs]
    want = args.which.lower()
    if want == "all":
        candidate = full_urls[0]
    else:
        candidates = [u for u in full_urls if want in u.lower()]
        candidate = candidates[0] if candidates else full_urls[0]

    download_and_extract(candidate, args.out_dir)

if __name__ == "__main__":
    main()
