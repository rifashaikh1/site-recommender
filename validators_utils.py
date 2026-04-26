import requests
import validators


def normalize_url(url):
    """
    Add https:// if user entered just domain
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def valid_format(url):
    """
    Checks if URL format is valid
    """
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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for u in urls:

        try:
            # try HEAD first
            r = requests.head(
                u,
                allow_redirects=True,
                timeout=5,
                headers=headers
            )

            # treat even 403 as live
            if r.status_code < 500:
                return True

        except:
            pass

        try:
            # fallback GET
            r = requests.get(
                u,
                allow_redirects=True,
                timeout=5,
                headers=headers
            )

            if r.status_code < 500:
                return True

        except:
            pass

    return False