from figure_scraper.website import Website
import figure_scraper.constants as constants


class Crysto(Website):
    base_folder = constants.FOLDER_CRYSTO
    title = constants.WEBSITE_TITLE_CRYSTO
    keywords = ["https://www.crysto.jp/view/category/5hanayome"]

    product_url_prefix = 'https://www.crysto.jp/view/category/%s?page='

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            category = input('Enter category name: ')
            if len(category) == 0:
                return
            num_page = input('Enter number of page: ')
            if not num_page.isnumeric() or int(num_page) < 1:
                continue
            cls.process_category(category, int(num_page))

    @classmethod
    def process_category(cls, category, num_page):
        page_url = cls.product_url_prefix % category
        folder = constants.SUBFOLDER_CRYSTO_CATEGORY + '/' + category
        try:
            for i in range(num_page):
                category_url = page_url + str(i + 1)
                soup = cls.get_soup(category_url)
                images = soup.select('.product-image img[src]')
                if len(images) == 0:
                    print(f'[ERROR] {category_url} does not exists.')
                    return
                for image in images:
                    image_url = image['src']
                    image_name = image_url.split('/')[-1]
                    cls.download_image(image_url, folder + '/' + image_name)
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
