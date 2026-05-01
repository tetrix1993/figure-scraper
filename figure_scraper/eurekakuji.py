from figure_scraper.website import Website
import figure_scraper.constants as constants


class EurekaKuji(Website):
    base_folder = constants.FOLDER_EUREKAKUJI
    title = constants.WEBSITE_TITLE_EUREKAKUJI
    keywords = ["https://eureka-kuji.com"]

    product_url_prefix = 'https://eureka-kuji.com/'
    product_url_template = product_url_prefix + 'lp/%s'
    product_url_template2 = product_url_prefix + 'dlp/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter page name: ')
            if len(expr) == 0:
                return

            cls.process_product_page(expr)

    @classmethod
    def process_product_page(cls, page):
        is_valid = False
        try:
            for template in [cls.product_url_template, cls.product_url_template2]:
                page_url = template % page
                if not page_url.endswith('/'):
                    page_url += '/'
                    soup = cls.get_soup(page_url)
                    if soup is None:
                        continue
                    images = soup.select('.prizeList img[src],.pcOnly img[src],.specialimage img[src]')
                    if len(images) == 0:
                        continue
                    is_valid = True
                    for image in images:
                        image_url = page_url + image['src']
                        img_name = image['src'].split('/')[-1]
                        cls.download_image(image_url, page + '/' + img_name)
                    break
            if not is_valid:
                print(f'[ERROR] {cls.product_url_template % page} does not exists.')
        except Exception as e:
            print(f'[ERROR] Error in processing {page}: {e}')
