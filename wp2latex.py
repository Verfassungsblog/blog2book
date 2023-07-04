import os
import re
import shutil
import unicodedata

import wp_import
import argparse
import my_globals


def find_free_path(preferred_path, file_extension = ""):
    if not os.path.exists(preferred_path+file_extension):
        output_path = preferred_path+file_extension
    else:
        x = 1
        while os.path.exists(preferred_path + "_" + str(x)+file_extension):
            x = x + 1
        output_path = preferred_path + "_" + str(x)+file_extension

    return output_path


def cli_main():
    parser = argparse.ArgumentParser(prog="wp2latex", usage="Convert your wordpress blog posts to LaTeX projects")
    parser.add_argument('--with-footnotes', action='store_true',
                        help='Converts footnotes, currently only wordpress.org/plugins/footnotes/ is supported.')
    parser.add_argument('--endnotes', action='store_true', help='if given, use endnotes instead of footnotes')
    parser.add_argument('--first-letter-before',
                        help='latex code to be put before the first letter of [wp2latex-post-content] in '
                             'single_post.tex template')
    parser.add_argument('--first-letter-after',
                        help='latex code to be put after first letter of [wp2latex-post-content]')
    parser.add_argument('--project-template',
                        help='must be supplied if url is a category, creates whole latex project instead of single '
                             'output file')
    parser.add_argument('--output', help="specify custom output path")
    parser.add_argument('--convert-links-to-citations', action='store_true', help="tries to convert all links in post "
                                                                                  "to citations commands with biblatex")
    parser.add_argument('--fix-sections', action='store_true', help="tries to correct sections commands, e.g. making "
                                                                    "them unnumbered, remove textbfs in section "
                                                                    "titles etc.")
    parser.add_argument('--cite-command', default="\\footfullcite", help="Set command for citations, default is "
                                                                         "\\footfullcite")
    parser.add_argument('--translation-server', default="https://translation-server.anghenfil.de",
                        help="Use different zotero translation server for automatic citation generation")
    parser.add_argument('--remove-ulines', action='store_true', help="Removes uline commands from LaTeX output")
    parser.add_argument('--zip', action='store_true', help="if set creates zip with latex project files")
    parser.add_argument('--all-posts', action='store_true', help="select all posts - only supply hostname")
    parser.add_argument('--limit-to-categories', help="used together with all-posts - only posts with supplied "
                                                      "categories")
    parser.add_argument('--after', help="used together with all-posts - only posts after specified date. Specify "
                                            "date as YYYY-MM-DD.")
    parser.add_argument('--before', help="used together with all-posts - only posts before specified date. "
                                             "Specify date as YYYY-MM-DD.")
    parser.add_argument('--exclude-categories', help="used together with all-posts - all posts except those in categories")
    parser.add_argument('--exclude-categories-recursive', action='store_true', help='if set also excludes children categories for given categories')
    parser.add_argument('--single-post-template')
    parser.add_argument('uris', nargs='+')
    args = parser.parse_args()

    if len(args.uris) > 1 or wp_import.check_if_url_is_category(args.uris[0]) or args.all_posts:
        if not args.project_template:
            print("Error: Project template required if more than one uri or uri of category or --all-posts supplied!")
            exit(-1)

        # Generate output path
        if args.output:
            output_path = args.output
        else:
            output_path = find_free_path("output")

        # Copy project template to output
        shutil.copytree(args.project_template, output_path)
        posts_directory = output_path + "/posts"
        if not os.path.exists(posts_directory):
            os.makedirs(posts_directory)

        post_count = 1
        include_list = ""

        if args.all_posts:
            print("Trying to download all posts from host " + args.uris[0])
            posts = wp_import.get_all_posts(args.uris[0], args.limit_to_categories, args.exclude_categories, args.after, args.before, args.exclude_categories_recursive)
            for post in posts:
                converted_post = wp_import.convert_post_json(post, args)
                post_in_latex = wp_import.generate_post(converted_post, args)
                fname = "post_" + str(post_count) + "_" + slugify(converted_post["authors"][0], False)
                with open(posts_directory + "/" + fname + ".tex", "x", encoding="utf-8") as f:
                    f.write(post_in_latex)
                include_list += "\\include{posts/" + fname + "}\n"
                post_count = post_count + 1
        else:

            for url in args.uris:
                if wp_import.check_if_url_is_category(url):
                    print("Found category url: " + url)
                    host, slug = wp_import.get_category_host_slug_from_url(url)
                    category_id = wp_import.get_category_id_from_slug(host, slug)

                    posts = wp_import.get_all_posts(host, category_id, None, None, None)

                    for post in posts:
                        converted_post = wp_import.convert_post_json(post, args)
                        post_in_latex = wp_import.generate_post(converted_post, args)
                        fname = "post_" + str(post_count) + "_" + slugify(converted_post["authors"][0], False)
                        with open(posts_directory +"/"+ fname+ ".tex", "x", encoding="utf-8") as f:
                            f.write(post_in_latex)
                        include_list += "\\include{posts/" + fname + "}\n"
                        post_count = post_count + 1

                else:
                    host, slug = wp_import.get_host_slug_from_url(url)
                    wp_import.download_post(host, slug, args, posts_directory, post_count)
                    include_list += "\\include{posts/" + "post_" + str(post_count) + "}\n"
                    post_count = post_count + 1

        # add include_list to main.tex
        with open(output_path + "/main.tex", "r+") as f:
            content = f.read()
            f.seek(0)
            f.truncate()
            f.write(content.replace("[wp2latex-file-includes]", include_list))

        # add biblatex file if required
        if len(my_globals.biblatex_entries) > 0:
            with open(output_path + "/bibliography.bib", "x") as f:
                f.write(my_globals.biblatex_entries)

        if args.zip:
            shutil.make_archive(output_path, "zip", output_path)
    else:
        print("Downloading " + args.uris[0])
        host, slug = wp_import.get_host_slug_from_url(args.uris[0])
        post_in_latex = wp_import.generate_post(wp_import.import_post(host, slug, args), args)

        if args.output:
            output_path = args.output
        else:
            output_path = find_free_path("output", ".tex")

        with open(output_path, "x", encoding="utf-8") as f:
            f.write(post_in_latex)

        print("Saved post to " + output_path)

        if len(my_globals.biblatex_entries) > 0:
            bib_output_path = find_free_path("bibliography", ".bib")

            with open(bib_output_path, "x") as f:
                f.write(my_globals.biblatex_entries)

            print("Saved bibliography as " + bib_output_path)


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


if __name__ == '__main__':
    my_globals.init()
    cli_main()
