from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class CurtainDamashii(Website):
    base_folder = constants.FOLDER_CURTAIN_DAMASHII
    title = constants.WEBSITE_TITLE_CURTAIN_DAMASHII
    keywords = ["https://www.curtain-damashii.com/"]

    page_prefix = 'https://www.curtain-damashii.com/'
    product_url_template = page_prefix + 'item/%s/'
    tag_url_template = page_prefix + 'item/tag/%s/'
    event_url_template = page_prefix + 'event/%s/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('2: Download by Tag')
            print('3: Download by Event')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                elif choice == 2:
                    cls.download_by_tag()
                elif choice == 3:
                    cls.download_by_event()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://www.curtain-damashii.com/item/{product_id}/')
        input_str = input('Enter product IDs (if multiple, separate by comma): ')
        if len(input_str) == 0:
            return
        product_ids = input_str.split(',')
        for product_id in product_ids:
            if len(product_id) > 0:
                cls.process_product_page(product_id, constants.SUBFOLDER_CURTAIN_DAMASHII_IMAGES)

    @classmethod
    def download_by_tag(cls):
        print('[INFO] URL is in the form: https://www.curtain-damashii.com/item/{product_id}/')
        input_str = input('Enter product IDs (if multiple, separate by comma): ')
        if len(input_str) == 0:
            return
        tags = input_str.split(',')
        valid_tags = []
        for tag in tags:
            if len(tag) > 0:
                valid_tags.append(tag)
        if len(valid_tags) == 0:
            return
        elif len(valid_tags) == 1:
            cls.process_tag_page(valid_tags[0], constants.SUBFOLDER_CURTAIN_DAMASHII_TAG)
        else:
            cls.process_tag_pages(valid_tags)

    @classmethod
    def download_by_event(cls):
        print('[INFO] URL is in the form https://www.curtain-damashii.com/event/{event_id}/')
        event_id = input('Enter event ID: ')
        if len(event_id) == 0:
            return
        cls.process_event_page(event_id)

    @classmethod
    def process_product_page(cls, product_id, folder):
        product_url = cls.product_url_template % product_id
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='leftBox')
            if not div:
                print('[INFO] Product ID %s not found.' % product_id)
                return
            images = div.find_all('img')
            for image in images:
                if image.has_attr('src'):
                    image_url = image['src']
                    image_name = folder + '/' + image_url.split('/')[-1]
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def process_tag_page(cls, tag, folder):
        tag_url = cls.tag_url_template % tag
        try:
            soup = cls.get_soup(tag_url)
            articles = soup.find_all('article')
            if len(articles) == 0:
                print('[INFO] Tag ID %s not found.' % tag)
                return
            for article in articles:
                a_tag = article.find('a')
                if a_tag.has_attr('href'):
                    product_url = a_tag['href']
                    if product_url[-1] == '/':
                        product_id = product_url.split('/')[-2]
                    else:
                        product_id = product_url.split('/')[-1]
                    save_folder = folder + '/' + tag
                    cls.process_product_page(product_id, save_folder)
            print('[INFO] Tag %s has been processed.' % tag)
        except Exception as e:
            print('[ERROR] Error in processing %s' % tag)
            print(e)

    @classmethod
    def process_tag_pages(cls, tags):
        max_processes = constants.MAX_PROCESSES
        if max_processes <= 0:
            max_processes = 1
        with Pool(max_processes) as p:
            results = []
            for tag in tags:
                result = p.apply_async(cls.process_tag_page, (tag, constants.SUBFOLDER_CURTAIN_DAMASHII_TAG))
                results.append(result)
            for result in results:
                result.wait()
        print('[INFO] All tags have been processed.')

    @classmethod
    def process_event_page(cls, event):
        event_url = cls.event_url_template % event
        try:
            soup = cls.get_soup(event_url)
            h2 = soup.find('h2', class_='anime-title')
            if h2 is None or not h2.has_attr('id'):
                print("[INFO] Event %s can't be processed." % event)
                return

            max_processes = constants.MAX_PROCESSES
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                next_tag = h2.next_sibling
                series = h2['id']
                product_ids = []
                while next_tag.next_sibling:
                    if next_tag.name == 'div' and next_tag.has_attr('class') and 'itemListBox' in next_tag['class']:
                        a_tag = next_tag.find('a')
                        if a_tag and a_tag.has_attr('href'):
                            product_url = a_tag['href']
                            if product_url[-1] == '/':
                                product_id = product_url.split('/')[-2]
                            else:
                                product_id = product_url.split('/')[-1]
                            product_ids.append(product_id)
                    elif next_tag.name == 'h2':
                        result = p.apply_async(cls.process_event_page_by_series, (event, series, product_ids))
                        results.append(result)
                        if next_tag.has_attr('id'):
                            series = next_tag['id']
                        product_ids = []
                    next_tag = next_tag.next_sibling
                if len(product_ids) > 0:
                    result = p.apply_async(cls.process_event_page_by_series, (event, series, product_ids))
                    results.append(result)
                for result in results:
                    result.wait()
            print('[INFO] Event %s has been processed' % event)
        except Exception as e:
            print('[ERROR] Error in processing %s' % event)
            print(e)

    @classmethod
    def process_event_page_by_series(cls, event, series, product_ids):
        for product_id in product_ids:
            save_folder = '%s/%s/%s' % (constants.SUBFOLDER_CURTAIN_DAMASHII_EVENT, event, series)
            cls.process_product_page(product_id, save_folder)
