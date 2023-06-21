import requests
import urllib
from bs4 import BeautifulSoup
import pypandoc
import re
import link_citation_converter


def import_post(host, slug, args):
    print("Slug for post is " + slug + ", host is " + host + ". Trying to get post from API.")

    post = requests.get("https://" + host + "/wp-json/wp/v2/posts?slug=" + slug)

    if post.status_code != 200:
        print("Couldn't get post from API!")
        return

    post_data = {}

    json = post.json()[0]
    post_data["title"] = json["title"]["rendered"]
    if json["date"]:
        post_data["date"] = json["date"]
    post_data["link"] = json["link"]
    if json["coauthors"]:
        authors = []
        for author in json["coauthors"]:
            authors.append(author["display_name"])
        post_data["authors"] = authors

    raw_content = json["content"]["rendered"]

    soup = BeautifulSoup(raw_content, 'html.parser')

    footnotes_dict = []

    if args.with_footnotes:
        footnotes = soup.find_all("span", class_="footnote_referrer")

        for footnote in footnotes:
            footnote_id = footnote.find("sup", class_="footnote_plugin_tooltip_text").get("id").replace("tooltip",
                                                                                                        "reference")
            footnote_text = soup.find("a", id=footnote_id).find_parent("tr").find("td",
                                                                                  class_="footnote_plugin_text").get_text()
            footnotes_dict.append(footnote_text)

            footnote.replace_with("wp2latex-footnote-placeholder-" + str(len(footnotes_dict) - 1))

        frc = soup.find("div", class_="footnotes_reference_container")
        if frc:
            frc.decompose()

    raw_html = soup.__str__()
    result = pypandoc.convert_text(raw_html, 'tex', format='html', extra_args=["--shift-heading-level-by=-1"])

    if args.with_footnotes:
        for footnote_count in range(len(footnotes_dict) - 1, -1, -1):
            command_start = ""
            if args.endnotes:
                command_start = "\\endnote{"
            else:
                command_start = "\\footnote{"
            result = result.replace("wp2latex-footnote-placeholder-" + str(footnote_count),
                                    command_start + footnotes_dict[footnote_count] + "}")

    first_letter = result[0]

    if args.first_letter_before:
        first_letter = args.first_letter_before + first_letter

    if args.first_letter_after:
        first_letter += args.first_letter_after

    if args.first_letter_after or args.first_letter_before:
        result = first_letter + " " + result[1:]

    if args.fix_sections:
        result = fix_sections(result)

    if args.convert_links_to_citations:
        result = link_citation_converter.convert_links_to_citations(result, args)

    if args.remove_ulines:
        result = result.replace("\\uline", "")

    post_data["content"] = result
    return post_data

def generate_post(post_data, args):
    post_template = ""
    with open("latex-templates/single_post.tex", 'r', encoding="utf-8") as f:
        post_template = f.read()

    authors_string = ""
    for author in post_data["authors"]:
        authors_string += author + ", "

    authors_string = authors_string[:-2]
    result = post_template.replace("[wp2latex-post-subtitle]", "") \
        .replace("[wp2latex-post-title]", tex_escape(post_data["title"])) \
        .replace("[wp2latex-post-authors]", tex_escape(authors_string)) \
        .replace("[wp2latex-post-url]", tex_escape(post_data["link"])) \
        .replace("[wp2latex-post-content]", post_data["content"])

    # Add \printendnotes if endnotes activated and there is at least one endnote
    if args.endnotes and (result.find("\\endnote") != -1 or result.find(args.cite_command) != -1):
        result = result.replace("[wp2latex-print-endnotes-if-any]", "\\printendnotes")
    else:
        result = result.replace("[wp2latex-print-endnotes-if-any]", "")

    return result


def get_host_slug_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    slug = parsed_url.path[1:-1]
    return host, slug


def check_if_url_is_category(url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.path.startswith("/category/"):
        return True
    else:
        return False


def get_category_host_slug_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    raw_slug = parsed_url.path[:-1]
    slug = raw_slug.split("/")[-1]
    return host, slug


def get_category_id_from_slug(host, slug):
    category = requests.get("https://" + host + "/wp-json/wp/v2/categories?slug=" + slug)

    if category.status_code != 200:
        print("Couldn't get category id for URL from API!")
        return

    print(category.json())
    return category.json()[0]["id"]


def get_post_slugs_in_category(host, category_id):
    posts = requests.get("https://" + host + "/wp-json/wp/v2/posts?categories=" + str(category_id) + "&per_page=100")

    if posts.status_code != 200:
        print("Couldn't get posts in category from API!")
        return

    post_slugs = []

    for post in posts.json():
        post_slugs.append(post["slug"])

    return post_slugs


def download_post(host, slug, args, posts_directory, post_count):
    print("Downloading post " + slug)
    post_in_latex = generate_post(import_post(host, slug, args), args)
    with open(posts_directory + "/post_" + str(post_count) + ".tex", "x", encoding="utf-8") as f:
        f.write(post_in_latex)


def fix_sections(input_str):
    regex = r"\\hypertarget\{[^}]+\}\{%\n\\section{\\texorpdfstring{\\textbf\{[^}]+\}}\{[^}]+\}\}\\label\{[^}]+\}}"
    matches = re.findall(regex, input_str)

    for match in matches:
        old_section_command = match
        regex2 = r"\\section{\\texorpdfstring{\\textbf{([^}]+)}}{[^}]+}}\\label{[^}]+}"
        section_title = re.search(regex2, old_section_command).group(1)
        input_str = input_str.replace(old_section_command, "\\section*{"+tex_escape(section_title)+"}")

    input_str = input_str.replace("\\section{", "\\section*{")

    return input_str

def tex_escape(text):
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)