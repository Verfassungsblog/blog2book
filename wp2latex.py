import os
import shutil
import wp_import
import argparse
import my_globals

biblatex_entries = ""


def cli_main():
    parser = argparse.ArgumentParser(prog="wp2latex", usage="Convert your wordpress blog posts to LaTeX projects")
    parser.add_argument('--with-footnotes', action='store_true', help='Converts footnotes, currently only wordpress.org/plugins/footnotes/ is supported.')
    parser.add_argument('--endnotes', action='store_true', help='if given, use endnotes instead of footnotes')
    parser.add_argument('--first-letter-before', help='latex code to be put before the first letter of [wp2latex-post-content] in single_post.tex template')
    parser.add_argument('--first-letter-after', help='latex code to be put after first letter of [wp2latex-post-content]')
    parser.add_argument('--project-template', help='must be supplied if url is a category, creates whole latex project instead of single output file')
    parser.add_argument('--output')
    parser.add_argument('--convert-links-to-citations', action='store_true')
    parser.add_argument('--unnumbered-headings', action='store_true')
    parser.add_argument('--cite-command', default="\\footfullcite")
    parser.add_argument('--translation-server', default="https://translation-server.anghenfil.de")
    parser.add_argument('uris', nargs='+')
    args = parser.parse_args()

    if len(args.uris) > 1:
        if not args.project_template:
            print("Error: Project template required if more than one uri supplied!")
            exit(-1)

        # Generate output path
        output_path = ""
        if args.output:
            output_path = args.output
        else:
            if not os.path.exists("output"):
                output_path = "output"
            else:
                x = 1
                while os.path.exists("output_" + str(x)):
                    x = x + 1

                output_path = "output_" + str(x)

            # Copy project template to output
            shutil.copytree(args.project_template, output_path)

        posts_directory = output_path + "/posts"
        if not os.path.exists(posts_directory):
            os.makedirs(posts_directory)

        post_count = 1
        include_list = ""

        for url in args.uris:
            if wp_import.check_if_url_is_category(url):
                print("Found category url: " + url)
                host, slug = wp_import.get_category_host_slug_from_url(url)
                category_id = wp_import.get_category_id_from_slug(host, slug)
                post_slugs = wp_import.get_post_slugs_in_category(host, category_id)
                for post_slug in post_slugs:
                    wp_import.download_post(host, post_slug, args, posts_directory, post_count)
                    include_list += "\\include{posts/" + "post_" + str(post_count) + "}\n"
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


    else:
        print("Downloading " + args.uris[0])
        host, slug = wp_import.get_host_slug_from_url(args.uris[0])
        post_in_latex = wp_import.generate_post(wp_import.import_post(host, slug, args), args)

        output_path = ""
        if args.output:
            output_path = args.output
        else:
            if not os.path.exists("output.tex"):
                output_path = "output.tex"
            else:
                x = 1
                while os.path.exists("output_" + str(x) + ".tex"):
                    x = x + 1

                output_path = "output_" + str(x) + ".tex"

        with open(output_path, "x", encoding="utf-8") as f:
            f.write(post_in_latex)

        print("Saved post to " + output_path)

        if len(my_globals.biblatex_entries) > 0:
            bib_output_path = "bibliography.bib"
            if os.path.exists("bibliography.bib"):
                x = 1
                while os.path.exists("bibliography_" + str(x) + ".bib"):
                    x = x + 1

                bib_output_path = "bibliography_" + str(x) + ".bib"


            with open(bib_output_path, "x") as f:
                f.write(my_globals.biblatex_entries)

            print("Saved bibliography as "+bib_output_path)


if __name__ == '__main__':
    my_globals.init()
    cli_main()
