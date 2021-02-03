# Figure Scraper
Figure Scraper downloads images from anime figure and merchandise websites by image IDs. It may uncover hidden images that is uploaded to the website by guessing the image URLs.

## Requirements
The following packages are required:
* bs4
* requests

## Websites
The scraper scrapes the following websites:
* [Aniplex+](https://www.aniplexplus.com/)
* [F:Nex](https://fnex.jp/)
* [Goodsmile Company](https://www.goodsmile.info/)
* [Kotobukiya](https://www.kotobukiya.co.jp/)
* [Medicos Entertainment](https://medicos-e-shop.net/)
* [Union Creative](https://union-creative.jp/)
* [Wave Corporation](https://www.hobby-wave.com/)

## Instructions
* Execute `figure_scraper.py` on Command Prompt (or Terminal for MacOS).
* Select a website to download from.
* For websites that prompts input for expression (e.g. Image IDs):
    * Input `3` to download image ID 3.
    * Input `2-5` to download image ID 2 to 5.
    * Input `5,8` to download image ID 5 and 8.
    * Input `2-5,7,9-11` to download image ID 2, 3, 4, 5, 7, 9, 10, 11
