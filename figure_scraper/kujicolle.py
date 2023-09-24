from figure_scraper.website import Website
import figure_scraper.constants as constants


class Kujicolle(Website):
    base_folder = constants.FOLDER_KUJICOLLE
    title = constants.WEBSITE_TITLE_KUJICOLLE
    keywords = ["https://kujibikido.com"]

    product_url_prefix = 'https://kujico.jp/'
    product_url_template = product_url_prefix + 'detail/%s'

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
        page_url = cls.product_url_template % page
        try:
            soup = cls.get_soup(page_url)
            images = soup.select('.is-half-desktop a[href][data-title]')
            if len(images) == 0:
                print(f'[ERROR] {page_url} does not exists.')
                return
            for image in images:
                image_url = image['href']
                img_name = image['data-title'].strip() + '.jpg'
                number_found = False
                first_idx = -1
                last_idx = -1
                for i in range(len(img_name)):
                    if img_name[i].isnumeric():
                        number_found = True
                        first_idx = i
                    elif number_found and not img_name[i].isnumeric():
                        last_idx = i
                        break
                if first_idx == -1 or last_idx == -1:
                    image_name = img_name
                elif last_idx != -1:
                    image_name = img_name[:last_idx] + '.jpg'
                cls.download_image(image_url, page + '/' + image_name)
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
