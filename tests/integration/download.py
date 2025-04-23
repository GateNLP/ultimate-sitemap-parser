import argparse
import gzip
import hashlib
import json
import logging
import shutil
import sys
from pathlib import Path

import requests

CASSETTE_REPO = "https://github.com/GateNLP/usp-test-cassettes"
MANIFEST_FILE = f"{CASSETTE_REPO}/raw/main/manifest.json"
CASSETTE_ROOT = Path(__file__).parent / "cassettes"

log = logging.getLogger(__name__)


def download_manifest():
    r = requests.get(MANIFEST_FILE, allow_redirects=True)
    r.raise_for_status()

    data = json.loads(r.text)

    with open(CASSETTE_ROOT / "manifest.json", "w") as f:
        f.write(r.text)

    return data


def load_hashes():
    if not (CASSETTE_ROOT / "hashes.json").exists():
        return {}

    with open(CASSETTE_ROOT / "hashes.json") as f:
        return json.load(f)


def find_new(manifest, current_hashes):
    to_dl = []

    for url, data in manifest.items():
        if current_hashes.get(url, {}) != data["hash"]:
            log.info(f"{url} is out-of-date")
            to_dl.append(url)

    return to_dl


def calc_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def dl_cassette(data):
    dl_gz_path = CASSETTE_ROOT / "download" / f"{data['name']}.gz"
    log.info(f"Downloading {data['url']} to {dl_gz_path}")
    with requests.get(data["url"], allow_redirects=True, stream=True) as r:
        r.raise_for_status()

        with open(dl_gz_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    cassette_path = CASSETTE_ROOT / data["name"]
    dl_hash = calc_hash(dl_gz_path)

    if dl_hash != data["hash"]:
        log.error(
            f"Downloaded file hash {dl_hash} does not match expected hash {data['hash']}"
        )
        exit(1)

    log.info(f"Download completed, extracting to {cassette_path}")

    with gzip.open(dl_gz_path, "rb") as f_gz:
        with open(cassette_path, "wb") as f_cassette:
            shutil.copyfileobj(f_gz, f_cassette)

    return dl_gz_path, cassette_path


def update_hashes(current_hashes, url, new_hashes):
    current_hashes[url] = new_hashes

    with open(CASSETTE_ROOT / "hashes.json", "w") as f:
        json.dump(current_hashes, f, indent=2)


def cleanup_files(data, confirm=True):
    cassettes = CASSETTE_ROOT.glob("*.yaml")
    downloads = (CASSETTE_ROOT / "download").glob("*.yaml.gz")

    files = set(list(cassettes) + list(downloads))

    keep_files = []
    for cassette in data.values():
        keep_files.append(CASSETTE_ROOT / cassette["name"])
        keep_files.append(CASSETTE_ROOT / "download" / f"{cassette['name']}.gz")
    keep_files = set(keep_files)

    to_delete = files - keep_files

    if len(to_delete) == 0:
        return

    if confirm:
        sys.stdout.write(f"{len(to_delete)} files to be deleted:\n")
        for file in to_delete:
            sys.stdout.write(f"\t{file}\n")
        sys.stdout.write("\n\n")
        resp = input("Confirm deletion? [y/N] ")
        if resp.lower() != "y":
            log.info("Skipped deletion")
            return

    log.info(f"Deleting {len(to_delete)} outdated files")
    for file in to_delete:
        log.info(f"Deleting {file}")
        file.unlink()


def main(force: bool = False, force_delete=False):
    logging.basicConfig(level=logging.INFO)
    CASSETTE_ROOT.mkdir(exist_ok=True)
    (CASSETTE_ROOT / "download").mkdir(exist_ok=True)

    manifest = download_manifest()
    log.info(f"Downloaded manifest with {len(manifest)} cassettes")
    current_hashes = load_hashes()
    if force:
        to_dl = list(manifest.keys())
    else:
        to_dl = find_new(manifest, current_hashes)
    log.info(f"Downloaded {len(to_dl)} cassettes")

    for url in to_dl:
        dl_cassette(manifest[url])
        update_hashes(current_hashes, url, manifest[url]["hash"])

    cleanup_files(manifest, confirm=not force_delete)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--force", action="store_true", help="Force downloading all cassettes"
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Delete unknown cassettes without confirmation",
    )
    parser.set_defaults(force=False, delete=False)
    args = parser.parse_args()
    main(force=args.force, force_delete=args.delete)
