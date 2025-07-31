from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import time
import os


class HobbyStock(Website):
    base_folder = constants.FOLDER_HOBBYSTOCK
    title = constants.WEBSITE_TITLE_HOBBYSTOCK
    keywords = ["http://www.hobbystock.jp/"]

    product_url_template = 'http://www.hobbystock.jp/item/view/%s'
    image_url_full_template = 'https://s3-ap-northeast-1.amazonaws.com/hobbystock/img/item/%s/pc_detail_0.jpg'
    image_url_thumb_template = 'https://s3-ap-northeast-1.amazonaws.com/hobbystock/img/item/%s/pc_thumbnail.jpg'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('2: Download by Image ID')
            print('0: Exit')
            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.process_by_product_id()
                elif choice == 2:
                    cls.process_by_image_id()
                elif choice == 0:
                    return
                else:
                    print('[ERROR] Invalid option.')
                    continue
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def process_by_product_id(cls):
        print('[INFO] Product Page URL is in the format: http://www.hobbystock.jp/item/view/{prefix}-{id}')
        prefix = input('Enter prefix (e.g. hso-ccg): ').strip().lower()
        if len(prefix) == 0:
            return
        expr = input('Enter expression (Product IDs): ').strip()
        if len(expr) == 0:
            return
        unfiltered_numbers = cls.get_numbers_from_expression(expr)
        today = cls.get_today_date()
        numbers = []
        for number in unfiltered_numbers:
            product_id = prefix + '-' + str(number).zfill(8)
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
            scan_output_file = constants.FILE_HOBBYSTOCK_SCAN_OUTPUT % today
            print('The result of the scan is saved at: %s' % scan_output_file)
            temp_folder = cls.base_folder + '/' + constants.SUBFOLDER_HOBBYSTOCK_TEMP
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            if len(numbers) == 1:
                cls.scan_product_page(prefix, numbers[0])
            else:
                max_processes = min(constants.MAX_PROCESSES, len(numbers))
                if max_processes <= 0:
                    max_processes = 1
                with Pool(max_processes) as p:
                    results = []
                    for number in numbers:
                        result = p.apply_async(cls.scan_product_page, (prefix, number,))
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
            cls.process_product_page(prefix, numbers[0], today, use_jan)
        elif len(numbers) > 1:
            max_processes = min(constants.MAX_PROCESSES, len(numbers))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for number in numbers:
                    result = p.apply_async(cls.process_product_page, (prefix, number, today, use_jan))
                    results.append(result)
                    time.sleep(constants.PROCESS_SPAWN_DELAY)
                for result in results:
                    result.wait()

    @classmethod
    def process_product_page(cls, prefix, product_id, folder=None, use_jan=False):
        id_ = prefix + '-' + str(product_id).zfill(8)
        product_url = cls.product_url_template % id_
        jan_code = id_
        try:
            soup = cls.get_soup(product_url)
            images = soup.select('.productMainBox__left img[src]')
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
    def scan_product_page(cls, prefix, product_id):
        id_ = prefix + '-' + str(product_id).zfill(8)
        product_url = cls.product_url_template % id_
        if not os.path.exists(constants.SUBFOLDER_HOBBYSTOCK_SCAN):
            os.makedirs(constants.SUBFOLDER_HOBBYSTOCK_SCAN)
        try:
            soup = cls.get_soup(product_url)
            title, jan = cls.get_title_and_code(soup)
            if len(title) == 0 or len(jan) == 0:
                print('[ERROR] Product ID %s does not exists.' % str(id_))
                return
            filepath = cls.base_folder + '/' + constants.SUBFOLDER_HOBBYSTOCK_TEMP + '/' + str(product_id)
            with open(filepath, 'a+', encoding='utf-8') as f:
                f.write('%s\t%s\t%s' % (str(id_), jan, title))
            print('Processed %s' % product_url)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)

    @classmethod
    def process_by_image_id(cls):
        is_thumbnail = False
        while True:
            print('[INFO] Select an option: ')
            print('1: Download full image')
            print('2: Download thumbnail')
            print('0: Return')
            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 0:
                    return
                elif choice != 1 and choice != 2:
                    print('[ERROR] Invalid option.')
                    continue
            except:
                print('[ERROR] Invalid option.')
                continue
            if choice == 1:
                image_url_template = cls.image_url_full_template
                break
            elif choice == 2:
                is_thumbnail = True
                image_url_template = cls.image_url_thumb_template
                break
            else:
                continue

        expr = input('Enter expression (Image IDs): ').strip()
        if len(expr) == 0:
            return
        unfiltered_numbers = cls.get_numbers_from_expression(expr)
        today = cls.get_today_date()
        numbers = []
        for number in unfiltered_numbers:
            image_id = str(number).zfill(11)
            filepath = today + '/' + image_id
            if cls.is_image_exists(filepath, has_extension=True) \
                    or cls.is_image_exists(filepath + '_1', has_extension=True) \
                    or cls.is_image_exists(filepath + '_01', has_extension=True):
                print(f'[INFO] Image ID {image_id} already downloaded')
                continue
            numbers.append(number)
        if len(numbers) == 1:
            image_id = str(numbers[0]).zfill(11)
            if is_thumbnail:
                image_name = today + '/' + image_id + '_t.jpg'
            else:
                image_name = today + '/' + image_id + '.jpg'
            image_url = image_url_template % image_id
            cls.download_image_by_url(image_name, image_url)
        elif len(numbers) > 1:
            max_processes = min(constants.MAX_PROCESSES, len(numbers))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for number in numbers:
                    image_id = str(number).zfill(11)
                    if is_thumbnail:
                        image_name = today + '/' + image_id + '_t.jpg'
                    else:
                        image_name = today + '/' + image_id + '.jpg'
                    image_url = image_url_template % image_id
                    result = p.apply_async(cls.download_image_by_url, (image_name, image_url))
                    results.append(result)
                    time.sleep(constants.PROCESS_SPAWN_DELAY)
                for result in results:
                    result.wait()

    @classmethod
    def download_image_by_url(cls, image_name, image_url):
        cls.download_image(image_url, image_name)

    @staticmethod
    def get_jan_code(soup):
        content = soup.select('meta[name="keywords"][content]')
        if len(content) > 0:
            for c in content[0]['content'].split(','):
                text = c.strip()
                if text.isnumeric() and len(text) == 13 and (text.startswith('45') or text.startswith('49')):
                    return text
        return ''

    @staticmethod
    def get_title_and_code(soup):
        content = soup.select('meta[name="keywords"][content]')
        if len(content) > 0:
            split_ = content[0]['content'].split(',')
            for i in range(len(split_)):
                text = split_[i].strip()
                if text.isnumeric() and len(text) == 13 and (text.startswith('45') or text.startswith('49')):
                    title = ''
                    for j in range(i):
                        title += split_[j]
                    return title, text
        return '', ''
