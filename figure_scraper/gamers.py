from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import os


class Gamers(Website):
    base_folder = constants.FOLDER_GAMERS
    title = constants.WEBSITE_TITLE_GAMERS
    keywords = ['https://www.gamers.co.jp/']

    product_url_template = 'https://www.gamers.co.jp/pn/pd/%s/'
    event_url_template = 'https://www.gamers.co.jp/contents/event_fair/detail.php?id=%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('2: Download by Event ID')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                elif choice == 2:
                    cls.download_by_event()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        while True:
            print('[INFO] Product Page URL is in the format: https://www.gamers.co.jp/pn/pd/{product_id}/')
            expr = input('Enter expression (Product IDs): ').strip()
            if len(expr) == 0:
                return
            evaluate = True
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
                        evaluate = False
                        break
                    else:
                        raise Exception
                except:
                    print('[ERROR] Invalid choice.')
            if evaluate:
                numbers = cls.get_sorted_page_numbers(expr)
                today = cls.get_today_date()
                if is_scan:
                    scan_output_file = constants.FILE_GAMERS_SCAN_OUTPUT % today
                    print('The result of the scan is saved at: %s' % scan_output_file)
                    temp_folder = cls.base_folder + '/' + constants.SUBFOLDER_GAMERS_TEMP
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
                    continue

                print('[INFO] Images will be saved at %s' % (cls.base_folder + '/' + today))
                if len(numbers) == 1:
                    cls.process_product_page(numbers[0], use_jan, today)
                elif len(numbers) > 1:
                    max_processes = min(constants.MAX_PROCESSES, len(numbers))
                    if max_processes <= 0:
                        max_processes = 1
                    with Pool(max_processes) as p:
                        results = []
                        for number in numbers:
                            result = p.apply_async(cls.process_product_page, (number, use_jan, today))
                            results.append(result)
                        for result in results:
                            result.wait()

    @classmethod
    def download_by_event(cls):
        while True:
            print('[INFO] Event URL is in the format: https://www.gamers.co.jp/contents/event_fair/detail.php?id={event_id}')
            event_id = input('Enter Event ID: ')
            if len(event_id.strip()) == 0:
                return
            folder = constants.SUBFOLDER_GAMERS_EVENT + '/' + event_id
            if not os.path.exists(folder):
                os.makedirs(folder)
            event_url = cls.event_url_template % event_id
            print('Processing ' + event_url)
            try:
                soup = cls.get_soup(event_url)
                images = soup.select('.fairevent_img img[src],.fairevent_detail_content img[src]')
                for image in images:
                    image_url = image['src']
                    if 'resize_image.php?image=' in image_url:
                        image_url = 'https://www.gamers.co.jp/upload/save_image/' + image_url.split('?image=')[-1]
                    elif image_url.startswith('/'):
                        image_url = 'https://www.gamers.co.jp' + image_url
                    image_name = image_url.split('/')[-1]
                    cls.download_image(image_url, 'event/' + event_id + '/' + image_name)
            except Exception as e:
                print('[ERROR] Error in processing %s' % event_url)
                print(e)

    @classmethod
    def process_product_page(cls, product_id, use_jan=False, folder=None):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        image_name_prefix = id_
        try:
            soup = cls.get_soup(product_url)
            ul = soup.find('ul', class_='item_img_main')
            if not ul:
                print('[ERROR] Product ID %s does not exists.' % id_)
                return
            if use_jan:
                jan_code = cls.get_jan_code(soup)
                if len(jan_code) > 0:
                    image_name_prefix = jan_code
            images = ul.find_all('img')
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                if images[i].has_attr('src'):
                    image_url = images[i]['src']
                    if len(images) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
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
        p_tags = soup.select('.item_detail_txt.pc p')
        if len(p_tags) > 0:
            content = p_tags[0].text
            stop = False
            for i in content:
                if i.isnumeric():
                    result += i
                    stop = True
                elif stop:
                    break
        return result

    @staticmethod
    def get_product_title(soup):
        result = ''
        span = soup.select('h1')
        if len(span) > 0:
            result = span[0].text
        return result

    @classmethod
    def scan_product_page(cls, product_id):
        id_ = str(product_id)
        product_url = cls.product_url_template % id_
        if not os.path.exists(constants.SUBFOLDER_GAMERS_SCAN):
            os.makedirs(constants.SUBFOLDER_GAMERS_SCAN)
        try:
            soup = cls.get_soup(product_url)
            title = cls.get_product_title(soup)
            jan = cls.get_jan_code(soup)
            if len(title) == 0 or len(jan) == 0:
                print('[ERROR] Product ID %s does not exists.' % str(product_id))
                return
            filepath = cls.base_folder + '/' + constants.SUBFOLDER_GAMERS_TEMP + '/' + str(product_id)
            with open(filepath, 'a+', encoding='utf-8') as f:
                f.write('%s\t%s\t%s' % (str(product_id), jan, title))
            print('Processed %s' % product_url)
        except Exception as e:
            print('[ERROR] Error in processing %s' % product_url)
            print(e)
