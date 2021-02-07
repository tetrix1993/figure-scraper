from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool


class Granup(Website):
    base_folder = constants.FOLDER_GRANUP
    title = constants.WEBSITE_TITLE_GRANUP
    keywords = ["https://granup.shop/"]

    page_prefix = 'https://granup.shop/'
    product_url_template = page_prefix + 'products/detail/%s'
    load_item_url_template = page_prefix + 'products/list?orderby=2&pageno=%s'
    load_item_category_url_template = page_prefix + 'products/list?category_id=%s&pageno=%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('2: Download by Categories')
            print('3: Download Items from Main Page')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                elif choice == 2:
                    cls.download_by_categories()
                elif choice == 3:
                    cls.download_from_main_page()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://granup.shop/products/detail/{product_id}/')
        expr = input('Enter product IDs (expression): ')
        if len(expr) == 0:
            return
        product_ids = cls.get_numbers_from_expression(expr)
        if len(product_ids) == 0:
            return

        result = cls.get_use_jan_choice()
        use_jan = False
        if result == 1:
            use_jan = True
        elif result == -1:
            return

        for product_id in product_ids:
            cls.process_product_page(str(product_id), constants.SUBFOLDER_GRANUP_IMAGES, use_jan)

    @classmethod
    def download_by_categories(cls):
        print('[INFO] URL is in the form: https://granup.shop/products/list?category_id={category_id}&pageno={page_no}')
        category_expr = input('Enter category IDs (expression): ')
        if len(category_expr) == 0:
            return
        categories = cls.get_sorted_page_numbers(category_expr)
        if len(categories) == 0:
            return

        expr = input('Enter page numbers to download (expression): ')
        if len(expr) == 0:
            return
        numbers = cls.get_sorted_page_numbers(expr, start_from=1)
        if len(numbers) == 0:
            return
        jan_result = cls.get_use_jan_choice()
        use_jan = False
        if jan_result == 1:
            use_jan = True
        elif jan_result == -1:
            return

        base_folder = constants.SUBFOLDER_GRANUP_CATEGORY
        if len(categories) == 1 and len(numbers) == 1:
            url = cls.load_item_category_url_template % (str(categories[0]), str(numbers[0]))
            product_ids = cls.get_product_ids_from_load_items_page(url)
            if len(product_ids) == 0:
                print('[ERROR] No items found on page %s' % str(numbers[0]))
                return
            else:
                folder = base_folder + '/' + categories[0]
                cls.process_product_pages(product_ids, folder, use_jan)
        else:
            max_processes = constants.MAX_PROCESSES
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for category in categories:
                    for number in numbers:
                        url = cls.load_item_category_url_template % (str(category), str(number))
                        product_ids = cls.get_product_ids_from_load_items_page(url)
                        if len(product_ids) == 0:
                            print('[ERROR] No items found on page %s for category %s' % (str(number), str(category)))
                            break
                        else:
                            folder = base_folder + '/' + str(category)
                            result = p.apply_async(cls.process_product_pages, (product_ids, folder, use_jan))
                            results.append(result)
                for result in results:
                    result.wait()

    @classmethod
    def download_from_main_page(cls):
        expr = input('Enter page numbers to download (expression): ')
        if len(expr) == 0:
            return
        numbers = cls.get_sorted_page_numbers(expr, start_from=1)
        if len(numbers) == 0:
            return
        jan_result = cls.get_use_jan_choice()
        use_jan = False
        if jan_result == 1:
            use_jan = True
        elif jan_result == -1:
            return

        folder = constants.SUBFOLDER_GRANUP_IMAGES
        if len(numbers) == 1:
            url = cls.load_item_url_template % str(numbers[0])
            product_ids = cls.get_product_ids_from_load_items_page(url)
            if len(product_ids) == 0:
                print('[ERROR] No items found on page %s' % str(numbers[0]))
                return
            else:
                cls.process_product_pages(product_ids, folder, use_jan)
        else:
            max_processes = constants.MAX_PROCESSES
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for number in numbers:
                    url = cls.load_item_url_template % str(number)
                    product_ids = cls.get_product_ids_from_load_items_page(url)
                    if len(product_ids) == 0:
                        print('[ERROR] No items found on page %s' % str(number))
                        break
                    result = p.apply_async(cls.process_product_pages, (product_ids, folder, use_jan))
                    results.append(result)
                for result in results:
                    result.wait()

    @classmethod
    def get_use_jan_choice(cls):
        while True:
            print('Select name of file to save as: ')
            print('1: Use Product ID as name')
            print('2: Use JAN code as name if possible')
            print('0: Return')

            try:
                choice = int(input('Enter choice: ').strip())
                if choice == 1:
                    return 0
                elif choice == 2:
                    return 1
                elif choice == 0:
                    return -1
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

    @classmethod
    def process_product_page(cls, product_id, folder, use_jan=False):
        product_url = cls.product_url_template % product_id
        image_name_prefix = product_id
        try:
            soup = cls.get_soup(product_url)
            divs = soup.find_all('div', class_='slide-item')
            if len(divs) == 0:
                print('[ERROR] Product ID %s not found.' % product_id)
                return
            if use_jan:
                jan_code = cls.get_jan_code(soup)
                if len(jan_code) > 0:
                    image_name_prefix = jan_code
            num_max_length = len(str(len(divs)))
            for i in range(len(divs)):
                image = divs[i].find('img')
                if image.has_attr('src'):
                    image_url = cls.page_prefix + image['src']
                    if len(divs) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, folder + '/' + image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def process_product_pages(cls, product_ids, folder, use_jan=False):
        for product_id in product_ids:
            cls.process_product_page(product_id, folder, use_jan)

    @classmethod
    def get_product_ids_from_load_items_page(cls, url):
        product_ids = []
        try:
            soup = cls.get_soup(url)
            lis = soup.find_all('li', class_='ec-shelfGrid__item')
            for li in lis:
                a_tag = li.find('a')
                if a_tag and a_tag.has_attr('href'):
                    product_id = a_tag['href'].split('/')[-1]
                    product_ids.append(product_id)
        except Exception as e:
            print('[ERROR] Error in processing %s' % url)
            print(e)
        return product_ids

    @staticmethod
    def get_jan_code(soup):
        result = ''
        span = soup.find('span', class_='product-code-default')
        if span:
            text = span.text.strip()
            if len(text) > 0:
                result = text
        return result
