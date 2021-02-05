from figure_scraper import *


def run():
    while True:
        print('[INFO] Figure Scraper Main Menu')
        print('[INFO] Select method to list websites: ')
        print('1: Search websites by keywords')
        print('2: List all websites')
        print('0: Exit')

        try:
            choice = int(input('Enter choice: '))
        except:
            print('[ERROR] Invalid choice.')
            continue

        if choice == 0:
            break
        elif choice == 1:
            search_websites_by_keywords()
        elif choice == 2:
            list_websites()
        else:
            print('[ERROR] Invalid choice.')
    print('[INFO] Exiting...')


def search_websites_by_keywords():
    keywords_str = input('Enter keyword(s): ').strip()
    if len(keywords_str) == 0:
        print('[INFO] No keywords have been entered.')
        return
    keywords = keywords_str.split(' ')
    websites = Website.__subclasses__()
    filtered_websites = []
    valid_keywords = []
    for keyword in keywords:
        if len(keyword) > 0:
            valid_keywords.append(keyword)

    for website in websites:
        matched_keywords = 0
        for keyword in valid_keywords:
            compares = [website.title.lower()]
            for website_keyword in website.keywords:
                compares.append(website_keyword.lower())
            for compare in compares:
                if keyword.lower() in compare:
                    matched_keywords += 1
                    break
            else:
                break
        if matched_keywords == len(valid_keywords):
            filtered_websites.append(website)

    if len(filtered_websites) == 0:
        print('[INFO] No websites found.')
        return
    else:
        list_websites(filtered_websites)


def list_websites(websites=None):
    if websites is None:
        websites = Website.__subclasses__()

    if len(websites) == 1:
        websites[0].run()
        return

    print('[INFO] Select a website to scrape: ')
    number_max_len = len(str(len(websites)))
    for i in range(len(websites)):
        number = i + 1
        number_str = str(number)
        if len(number_str) < number_max_len:
            for j in range(number_max_len - len(number_str)):
                number_str = ' ' + number_str
        print('%s: %s' % (number_str, websites[i].title))

    zero_str = '0'
    for i in range(number_max_len - 1):
        zero_str = ' ' + zero_str
    print('%s: Exit' % zero_str)

    try:
        choice = int(input('Enter choice: '))
    except:
        print('[ERROR] Invalid choice.')
        return

    if choice == 0:
        pass
    elif choice < 0 or choice > len(websites):
        print('[ERROR] Invalid choice.')
    else:
        try:
            # print('[INFO] %s selected.' % websites[choice - 1].title)
            websites[choice - 1].run()
        except Exception as e:
            print('[ERROR] Error in executing website')
            print(e)
    return


if __name__ == '__main__':
    run()
