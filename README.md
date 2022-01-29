# Figure Scraper
Figure Scraper downloads images from anime figure and merchandise websites by image IDs. It may uncover hidden images that is uploaded to the website by guessing the image URLs.

## Requirements
The following packages are required:
* bs4
* requests

## Websites
The scraper scrapes the following websites:
* [Alter](https://alter-web.jp/)
* [Amakuni](http://amakuni.info/)
* [AmiAmi](https://amiami.jp/)
* [Amnibus](https://amnibus.com/)
* [Animaru](https://animaru.jp/)
* [Animate](https://www.animate-onlineshop.jp/)
* [Aniplex+](https://www.aniplexplus.com/)
* [Bell House](https://bellhouse-shop.com/)
* [Cocollabo](https://www.cocollabo.net/)
* [Cospa](https://cospa.co.jp/)
* [Crux](http://www.crux-onlinestore.com/)
* [Curtain Damashii](https://www.curtain-damashii.com/)
* [Dash Store](http://dashstore.net/)
* [Dezaegg](http://dezaegg.com/)
* [DMM Scratch](https://scratch.dmm.com/)
* [Eeo Store](https://eeo.today/)
* [Ensky](https://www.enskyshop.com/)
* [F:Nex](https://fnex.jp/)
* [Gamers](https://www.gamers.co.jp/)
* [Goodsmile Company](https://www.goodsmile.info/)
* [GraffArt Shop](https://kyaragoods.shop-pro.jp/)
* [Granup](https://granup.shop/)
* [Hobby Search](https://www.1999.co.jp/)
* [Hobby Stock](http://www.hobbystock.jp/)
* [Kotobukiya](https://www.kotobukiya.co.jp/)
* [Kujibikido](https://kujibikido.com/)
* [Medicos Entertainment](https://medicos-e-shop.net/)
* [MS Factory](https://shop.ms-factory.net/)
* [Neowing (CDJapan)](https://www.neowing.co.jp/)
* [Penguin Parade](http://www.penguinparade.jp/)
* [QuesQ](http://www.quesq.net/)
* [Stella Notes](https://stellanotes.kawaiishop.jp/)
* [Union Creative](https://union-creative.jp/)
* [Wave Corporation](https://www.hobby-wave.com/)
* [YYWorld](https://yyworld.kawaiishop.jp/)

## Instructions
* Execute `figure_scraper.py` on Command Prompt (or Terminal for MacOS).
* Select a website to download from.
* For websites that prompts input for expression (e.g. Image IDs):
    * Input `3` to download image ID 3.
    * Input `2-5` to download image ID 2 to 5.
    * Input `5,8` to download image ID 5 and 8.
    * Input `2-5,7,9-11` to download image ID 2, 3, 4, 5, 7, 9, 10, 11
* To exit a scraper or cancel, enter `0` if it specifically states so. Otherwise enter blank input.

## Other Notes
* The saved images usually use the product ID as its name.
* Some scrapers have an option to save image name as JAN (Japanese Article Number) code when the code is visible on the product page.
