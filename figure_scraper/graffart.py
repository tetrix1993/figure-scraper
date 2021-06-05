from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import os
import time


class GraffArt(Website):
    base_folder = constants.FOLDER_GRAFFART
    title = constants.WEBSITE_TITLE_GRAFFART
    keywords = ["https://kyaragoods.shop-pro.jp/", "A3Market Online"]

    page_url_prefix = 'https://kyaragoods.shop-pro.jp/'
    group_page_template = page_url_prefix + '?mode=grp&gid=%s'
    group_sorted_page_template = page_url_prefix + '?mode=grp&gid=%s&sort=n&page=%s'
    product_page_template = page_url_prefix + '?pid=%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product IDs')
            print('2: Download by Group IDs')
            print('3: Scan and download new images based on Group ID of existing folders')
            print('4: Retrieve list of Group ID')
            print('0: Return')

            try:
                choice = int(input('[INFO] Enter choice: '))
                if choice == 1:
                    cls.download_by_product_id()
                elif choice == 2:
                    cls.download_by_group_id()
                elif choice == 3:
                    cls.update_by_group_id()
                elif choice == 4:
                    cls.retrieve_group_ids()
                elif choice == 0:
                    return
                else:
                    raise Exception
            except:
                print('[ERROR] Invalid option.')

    @classmethod
    def download_by_product_id(cls):
        print('[INFO] URL is in the form: https://kyaragoods.shop-pro.jp/?pid={product_id}')
        expr = input('Enter product IDs (expression): ')
        if len(expr) == 0:
            return
        product_ids = cls.get_sorted_page_numbers(expr)
        if len(product_ids) == 0:
            return
        folder = constants.SUBFOLDER_GRAFFART_IMAGES
        if len(product_ids) == 1:
            cls.process_product_page(str(product_ids[0]), folder)
        else:
            max_processes = min(constants.MAX_PROCESSES, len(product_ids))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for product_id in product_ids:
                    result = p.apply_async(cls.process_product_page, (str(product_id), folder))
                    results.append(result)
                for result in results:
                    result.wait()

    @classmethod
    def download_by_group_id(cls):
        print('[INFO] URL is in the form: https://kyaragoods.shop-pro.jp/?mode=grp&gid={group_id}')
        expr = input('Enter group IDs (expression): ')
        if len(expr) == 0:
            return
        group_ids = cls.get_sorted_page_numbers(expr)
        if len(group_ids) == 0:
            return

        result = cls.get_use_jan_choice()
        use_jan = False
        if result == 1:
            use_jan = True
        elif result == -1:
            return

        cls.process_group_pages(group_ids, use_jan)

    @classmethod
    def update_by_group_id(cls):
        jan_result = cls.get_use_jan_choice()
        use_jan = False
        if jan_result == 1:
            use_jan = True
        elif jan_result == -1:
            return

        group_folder = cls.base_folder + '/' + constants.SUBFOLDER_GRAFFART_GROUP
        folders = os.listdir(group_folder)
        group_ids = []
        for folder in folders:
            if os.path.isdir(group_folder + '/' + folder):
                try:
                    group_id = int(folder)
                    group_ids.append(group_id)
                except:
                    continue

        if len(group_ids) == 1:
            cls.process_group_page(group_ids[0], use_jan)
        else:
            max_processes = min(constants.MAX_PROCESSES, len(group_ids))
            if max_processes <= 0:
                max_processes = 1
            with Pool(max_processes) as p:
                results = []
                for group_id in group_ids:
                    result = p.apply_async(cls.process_group_page, (group_id, use_jan))
                    results.append(result)
                for result in results:
                    result.wait()

    @classmethod
    def process_product_page(cls, product_id, folder, jan_code=None):
        url = cls.product_page_template % str(product_id)
        if jan_code:
            image_name_prefix = jan_code
        else:
            image_name_prefix = product_id
        try:
            soup = cls.get_soup(url)
            images = soup.find_all('img', class_='zoom-tiny-image')
            if len(images) == 0:
                print('[ERROR] Product ID %s not found.' % str(product_id))
                return
            num_max_length = len(str(len(images)))
            for i in range(len(images)):
                if images[i].has_attr('src'):
                    image_url = images[i]['src'].split('?')[0]
                    if len(images) == 1:
                        image_name = image_name_prefix + '.jpg'
                    else:
                        image_name = '%s_%s.jpg' % (image_name_prefix, str(i + 1).zfill(num_max_length))
                    cls.download_image(image_url, folder + '/' + image_name)
        except Exception as e:
            print('[ERROR] Error in processing %s' % url)
            print(e)

    @classmethod
    def process_group_pages(cls, group_ids, use_jan=False):
        max_processes = constants.MAX_PROCESSES
        if max_processes <= 0:
            max_processes = 1
        with Pool(max_processes) as p:
            results = []
            for group_id in group_ids:
                folder = constants.SUBFOLDER_GRAFFART_GROUP + '/' + str(group_id)
                for page in range(1, 101, 1):
                    url = cls.group_sorted_page_template % (str(group_id), str(page))
                    try:
                        soup = cls.get_soup(url)
                        divs = soup.find_all('div', class_='item_box')
                        if len(divs) == 0:
                            print('[ERROR] Group ID %s not found.' % str(group_id))
                            break
                        for div in divs:
                            a_tag = div.find('a')
                            if a_tag and a_tag.has_attr('href') and 'pid=' in a_tag['href']:
                                pid = a_tag['href'].split('pid=')[1].strip()
                                jan_code = None
                                if use_jan:
                                    jan_code = cls.get_jan_code(div)
                                result = p.apply_async(cls.process_product_page, (pid, folder, jan_code))
                                results.append(result)
                                time.sleep(constants.PROCESS_SPAWN_DELAY)
                        if not cls.has_next_page(soup, page + 1):
                            break
                    except Exception as e:
                        print('[ERROR] Error in processing %s' % url)
                        print(e)
            for result in results:
                result.wait()

    @classmethod
    def process_group_page(cls, group_id, use_jan=False):
        folder = constants.SUBFOLDER_GRAFFART_GROUP + '/' + str(group_id)
        for page in range(1, 101, 1):
            url = cls.group_sorted_page_template % (str(group_id), str(page))
            try:
                soup = cls.get_soup(url)
                divs = soup.find_all('div', class_='item_box')
                if len(divs) == 0:
                    print('[ERROR] Group ID %s not found.' % str(group_id))
                    break
                for div in divs:
                    a_tag = div.find('a')
                    if a_tag and a_tag.has_attr('href') and 'pid=' in a_tag['href']:
                        pid = a_tag['href'].split('pid=')[1].strip()
                        jan_code = None
                        if use_jan:
                            jan_code = cls.get_jan_code(div)
                        if not cls.is_image_exists_in_group(folder, pid, jan_code):
                            cls.process_product_page(pid, folder, jan_code)
                if not cls.has_next_page(soup, page + 1):
                    break
            except Exception as e:
                print('[ERROR] Error in processing %s' % url)
                print(e)

    @classmethod
    def retrieve_group_ids(cls):
        try:
            temp_folder = cls.base_folder + '/' + constants.SUBFOLDER_GRAFFART_TEMP
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            soup = cls.get_soup(cls.page_url_prefix, get_text=True)
            div = soup.find('div', id='box_group')
            if div:
                a_tags = div.find_all('a')
                max_processes = min(constants.MAX_PROCESSES, len(a_tags))
                if max_processes <= 0:
                    max_processes = 1
                gids = []
                print('[INFO] Processing and creating temporary files...')
                with Pool(max_processes) as p:
                    results = []
                    for a_tag in a_tags:
                        if a_tag.has_attr('href') and 'gid=' in a_tag['href']:
                            gid = a_tag['href'].split('gid=')[1].split('&')[0]
                            if len(gid) > 0:
                                result = p.apply_async(cls.generate_group_id_temp_file, (gid, temp_folder))
                                results.append(result)
                                gids.append(gid)
                    for result in results:
                        result.wait()
                print('[INFO] Reading temporary files for generating list of group ID...')
                gid_list = []
                for gid in gids:
                    filepath = temp_folder + '/' + gid
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            line = f.readline()
                            while line:
                                split1 = line.replace('\n', '').split('\t')
                                if len(split1) == 2:
                                    gid_list.append({'id': split1[0], 'name': split1[1]})
                                line = f.readline()
                print('[INFO] Generating list of group ID...')
                save_file = cls.base_folder + '/' + constants.FILE_GRAFFART_GID_LIST
                with open(save_file, 'w+', encoding='utf-8') as f:
                    for k in sorted(gid_list, key=lambda i: i['id'], reverse=True):
                        f.write(k['id'] + '\t' + k['name'] + '\n')

                print('[INFO] Removing temporary files...')
                for gid in gids:
                    filepath = temp_folder + '/' + gid
                    if os.path.exists(filepath):
                        os.remove(filepath)
                if os.path.exists(temp_folder):
                    os.removedirs(temp_folder)
                print('[INFO] Temporary files removed.')
                print('[INFO] List has been generated at %s' % save_file)
        except Exception as e:
            print('Error in processing %s' % cls.page_url_prefix)
            print(e)

    @classmethod
    def generate_group_id_temp_file(cls, gid, folder):
        url = cls.group_page_template % gid
        filepath = folder + '/' + gid
        try:
            soup = cls.get_soup(url, get_text=True)
            div = soup.find('div', class_='sub_group_area')
            if not div:
                return
            a_tags = div.find_all('a')
            with open(filepath, 'w+', encoding='utf-8') as f:
                for a_tag in a_tags:
                    if a_tag.has_attr('href') and 'gid=' in a_tag['href']:
                        id_ = a_tag['href'].split('gid=')[1].split('&')[0]
                        name = a_tag.text
                        f.write('%s\t%s\n' % (id_, name))
            print('[INFO] Gererated temporary file at %s' % filepath)
        except Exception as e:
            print('Error in processing %s' % cls.page_url_prefix)
            print(e)

    @staticmethod
    def get_jan_code(container):
        result = ''
        p_tag = container.find('p', class_='item_description')
        if p_tag:
            text = p_tag.text.strip()
            if len(text) > 14 and text[0] == '【' and text[14] == '】':
                result = text[1:14]
        return result

    @staticmethod
    def has_next_page(soup, next_page):
        pager = soup.find('div', class_='pager')
        if pager:
            a_tag = pager.find('a')
            if a_tag and a_tag.has_attr('href') and '&' in a_tag['href']:
                page_text = a_tag['href'].split('&')[-1]
                return page_text == ('page=' + str(next_page))
        return False

    @classmethod
    def is_image_exists_in_group(cls, folder, product_id, jan_code=None):
        template = '%s/%s.jpg'
        if jan_code:
            list_ = [template % (folder, jan_code),
                     template % (folder, jan_code + '_1'),
                     template % (folder, jan_code + '_01')]
        else:
            list_ = [template % (folder, str(product_id)),
                     template % (folder, str(product_id) + '_1'),
                     template % (folder, str(product_id) + '_01')]
        for item in list_:
            if os.path.exists(cls.base_folder + '/' + item):
                return True
        return False
