import requests
import urllib
from bs4 import BeautifulSoup
import pypandoc


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

        soup.find("div", class_="footnotes_reference_container").decompose()

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

    result = first_letter + " " + result[1:]

    post_data["content"] = result
    return post_data


def generate_post(post_data):
    post_template = ""
    with open("latex-template/single_post.tex", 'r', encoding="utf-8") as f:
        post_template = f.read()

    authors_string = ""
    for author in post_data["authors"]:
        authors_string += author + ", "

    authors_string = authors_string[:-2]
    result = post_template.replace("[wp2latex-post-subtitle]", "") \
        .replace("[wp2latex-post-title]", post_data["title"]) \
        .replace("[wp2latex-post-authors]", authors_string) \
        .replace("[wp2latex-post-url]", post_data["link"]) \
        .replace("[wp2latex-post-content]", post_data["content"])
    print(result)


def get_host_slug_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    slug = parsed_url.path[1:-1]
    return host, slug
