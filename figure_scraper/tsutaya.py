from figure_scraper.website import Website
import figure_scraper.constants as constants


class Tsutaya(Website):
    base_folder = constants.FOLDER_TSUTAYA
    title = constants.WEBSITE_TITLE_TSUTAYA
    keywords = ["https://tsutaya.tsite.jp/"]

    article_url_prefix = 'https://tsutaya.tsite.jp/articles/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter page name (https://tsutaya.tsite.jp/articles/{page}): ')
            if len(expr) == 0:
                return

            cls.process_product_page(expr)

    @classmethod
    def process_product_page(cls, page):
        try:
            page_url = cls.article_url_prefix + page
            soup = cls.get_soup(page_url)
            if soup is None:
                return
            images = []
            header_img = soup.select_one('section>div>div img[data-sd-img-src]')
            if header_img is not None:
                img_ext = header_img['data-sd-img-src'].split('?')[0].split('.')[-1]
                images.append(('main.' + img_ext, header_img['data-sd-img-src']))
            divs = soup.select('#goods>div')
            i = 0
            for div in divs:
                tags = div.select('img[data-sd-img-src]')
                if len(tags) == 0:
                    continue
                i += 1
                for j in range(len(tags)):
                    img_url = tags[j]['data-sd-img-src']
                    img_ext = img_url.split('?')[0].split('.')[-1]
                    img_name = str(i).zfill(2) + '_' + str(j + 1).zfill(2) + '.' + img_ext
                    images.append((img_name, img_url))
            for image in images:
                cls.download_image(image[1], page + '/' + image[0])
        except Exception as e:
            print(f'[ERROR] Error in processing {page}: {e}')
