from figure_scraper.website import Website
import figure_scraper.constants as constants


class DmmScratch(Website):
    base_folder = constants.FOLDER_DMMSCRATCH
    title = constants.WEBSITE_TITLE_DMMSCRATCH
    keywords = ["https://scratch.dmm.com/"]

    product_url_template = 'https://scratch.dmm.com/kuji/%s/'

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
            # top_image = soup.select('h1 img')
            # if len(top_image) > 0 and top_image[0].has_attr('src'):
            #     image_list.append({'name': 'top.jpg', 'url': top_image[0]['src'].split('?')[0]})
            #
            # prize_items = soup.select('li.prize-item')
            # for item in prize_items:
            #     title_tag = item.select('.card-header-title')
            #     prize_img = item.select('img')
            #     if len(title_tag) > 0 and len(prize_img) > 0 and prize_img[0].has_attr('data-original'):
            #         title = title_tag[0].text
            #         image_list.append({'name': title + '.jpg', 'url': prize_img[0]['data-original'].split('?')[0]})
            #
            # w_imgs = soup.select('.product-wchance-image img')
            # for i in range(len(w_imgs)):
            #     if w_imgs[i].has_attr('data-original'):
            #         w_url = w_imgs[i]['data-original'].split('?')[0]
            #         if len(w_imgs) == 1:
            #             w_name = 'wchance.jpg'
            #         else:
            #             w_name = 'wchance' + str(i) + '.jpg'
            #         image_list.append({'name': w_name, 'url': w_url})

            top_image = soup.select("meta[property='og:image'][content]")
            if len(top_image) > 0:
                image_list.append({'name': 'top.jpg', 'url': top_image[0]['content'].split('?')[0]})

            cards = soup.select('.card-prod')
            for card in cards:
                text_body = card.select('.text-body1')
                images = card.select('img[src].w-full.h-auto')
                if len(images) == 0:
                    continue
                item_url = images[0]['src'].split('?')[0]
                if len(text_body) > 0:
                    item_name = ' '.join(text_body[0].text.replace('/', '').replace('\\', '').split()) + '.jpg'
                else:
                    item_name = item_url.split('/')[-1]
                image_list.append({'name': item_name, 'url': item_url})

            w_imgs = soup.select('#wchance img[src].w-full.h-auto')
            for i in range(len(w_imgs)):
                w_url = w_imgs[i]['src'].split('?')[0]
                if len(w_imgs) == 1:
                    w_name = 'wchance.jpg'
                else:
                    w_name = 'wchance' + str(i) + '.jpg'
                image_list.append({'name': w_name, 'url': w_url})

            if len(image_list) == 0:
                print(f'[ERROR] {page_url} does not exists.')
                return
            for image in image_list:
                cls.download_image(image['url'], page + '/' + image['name'])
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
