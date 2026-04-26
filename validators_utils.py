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
    """
    Checks if website is reachable
    """
    try:
        url = normalize_url(url)

        response = requests.get(
            url,
            timeout=5,
            allow_redirects=True,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        return response.status_code < 400

    except:
        return False