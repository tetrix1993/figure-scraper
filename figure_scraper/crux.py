from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time


class Crux(Website):
    base_folder = constants.FOLDER_CRUX
    title = constants.WEBSITE_TITLE_CRUX
    keywords = ['http://www.crux-onlinestore.com/']

    page_prefix = 'http://www.crux-onlinestore.com'
    product_url_template = page_prefix + '/shopdetail/%s/'
    category_url_template = page_prefix + '/shopbrand/%s/page%s/order/'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product IDs')
            print('2: Download by Category IDs')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                elif choice == 2:
                    cls.download_by_category()
                elif choice == 0:
                    break
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        cls.init()
        print('[INFO] Product Page URL is in the format: http://www.crux-onlinestore.com/shopdetail/{product_id}/')
        expr = input('Enter expression (Product IDs): ').strip()
        if len(expr) == 0:
            return
        numbers = cls.get_sorted_page_numbers(expr, start_from=1)
        if len(numbers) == 1:
            cls.process_product_page(numbers[0], constants.SUBFOLDER_CRUX_IMAGES)
        elif len(numbers) > 1:
            max_processes = constants.MAX_PROCESSES
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for number in numbers:
                    result = p.apply_async(cls.process_product_page, (number, constants.SUBFOLDER_CRUX_IMAGES))
                    results.append(result)
                    time.sleep(constants.PROCESS_SPAWN_DELAY)
                for result in results:
                    result.wait()

    @classmethod
    def download_by_category(cls):
        print('[INFO] Category Page URL is in the format: http://www.crux-onlinestore.com/shopbrand/{prefix}{category_id}/')
        prefix = input('[INFO] Enter prefix (e.g. ct): ').lower()
        if len(prefix) == 0:
            return
        expr = input('Enter expression (Category IDs): ').strip()
        if len(expr) == 0:
            return
        numbers = cls.get_sorted_page_numbers(expr, start_from=1)
        if len(numbers) > 0:
            cls.process_category_pages(prefix, numbers)

    @classmethod
    def process_category_pages(cls, prefix, category_ids):
        max_processes = constants.MAX_PROCESSES
        if max_processes <= 0:
            max_processes = 1
        with Pool(max_processes) as p:
            results = []
            for cat_id in category_ids:
                category_id = prefix + str(cat_id)
                folder = constants.SUBFOLDER_CRUX_CATEGORY + '/' + category_id
                for page in range(1, 101, 1):
                    url = cls.category_url_template % (str(category_id), str(page))
                    try:
                        soup = cls.get_soup(url)
                        if not soup:
                            break
                        inner_lists = soup.find_all('ul', class_='innerList')
                        for inner_list in inner_lists:
                            lis = inner_list.find_all('li')
                            for li in lis:
                                a_tag = li.find('a')
                                if a_tag.has_attr('href'):
                                    split1 = a_tag['href'].split('/')
                                    if len(split1) > 2:
                                        id_ = split1[2]
                                        if cls.is_product_id_processed(id_, folder):
                                            continue
                                        result = p.apply_async(cls.process_product_page, (id_, folder))
                                        results.append(result)
                                        time.sleep(constants.PROCESS_SPAWN_DELAY)
                        if not cls.has_next_page(soup, page + 1):
                            break
                    except Exception as e:
                        print('[ERROR] Error in processing %s' % url)
                        print(e)
            for result in results:
                result.wait()

    @staticmethod
    def has_next_page(soup, next_page):
        pager = soup.find('ul', class_='M_pager')
        if pager:
            next_lis = pager.find_all('li', class_='next')
            if len(next_lis) > 0:
                a_tag = next_lis[-1].find('a')
                if a_tag and a_tag.has_attr('href') and ('page' + str(next_page)) in a_tag['href']:
                    return True
        return False

    @classmethod
    def process_product_page(cls, product_id, folder):
        id_ = str(product_id).zfill(12)
        product_url = cls.product_url_template % id_
        image_name_prefix = folder + '/' + id_
        try:
            soup = cls.get_soup(product_url)
            div = soup.find('div', class_='M_imageMain')
            if not div:
                # Page only has one image
                div = soup.find('div', id='itemImg')
                if not div:
                    print('[ERROR] Product ID %s does not exists.' % str(product_id))
                    return
                image = div.find('img')
                if image:
                    images = [image]
                else:
                    print('[ERROR] Product ID %s does not exists.' % str(product_id))
                    return
            else:
                images = div.find_all('img')
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                if images[i].has_attr('src'):
                    image_url = images[i]['src'].split('?')[0]
                    if len(images) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
