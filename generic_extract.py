from bs4 import BeautifulSoup
from bs4.element import NavigableString
from sanitizer import sanitize_text
from pathlib import Path
import re

img_tags = ["img", "image", "picture", "map", "area", "svg"]
formatting_tags = ["a", "strong", "span", "b", "strong", "i", "em", "mark", "small", "del", "ins", "sub", "sup"]

search_lists = [
    [[{"tag": "title", "attrs": {}}], [{"tag": "h1", "attrs": {}}]],
    [[{"tag": "h2", "attrs": {}}]],
    [{"tag": "div", "attrs": {}}]
]


def search_title(soup_obj, search_list, separator=""):
    for item in search_list:
        candidate = soup_obj
        for step in item:
            candidate = candidate.find(step['tag'], step['attrs'])
            if candidate is None:
                break
            #else, continue
        #at the end, if something found
        if candidate is not None:
            return candidate.get_text(separator=separator)
        #else, continue
    return ""


def is_image(element: NavigableString):
    parent_tag = element.parent.name
    parent_class = element.parent.attrs.get("class")
    img_tag_check = parent_tag in img_tags
    img_class_check = False
    if parent_class is not None:
        img_class_check = any([class_tag.find("image") > 0 or class_tag.find("img") > 0 for class_tag in parent_class])
    return img_tag_check or img_class_check


def is_blacklisted(element, blacklist):
    for tag in blacklist:
        if element.name == tag.get("tag"):
            if element.get('class') is not None and tag.get("attrs").get("class") in element.get('class'):
                return True
    return False


def get_content(candidates, separator="", blacklist=None):
    if blacklist is not None:
        for candidate in candidates:
            for child in candidate.find_all():
                if is_blacklisted(child, blacklist):
                    child.decompose()
    return '\n'.join([candidate.get_text(separator=separator) for candidate in candidates])


def get_content_complex(candidates, blacklist=None):
    if blacklist is not None:
        for candidate in candidates:
            for child in candidate.find_all():
                if is_blacklisted(child, blacklist):
                    child.decompose()
    content_text = ""
    for candidate in candidates:
        candidate_text = ""
        for descendant in candidate.descendants:
            text = str(descendant)
            if isinstance(descendant, NavigableString):
                parent_tag = descendant.parent.name
                #ignore images and empty content
                if is_image(descendant) or re.match(r"^[\n\t\s]+$", text) is not None:
                    continue
                #formatting tags and hyperlinks do not add newline
                if parent_tag in formatting_tags:
                    candidate_text = "".join([candidate_text, text])
                    #text from other elements is separated by newline
                else:
                    candidate_text = "".join([candidate_text, text])
        content_text = "\n".join([content_text, candidate_text])
    return content_text


def search_content(soup_obj, search_list, black_list=None, separator=""):
    for item in search_list:
        candidates = soup_obj.find_all(item['tag'], item['attrs'])
        if len(candidates) > 0:
            #return get_content_complex(candidates) #for more customization
            return get_content(candidates, separator, black_list)
    return ""


def extract_article_info(html_file_path, search_lists=search_lists):
    with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Extract the file name
    path = Path(html_file_path)
    file_name = "./" + "/".join(path.parts[-3:])

    # Search for body. If none, skip
    body_tag = soup.find('body')
    if body_tag is None:
        title = ""
        title_long = ""
        content = ""
    else:
        title = search_title(soup, search_lists[0])
        if len(search_lists[1]) > 0:
            subtitle = search_title(soup, search_lists[1], separator=" - ")
            title_long = title + "\n" + subtitle
        else:
            title_long = title
        content = search_content(soup_obj=soup, search_list=search_lists[2], black_list=search_lists[3])

    # Return the extracted information as a dictionary
    return {
        'file_name': file_name,
        'title': sanitize_text(title),
        'content': sanitize_text(title_long + content)
    }
