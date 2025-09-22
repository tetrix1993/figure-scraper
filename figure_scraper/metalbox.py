from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time
import os


class MetalBox(Website):
    base_folder = constants.FOLDER_METALBOX
    title = constants.WEBSITE_TITLE_METALBOX
    keywords = ["https://www.metal-box.jp/"]

    product_url_template = 'https://www.metal-box.jp/product_detail/%s'

    @classmethod
    def run(cls):
        cls.init()
        cls.process_by_product_id()

        '''
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('0: Exit')
            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.process_by_product_id()
                elif choice == 0:
                    return
                else:
                    print('[ERROR] Invalid option.')
                    continue
            except:
                print('[ERROR] Invalid option.')
        '''

    @classmethod
    def process_by_product_id(cls):
        print('[INFO] Product Page URL is in the format: https://www.metal-box.jp/product_detail/{id}')
        expr = input('Enter expression (Product IDs): ').strip()
        if len(expr) == 0:
            return
        unfiltered_numbers = cls.get_numbers_from_expression(expr)
        today = cls.get_today_date()
        numbers = []
        for number in unfiltered_numbers:
            product_id = str(number)
            filepath = today + '/' + product_id
            if cls.is_image_exists(filepath, has_extension=True) \
                    or cls.is_image_exists(filepath + '_1', has_extension=True) \
                    or cls.is_image_exists(filepath + '_01', has_extension=True):
                print(f'[INFO] Product ID {product_id} already downloaded')
                continue
            numbers.append(number)

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
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid choice.')

        if is_scan:
            scan_output_file = constants.FILE_METALBOX_SCAN_OUTPUT % today
            print('The result of the scan is saved at: %s' % scan_output_file)
            temp_folder = cls.base_folder + '/' + constants.SUBFOLDER_METALBOX_TEMP
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            if len(numbers) == 1:
                cls.scan_product_page(numbers[0])
            else:
                max_processes = min(constants.MAX_PROCESSES, len(numbers))
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
            return

        if len(numbers) == 1:
            cls.process_product_page(numbers[0], today, use_jan)
        elif len(numbers) > 1:
            max_processes = min(constants.MAX_PROCESSES, len(numbers))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for number in numbers:
                    result = p.apply_async(cls.process_product_page, (number, today, use_jan))
                    results.append(result)
                    time.sleep(constants.PROCESS_SPAWN_DELAY)
                for result in results:
                    result.wait()

    @classmethod
    def process_product_page(cls, product_id, folder=None, use_jan=False):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        jan_code = id_
        try:
            soup = cls.get_soup(product_url, verify=False)
            images = soup.select('#detail_image_box__slides img[src]')
            if use_jan:
                jan_code = cls.get_jan_code(soup)
            image_urls = set()
            for image in images:
                image_urls.add(image['src'].split('?')[0])
            if len(image_urls) > 0:
                num_max_length = len(str(len(image_urls)))
                i = 0
                for image_url in image_urls:
                    i += 1
                    id__ = (jan_code if use_jan else id_)
                    if len(image_urls) == 1:
                        image_name = id__ + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (id__, str(i).zfill(num_max_length))
                    if folder:
                        image_name = folder + '/' + image_name
                    cls.download_image(image_url, image_name)
            else:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return

        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def scan_product_page(cls, product_id):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        if not os.path.exists(constants.SUBFOLDER_METALBOX_SCAN):
            os.makedirs(constants.SUBFOLDER_METALBOX_SCAN)
        try:
            soup = cls.get_soup(product_url, verify=False)
            title = cls.get_title(soup)
            jan = cls.get_jan_code(soup)
            if len(title) == 0 or len(jan) == 0:
                print('[ERROR] Product ID %s does not exists.' % str(id_))
                return
            filepath = cls.base_folder + '/' + constants.SUBFOLDER_METALBOX_TEMP + '/' + str(product_id)
            with open(filepath, 'a+', encoding='utf-8') as f:
                f.write('%s\t%s\t%s' % (str(id_), jan, title))
            print('Processed %s' % product_url)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def download_image_by_url(cls, image_name, image_url):
        cls.download_image(image_url, image_name)

    @staticmethod
    def get_jan_code(soup):
        content = soup.select('#jan_code_default')
        if len(content) > 0:
            for c in content[0]:
                text = c.strip()
                if text.isnumeric() and len(text) == 13 and (text.startswith('45') or text.startswith('49')):
                    return text
        return ''

    @staticmethod
    def get_title(soup):
        title_ = soup.select('.item_name')
        if len(title_) > 0:
            return title_[0].text.strip()
        else:
            return ''
