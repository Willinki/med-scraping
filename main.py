import os
import sys
import json
from tqdm import tqdm
from generic_extract import extract_article_info 
from pathlib import Path
import string

os.chdir(os.path.dirname(sys.argv[0]))

with open('./search_lists.json') as f:
    websites = json.load(f)

website = websites["medicitalia"]

datasetname = ''.join([i for i in Path(website["source"]).name if i not in string.punctuation])

def find_html_files(parent_dir):
    """
    Recursively finds all HTML files in the given parent directory.

    :param parent_dir: The directory to start searching from.
    :return: A list of paths to HTML files.
    """
    html_files = []

    for root, dirs, files in os.walk(parent_dir):
        for file in files:
            if file.lower().endswith('.html'):
                html_files.append(os.path.join(root, file))

    return html_files


if __name__ == "__main__":
    output_json={"version":"0.1","data":[]}
    parent_directory = website["source"]
    html_files = find_html_files(parent_directory)
    for file in tqdm(html_files):
        output_json["data"].append(extract_article_info(file, search_lists=[website["title_search_list"],
                                                                            website["subtitle_search_list"],
                                                                            website["content_search_list"]]))
    with open("../"+datasetname+".json", 'w', encoding='utf8') as outfile:
        json.dump(output_json, outfile,indent=4, ensure_ascii=False)       

