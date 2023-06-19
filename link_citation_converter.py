import requests
from requests.exceptions import ReadTimeout

def convert_link_to_bibtex(link, translation_server):
    print("Trying to get citation for link \"" + link + "\".")
    try:
        api_res = requests.post(translation_server + "/web", data=link, headers={'Content-type': 'text/plain'}, timeout=3.5)
    except ReadTimeout:
        print("Timeout.")
        return False

    if api_res.status_code != 200:
        print("Couldn't get citation for link " + link + "!")
        return False

    biblatex_entry = requests.post(translation_server + "/export?format=biblatex", data=api_res.text.encode('utf-8'),
                                   headers={'Content-type': 'application/json'})
    if biblatex_entry.status_code != 200:
        print("Couldn't export citation for link " + link + "!")
        return False

    return biblatex_entry.text
