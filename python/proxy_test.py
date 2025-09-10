import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # progress bar

PROXIES_FILE = Path("data/proxies.txt")
TEST_URL = "https://wplace.live"
TIMEOUT = 10  # seconds
MAX_WORKERS = 20  # number of threads

# Browser-like headers (important for avoiding 403)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def load_proxies(file_path):
    """Load proxies from file, stripping whitespace and skipping blanks."""
    if not file_path.exists():
        print(f"❌ Proxy file not found: {file_path}")
        return []

    with file_path.open("r") as f:
        return [line.strip() for line in f if line.strip()]


def test_proxy(proxy):
    """Test a single proxy. Return proxy if working, None otherwise."""
    proxies = {"http": proxy, "https": proxy}
    try:
        response = requests.get(TEST_URL, proxies=proxies, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code == 200 and "<!doctype html>" in response.text.lower():
            return f"{proxy} -> OK (HTML {len(response.text)} bytes)"
    except Exception:
        pass
    return None


def main():
    proxies = load_proxies(PROXIES_FILE)
    if not proxies:
        print("No proxies to test.")
        return

    print(f"Testing {len(proxies)} proxies with {MAX_WORKERS} threads...\n")
    working_proxies = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(test_proxy, proxy) for proxy in proxies]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing proxies"):
            result = future.result()
            if result:
                proxy = result.split(" -> ")[0]
                print(f"✅ WORKING: {result}")
                working_proxies.append(proxy)

    # Save only working proxies
    with PROXIES_FILE.open("w") as f:
        f.write("\n".join(working_proxies))

    print(f"\n✅ Done. {len(working_proxies)} working proxies saved back to {PROXIES_FILE}")


if __name__ == "__main__":
    main()
