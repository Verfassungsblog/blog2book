import uuid

import requests
from requests.exceptions import ReadTimeout
import re
import my_globals
import wp_import


def convert_link_to_bibtex(link, translation_server):
    link = link.replace("\\%", "%")
    print("Trying to get citation for link \"" + link + "\".")
    try:
        api_res = requests.post(translation_server + "/web", data=link, headers={'Content-type': 'text/plain'},
                                timeout=3.5)
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


def convert_links_to_citations(input_str, args):
    pattern = r'\\href\{([^}]+)\}\{([^}]+)\}'
    links = re.findall(pattern, input_str)

    for link in links:
        url = link[0]
        link_text = link[1]
        print("URL:", url)
        print("Link-Text:", link_text)
        biblatex_entry = convert_link_to_bibtex(url, args.translation_server)
        if not biblatex_entry:
            print("Couldn't convert Link " + url + " to Citation!")
            continue

        new_biblatex_uuid = uuid.uuid4()
        while new_biblatex_uuid in my_globals.biblatex_uuids:
            new_biblatex_uuid = uuid.uuid4()

        my_globals.biblatex_uuids.append(new_biblatex_uuid)

        biblatex_id_pattern = r"@\w+{([^,]+)"
        biblatex_id_raw = re.search(biblatex_id_pattern, str(biblatex_entry))
        if not biblatex_id_raw:
            print("Couldn't convert Link " + url + " to Citation!")
            continue

        old_biblatex_id = biblatex_id_raw.group(1)
        biblatex_entry = biblatex_entry.replace(old_biblatex_id, str(new_biblatex_uuid))
        my_globals.biblatex_entries += str(biblatex_entry)
        input_str = input_str.replace("\\href{" + url + "}{" + link_text + "}",
                                      " " + wp_import.tex_escape(link_text) + args.cite_command + "{" + str(
                                          new_biblatex_uuid) + "}")
    return input_str
