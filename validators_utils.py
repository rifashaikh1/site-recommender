import requests
import validators
import re


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def valid_format(url):
    return validators.url(normalize_url(url))


def site_live(url):

    if not url.startswith(("http://","https://")):
        urls = [
            "https://" + url,
            "http://" + url
        ]
    else:
        urls = [url]

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    for u in urls:

        try:
            r = requests.head(
                u,
                timeout=5,
                allow_redirects=True,
                headers=headers
            )

            if r.status_code < 500:
                return True

        except:
            pass

        try:
            r = requests.get(
                u,
                timeout=5,
                allow_redirects=True,
                headers=headers
            )

            if r.status_code < 500:
                return True

        except:
            pass

    return False


def check_parked_domain(url):

    url = normalize_url(url)

    try:
        r = requests.get(
            url,
            timeout=5,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        html = r.text.lower()

        parked_markers = [
            "domain for sale",
            "buy this domain",
            "parked free",
            "courtesy of godaddy",
            "this domain is parked",
            "coming soon"
            "parking"
        ]

        if any(marker in html for marker in parked_markers):
            return True

        return False

    except:
        return False


def gibberish_domain(url):

    domain = (
        url.replace("https://","")
           .replace("http://","")
           .split("/")[0]
           .split(".")[0]
    )

    vowels = len(
        re.findall(
            r"[aeiou]",
            domain.lower()
        )
    )

    if len(domain) > 6 and vowels <= 1:
        return True

    return False


def domain_to_keywords(url):

    domain = (
        url.replace("https://","")
           .replace("http://","")
           .split("/")[0]
    )

    text = re.sub(
        r'[^a-zA-Z]',
        ' ',
        domain
    )

    return text.lower()