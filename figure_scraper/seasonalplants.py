from figure_scraper.website import Website
import figure_scraper.constants as constants


class SeasonalPlants(Website):
    base_folder = constants.FOLDER_SEASONALPLANTS
    title = constants.WEBSITE_TITLE_SEASONALPLANTS
    keywords = ["http://www.seasonal-plants.co.jp/"]

    event_page_template = 'http://www.seasonal-plants.co.jp/event/%s/'
    product_page_prefix = 'https://seasonalplants.shop-pro.jp/?pid='
    cbid_template = 'https://seasonalplants.shop-pro.jp/?mode=cate&cbid=%s&csid=0'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Event ID')
            print('2: Download by cbid')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.process_event_page()
                elif choice == 2:
                    cls.process_by_cbid()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def process_event_page(cls):
        print('Event page url template: ' + cls.event_page_template)
        page = input('Enter event page name: ')
        if len(page) == 0:
            return

        event_page_prefix = cls.event_page_template % page
        page_url = event_page_prefix + 'index.html'
        try:
            soup = cls.get_soup(page_url)
            images = soup.select('.galleryList img[src^="goods/"]')
            if len(images) == 0:
                print(f'[ERROR] {page_url} does not exists.')
                return
            for image in images:
                image_url = event_page_prefix + image['src']
                image_name = image['src'].split('/')[-1]
                cls.download_image(image_url, constants.SUBFOLDER_SEASONALPLANTS_EVENT + '/' + page + '/' + image_name)
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')

    @classmethod
    def process_by_cbid(cls):
        print('Template: ' + cls.cbid_template)
        cbid = input('Enter cbid: ')
        if len(cbid) == 0:
            return
        use_jan_code_choice = input('Use JAN code is possible (y/n)? ')
        use_jan_code = use_jan_code_choice.lower() == 'y'

        prefix = cls.cbid_template % cbid
        page_num = 0
        save_folder = constants.SUBFOLDER_SEASONALPLANTS_CBID + '/' + cls.get_today_date()
        try:
            while True:
                page_num += 1
                print(f'Loading page {page_num}...')
                cbid_url = prefix if page_num == 1 else prefix + f'&page={page_num}'
                soup = cls.get_soup(cbid_url)
                items = soup.select('.productlist-list .product-list__unit')
                pids = []
                for item in items:
                    a_tags = item.select('a[href]')
                    if len(a_tags) == 0:
                        continue
                    pids.append(a_tags[0]['href'].split('=')[-1])

                print('Select pids to download: ')
                for i in range(len(pids)):
                    print(f'{i} - {pids[i]}')
                expr = input('Enter expression (e.g. 1-3,4): ')
                if len(expr) > 0:
                    idxs = cls.get_numbers_from_expression(expr)
                    for idx in idxs:
                        if idx < len(pids):
                            cls.process_product_page(pids[idx], save_folder, use_jan_code)

                if cls.has_next_page(soup):
                    next_page_choice = input(f'Load page {page_num + 1} (y/n)? ')
                    if next_page_choice.lower() != 'y':
                        break
                else:
                    break
        except:
            print('[ERROR] Error encountered')

    @classmethod
    def has_next_page(cls, soup):
        return soup is not None and len(soup.select('.pagenation-next a[href]')) > 0

    @classmethod
    def process_product_page(cls, pid, save_folder, use_jan_code=False):
        url = cls.product_page_prefix + pid
        try:
            soup = cls.get_soup(url)
            if use_jan_code:
                jan_code = cls.get_jan_code(soup)
                image_name = pid if jan_code is None or len(jan_code) == 0 else jan_code
            else:
                image_name = pid
            images = soup.select('.product__image-main img[src]')
            for i in range(len(images)):
                if len(images) == 1:
                    final_image_name = image_name
                else:
                    final_image_name = f'{image_name}_{i + 1}'
                image_url = images[i]['src']

                image_url_split = image_url.split('?')[0]
                image_ext_idx = image_url_split.rfind('.')
                if 0 < image_ext_idx < len(image_url_split) - 1:
                    image_ext = image_url_split[image_ext_idx + 1:]
                    if len(image_ext) > 0:
                        final_image_name += '.' + image_ext.lower()
                cls.download_image(image_url, save_folder + '/' + final_image_name)
        except:
            print(f'[ERROR] Error encountered when loading {url}')

    @classmethod
    def get_jan_code(cls, soup):
        if soup is None:
            return None
        try:
            return soup.select('.product__model')[0].text.strip()
        except:
            return None
