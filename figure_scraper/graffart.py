from figure_scraper.website import Website
import figure_scraper.constants as constants
from multiprocessing import Pool
import os


class GraffArt(Website):
    base_folder = constants.FOLDER_GRAFFART
    title = constants.WEBSITE_TITLE_GRAFFART
    keywords = ["https://kyaragoods.shop-pro.jp/", "A3Market Online"]

    page_url_prefix = 'https://kyaragoods.shop-pro.jp/'
    group_page_template = page_url_prefix + '?mode=grp&gid=%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            print('[INFO] Select an option: ')
            print('1: Download by Product ID')
            print('2: Download by Group ID')
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
        print('Coming soon...')

    @classmethod
    def download_by_group_id(cls):
        print('Coming soon...')

    @classmethod
    def update_by_group_id(cls):
        print('Coming soon...')

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
                max_processes = constants.MAX_PROCESSES
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
