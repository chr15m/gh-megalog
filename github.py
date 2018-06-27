import re
import requests

def get_next_link(result):
    # https://stackoverflow.com/a/32860213
    s = result.headers.get("Link", "")
    if re.search(r'; rel="next"', s):
        return re.sub(r'.*<(.*)>; rel="next".*', r'\1', s)

def github(url, name, project, auth=None, follow=True):
    if project:
        url_constructed = ('https://api.github.com/repos/%s/%s/' % (name, project,)) + url
    else:
        url_constructed = ('https://api.github.com/orgs/%s/' % (name,)) + url
    result = requests.get(url.startswith("https://") and url or url_constructed, auth=auth)
    if result.status_code >= 200 and result.status_code <= 299:
        next_url = get_next_link(result)
        if next_url and follow:
            return result.json() + github(next_url, name, project, auth, follow)
        else:
            return result.json()
    else:
        raise Exception("GitHub returned " + str(result.status_code) + " error")

