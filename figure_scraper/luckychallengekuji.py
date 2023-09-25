from figure_scraper.website import Website
import figure_scraper.constants as constants


class LuckyChallengeKuji(Website):
    base_folder = constants.FOLDER_LUCKYCHALLENGEKUJI
    title = constants.WEBSITE_TITLE_LUCKYCHALLENGEKUJI
    keywords = ["https://luckychallenge-kuji.com/"]

    product_url_template = 'https://luckychallenge-kuji.com/lotteries/%s'

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter page name: ')
            if len(expr) == 0:
                return
            cls.process_product_page(expr)

    @classmethod
    def process_product_page(cls, page):
        page_url = cls.product_url_template % page
        image_list = []
        try:
            soup = cls.get_soup(page_url)

            sections = soup.select('.lotteries_container section')
            for section in sections:
                if section.has_attr('class') and len(section['class']) > 0:
                    class_name = section['class'][0]
                    images = section.select('img[src], img[data-src]')
                    for i in range(len(images)):
                        if images[i].has_attr('data-src'):
                            image_url = images[i]['data-src']
                        else:
                            image_url = images[i]['src']
                        image_name = class_name + '_' + str(i + 1).zfill(2) + '.jpg'
                        image_list.append({'name': image_name, 'url': image_url})

            rank_banners = soup.select('section.area')
            for banner in rank_banners:
                if not banner.has_attr('id'):
                    continue
                id_name = banner['id']
                images = banner.select('img[data-src]')
                for i in range(len(images)):
                    image_name = id_name + '_' + str(i + 1).zfill(2) + '.jpg'
                    image_url = images[i]['data-src']
                    image_list.append({'name': image_name, 'url': image_url})

            if len(image_list) == 0:
                print(f'[ERROR] {page_url} does not exists.')
                return
            for image in image_list:
                cls.download_image(image['url'], page + '/' + image['name'])
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
