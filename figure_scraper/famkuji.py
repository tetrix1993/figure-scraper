from figure_scraper.website import Website
import figure_scraper.constants as constants


class FamKuji(Website):
    base_folder = constants.FOLDER_FAMKUJI
    title = constants.WEBSITE_TITLE_FAMKUJI
    keywords = ["famkuji", 'Fam Kuji']

    product_url_prefix = 'https://famkuji.jp/lottery/'

    graphql_api = 'https://api.thefam.jp/graphql'
    referer = 'https://famkuji.jp'
    # query_top = "query lottery($id: ID!) {\n  lottery(id: $id) {\n    ...lottery\n    __typename\n  }\n}\n\nfragment lottery on Lottery {\n  id\n  name\n  body\n  bottomBody\n  shippingFee\n  isolatedAreaAdditionalFee\n  quantityPerShippingLimit\n  exchangeStartAt\n  exchangeDeadline\n  isExchangeable\n  estimatedShipping\n  digitalContentDownloadDeadline\n  isAvailableForDigitalContentDownload\n  isAvailableForDraw\n  mode\n  startAt\n  endAt\n  pickupStartAt\n  pickupEndAt\n  announcedPickupPeriod\n  availability {\n    userGroup\n    subscriptionPlanIds\n    viewerSuitable\n    __typename\n  }\n  metadata\n  image {\n    presetUrl {\n      originalNoAuto\n      __typename\n    }\n    __typename\n  }\n  sceneLottie {\n    standby {\n      url\n      __typename\n    }\n    drawing {\n      url\n      __typename\n    }\n    dispensing {\n      url\n      __typename\n    }\n    __typename\n  }\n  remainingAmount\n  viewerExchangeablePrizeQuantity\n  viewerCapturedDigitalContentCount\n  viewerPickupablePrizeQuantity\n  announcement {\n    id\n    title\n    body\n    __typename\n  }\n  __typename\n}\n"
    # query_prize = "query lotteryPrizes($lotteryId: ID!, $rarityId: ID) {\n  lotteryPrizes(lotteryId: $lotteryId, rarityId: $rarityId) {\n    edges {\n      cursor\n      node {\n        id\n        rarityId\n        isDigital\n        fulfillmentType\n        shopVariant {\n          id\n          name\n          image {\n            presetUrl {\n              originalNoAuto\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        viewerCapturedQuantity\n        viewerExchangeableQuantity\n        viewerPickupableQuantity\n        selectablePrizes {\n          id\n          rarityId\n          isDigital\n          shopVariant {\n            id\n            name\n            image {\n              presetUrl {\n                originalNoAuto\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          viewerCapturedQuantity\n          viewerExchangeableQuantity\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      startCursor\n      endCursor\n      __typename\n    }\n    totalCount\n    __typename\n  }\n}\n"
    query_top = "query lottery($id: ID!) {\n  lottery(id: $id) {\n    ...lottery\n    __typename\n  }\n}\n\nfragment lottery on Lottery {\n  image {\n    presetUrl {\n      originalNoAuto\n    }\n  }\n}\n"
    query_prize = "query lotteryPrizes($lotteryId: ID!, $rarityId: ID) {\n  lotteryPrizes(lotteryId: $lotteryId, rarityId: $rarityId) {\n    edges {\n      node {\n        shopVariant {\n          name\n          image {\n            presetUrl {\n              originalNoAuto\n            }\n          }\n        }\n        selectablePrizes {\n          shopVariant {\n            name\n            image {\n              presetUrl {\n                originalNoAuto\n              }\n            }\n          }\n        }\n      }\n    }\n  }\n}\n"

    @classmethod
    def run(cls):
        cls.init()
        while True:
            print('[INFO] %s Scraper' % cls.title)
            expr = input('Enter page (https://famkuji.jp/lottery/{page}): ')
            if len(expr) == 0:
                return
            cls.process_product_page(expr)

    @classmethod
    def process_product_page(cls, page):
        page_url = cls.product_url_prefix + page
        try:
            images = []
            # Top Data
            data = {'operationName': 'lottery', 'variables': {'id': page}, 'query': cls.query_top}
            top_json = cls.post_json(cls.graphql_api, data=data, headers={'origin': cls.referer,
                                                                          'referer': cls.referer,
                                                                          'x-referer': cls.referer})
            try:
                image_url = top_json['data']['lottery']['image']['presetUrl']['originalNoAuto']
                if len(image_url) > 0:
                    image_ext = image_url.split('?')[0].split('.')[-1]
                    images.append(('top.' + image_ext, image_url))
            except:
                pass

            # Prize Data
            data = {'operationName': 'lotteryPrizes', 'variables': {'lotteryId': page}, 'query': cls.query_prize}
            prize_json = cls.post_json(cls.graphql_api, data=data, headers={'origin': cls.referer,
                                                                            'referer': cls.referer,
                                                                            'x-referer': cls.referer})
            variants = []
            if 'data' in prize_json and 'lotteryPrizes' in prize_json['data']\
                    and 'edges' in prize_json['data']['lotteryPrizes']:
                for edge in prize_json['data']['lotteryPrizes']['edges']:
                    if 'node' not in edge:
                        continue
                    node = edge['node']
                    if 'selectablePrizes' in node and node['selectablePrizes'] is not None:
                        for prize in node['selectablePrizes']:
                            if 'shopVariant' in prize:
                                variants.append(prize['shopVariant'])
                    elif 'shopVariant' in node:
                        variants.append(node['shopVariant'])
            for variant in variants:
                try:
                    image_name = variant['name'].split(' ')[0]
                    image_url = variant['image']['presetUrl']['originalNoAuto']
                    image_ext = image_url.split('?')[0].split('.')[-1]
                    images.append((f'{image_name}.{image_ext}', image_url))
                except:
                    pass
            for image in images:
                image_url = image[1]
                image_name = image[0]
                cls.download_image(image_url, page + '/' + image_name)
        except Exception as e:
            print(f'[ERROR] Error in processing {page_url}: {e}')
