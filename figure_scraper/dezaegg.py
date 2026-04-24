from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import os


class Dezaegg(Website):
    base_folder = constants.FOLDER_DEZAEGG
    title = constants.WEBSITE_TITLE_DEZAEGG
    keywords = ["http://dezaegg.com/", "Dezaegg", "License Agent"]

    page_prefix = 'http://dezaegg.com'
    product_url_template = page_prefix + '/products/detail.php?product_id=%s'

    @classmethod
    def run(cls):
        cls.init()
        loop = True
        while loop:
            print('[INFO] %s Scraper' % cls.title)
            loop = cls.download_by_product_id()

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: http://dezaegg.com/products/detail.php?product_id={product_id}')
        expr = input('Enter product IDs: ')
        if len(expr) == 0:
            return False
        numbers = cls.get_sorted_page_numbers(expr)
        if len(numbers) == 0:
            return True

        use_jan = False
        is_scan = False
        while True:
            print('Select name of file to save as: ')
            print('1: Use Product ID as name')
            print('2: Use JAN code as name if possible')
            print('3: Scan for JAN code instead of downloading images')
            print('0: Return')

            try:
                choice = int(input('Enter choice: ').strip())
                if choice == 1:
                    break
                elif choice == 2:
                    use_jan = True
                    break
                elif choice == 3:
                    is_scan = True
                    break
                elif choice == 0:
                    return True
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

        today = cls.get_today_date()
        if is_scan:
            scan_output_file = constants.FILE_DEZAEGG_SCAN_OUTPUT % today
            print('The result of the scan is saved at: %s' % scan_output_file)
            temp_folder = cls.base_folder + '/' + constants.SUBFOLDER_DEZAEGG_TEMP
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            if len(numbers) == 1:
                cls.scan_product_page(numbers[0])
            else:
                max_processes = min(cls.max_processes, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.scan_product_page, (number,))
                        results.append(result)
                    for result in results:
                        result.wait()

            item_list = []
            for number in numbers:
                filepath = temp_folder + '/' + str(number)
                if os.path.exists(filepath):
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            line = f.readline()
                            split1 = line.replace('\n', '').split('\t')
                            if len(split1) == 3:
                                item_list.append({'id': split1[0], 'jan': split1[1], 'title': split1[2]})
            with open(scan_output_file, 'a+', encoding='utf-8') as f:
                for item in item_list:
                    f.write('%s\t%s\t%s\n' % (item['id'], item['jan'], item['title']))
            for number in numbers:
                filepath = temp_folder + '/' + str(number)
                if os.path.exists(filepath):
                    os.remove(filepath)
            if os.path.exists(temp_folder):
                os.removedirs(temp_folder)
            return True
        if len(numbers) == 1:
            cls.process_product_page(numbers[0], use_jan, today)
        else:
            max_processes = min(cls.max_processes, len(numbers))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for product_id in numbers:
                    result = p.apply_async(cls.process_product_page, (product_id, use_jan, today))
                    results.append(result)
                for result in results:
                    result.wait()
        return True

    @classmethod
    def process_product_page(cls, product_id, use_jan=False, folder=None):
        product_url = cls.product_url_template % product_id
        image_name_prefix = product_id
        try:
            soup = cls.get_soup(product_url)
            if use_jan:
                jan_code = cls.get_jan_code(soup)
                if len(jan_code) > 0:
                    image_name_prefix = jan_code
            images = soup.select('div.photo a')
            if len(images) == 0:
                print('[ERROR] Product ID %s not found.' % product_id)
                return
            elif len(images) == 1:
                image_url = cls.page_prefix + images[0]['href']
                image_name = image_name_prefix + '.jpg'
                if folder:
                    image_name = folder + '/' + image_name
                cls.download_image(image_url, image_name)
            else:
                num_max_length = len(str(len(images)))
                for i in range(len(images)):
                    image_url = cls.page_prefix + images[i]['href']
                    image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    if folder:
                        image_name = folder + '/' + image_name
                    cls.download_image(image_url, image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @staticmethod
    def get_jan_code(soup):
        result = ''
        elem = soup.select('p.jan_code')
        if len(elem) > 0:
            result = elem[0].text.strip()
        return result

    @staticmethod
    def get_product_name(soup):
        result = ''
        elem = soup.select('h1.title')
        if len(elem) > 0:
            result = elem[0].text.strip()
        return result

    @classmethod
    def scan_product_page(cls, product_id):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        if not os.path.exists(constants.SUBFOLDER_DEZAEGG_SCAN):
            os.makedirs(constants.SUBFOLDER_DEZAEGG_SCAN)
        try:
            soup = cls.get_soup(product_url)
            jan = cls.get_jan_code(soup)
            name = cls.get_product_name(soup)
            if name is None or jan is None:
                print('[ERROR] Product ID %s does not exists.' % str(product_id))
                return
            filepath = cls.base_folder + '/' + constants.SUBFOLDER_DEZAEGG_TEMP + '/' + str(product_id)
            with open(filepath, 'a+', encoding='utf-8') as f:
                f.write('%s\t%s\t%s' % (str(product_id), jan, name))
            print('Processed %s' % product_url)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
