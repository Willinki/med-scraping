import os
import sys
import json
from tqdm import tqdm
from generic_extract import extract_article_info
from pathlib import Path
import string

os.chdir(os.path.dirname(sys.argv[0]))

with open("./search_lists.json") as f:
    websites = json.load(f)

website = websites["quotidianosanita"]

datasetname = "".join(
    [i for i in Path(website["source"]).name if i not in string.punctuation]
)


def find_files(parent_dir, only_html=True):
    """
    Recursively finds all HTML files in the given parent directory.

    :param parent_dir: The directory to start searching from.
    :return: A list of paths to HTML files.
    """
    html_files = []

    for root, dirs, files in os.walk(parent_dir):
        for file in files:
            # include every file if no html filter
            if not only_html:
                html_files.append(os.path.join(root, file))
            # if html filter is on, include only files that ends with html
            elif only_html and file.lower().endswith(".html"):
                html_files.append(os.path.join(root, file))
            # otherwise, skip
            else:
                continue

    return html_files


if __name__ == "__main__":
    output_json = {"version": "0.1", "data": []}
    parent_directory = website["source"]
    html_files = find_files(parent_directory, only_html=False)
    for file in tqdm(html_files):
        try:
            article_info = extract_article_info(
                file,
                search_lists=[
                    website["title_search_list"],
                    website["subtitle_search_list"],
                    website["content_search_list"],
                    website.get("content_ignore_list"),
                ],
            )
        except Exception as e:
            print(e)
            continue
        output_json["data"].append(article_info)
    with open("./data" + datasetname + ".json", "w", encoding="utf8") as outfile:
        json.dump(output_json, outfile, indent=4, ensure_ascii=False)
