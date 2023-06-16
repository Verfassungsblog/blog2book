import wp_import
import argparse

def main():
    parser = argparse.ArgumentParser(prog="wp2latex", usage="Convert your wordpress blog posts to LaTeX projects")
    parser.add_argument('--with-footnotes', action='store_true')
    parser.add_argument('--endnotes', action='store_true')
    parser.add_argument('--first-letter-before')
    parser.add_argument('--first-letter-after')
    parser.add_argument('uris', nargs='+')
    args = parser.parse_args()

    for url in args.uris:
        print("Downloading "+url)
        host,slug = wp_import.get_host_slug_from_url(url)
        post_data = wp_import.import_post(host, slug, args)
        post_in_latex = wp_import.generate_post(post_data)


if __name__ == '__main__':
    main()
