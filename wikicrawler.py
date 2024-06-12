import wikipediaapi
from tqdm import tqdm
import json
from sanitizer import sanitize_text
from urllib.parse import urlparse


def get_categorymembers(categorymembers, datacontainer, level=0, max_level=1, inside_loop=False, visited=[]):
    pbar = tqdm(categorymembers.values(), position=0, leave=True)
    index = 0
    for c in pbar:
        if not inside_loop and index < 7:
            index += 1
            continue
        #CHECK IF IT HAS A URL
        if not isinstance(c.fullurl, str):
            c.fullurl = "ERROR"
            desc = "ERROR"
        else:
            desc = urlparse(c.fullurl).path
        pbar.set_description(f"Processing {desc[:35].ljust(35)} (level {level})")
        if c.fullurl in visited:
            continue
        else:
            visited.append(c.fullurl)
        #CHECK IF IT BELONGS TO THE MEDICINE PORTAL (otherwise lot of garbage will be included while searching)
        if c.links.get('Portale:Medicina') is not None:
            #CHECK IF EVERYTHING HAS BEEN RETRIEVED CORRECTLY, IF NOT, FLAG AS ERROR
            if not isinstance(c.title, str):
                c.title = "ERROR"
            if not isinstance(c.text, str):
                c.text = "ERROR"
            #APPEND TO DATACONTAINER AND SANITIZE TEXT TO PREVENT ENCODING ERRORS
            datacontainer.append(
                {"file_name": sanitize_text(c.fullurl, remove_urls=False), "title": sanitize_text(c.title),
                 "content": sanitize_text(c.text)})
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            get_categorymembers(c.categorymembers, datacontainer, level=level + 1, max_level=max_level,
                                inside_loop=True, visited=visited)
        if not inside_loop:
            print(f"******** {index} COMPLETED! **********\n*********************************")
            index += 1
    if not inside_loop:
        return datacontainer
    else:
        with open("../wiki_temp_3.json", 'w', encoding='utf8') as tempfile:
            temp_json = {"version": "0.1", "data": datacontainer, "already_visited": visited}
            json.dump(temp_json, tempfile, indent=4, ensure_ascii=False)


def load_json(path: str) -> dict:
    with open(path, 'r') as file:
        jsondict = json.load(file)
    return jsondict


if __name__ == "__main__":
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='Detsutut/0.0 (buonocore.tms@gmail.com)',
        language='it',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        timeout=1000000000
    )
    cat = wiki_wiki.page("Category:Scienze della salute")
    data = []
    j = load_json(r"../wiki_temp_2.json")
    already_visited = list(set(d['file_name'] for d in j["data"]))
    output_json = {"version": "0.1",
                   "data": get_categorymembers(cat.categorymembers, datacontainer=j["data"], level=0, max_level=8,
                                               visited=already_visited)}
    with open("../wiki.json", 'w', encoding='utf8') as outfile:
        json.dump(output_json, outfile, indent=4, ensure_ascii=False)
