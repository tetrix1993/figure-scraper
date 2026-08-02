from figure_scraper.website import Website
import figure_scraper.constants as constants


class KotobukiyaKuji(Website):
    base_folder = constants.FOLDER_KOTOBUKIYAKUJI
    title = constants.WEBSITE_TITLE_KOTOBUKIYAKUJI
    keywords = ["https://kuji.kotobukiya.co.jp"]

    product_url_prefix = 'https://kuji.kotobukiya.co.jp/'
    product_url_template = product_url_prefix + 'lp/%s'

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
        try:
            page_url = cls.product_url_template % page
            if not page_url.endswith('/'):
                page_url += '/'
                soup = cls.get_soup(page_url)
                if soup is None:
                    print(f'[ERROR] {page_url} does not exists.')
                    return
                images = soup.select('.prizeList img[src],.kvArea .pcOnly img[src],.specialimage img[src]')
                if len(images) == 0:
                    print(f'[ERROR] {page_url} does not exists.')
                    return
                for image in images:
                    image_url = page_url + image['src']
                    img_name = image['src'].split('/')[-1]
                    cls.download_image(image_url, page + '/' + img_name)
        except Exception as e:
            print(f'[ERROR] Error in processing {page}: {e}')
