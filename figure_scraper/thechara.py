from figure_scraper.website import Website
import figure_scraper.constants as constants


class TheChara(Website):
    base_folder = constants.FOLDER_THECHARA
    title = constants.WEBSITE_TITLE_THECHARA
    keywords = ["https://www.the-chara.com/"]

    url_prefix = 'https://www.the-chara.com/'
    search_url_template = url_prefix + 'view/search?search_category=%s'
    search_pageno_template = url_prefix + 'view/search?page=%s&search_category=%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] ' + cls.search_url_template)
            expr = input('Enter page name: ')
            if len(expr) == 0:
                return

            cls.process_product_page(expr)

    @classmethod
    def process_product_page(cls, page):
        page_url = cls.search_url_template % page
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        pageno = 1
        while pageno <= 20:
            try:
                if pageno > 1:
                    page_url = cls.search_pageno_template % (pageno, page)
                soup = cls.get_soup(page_url, headers=headers)
                images = soup.select('.p-itemCard__thumb img[src]')
                if len(images) == 0:
                    print(f'[ERROR] {page_url} does not exists.')
                    return
                for image in images:
                    image_url = image['src']
                    image_name = image_url.split('/')[-1]
                    cls.download_image(image_url, page + '/' + image_name)
                page_elems = soup.select('.p-pagination__item a[href]')
                has_next_page = False
                for elem in page_elems:
                    try:
                        if pageno < int(elem.text):
                            has_next_page = True
                            break
                    except:
                        continue
                if not has_next_page:
                    break
            except Exception as e:
                print(f'[ERROR] Error in processing {page_url}: {e}')
            pageno += 1
