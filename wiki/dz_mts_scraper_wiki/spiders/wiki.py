import scrapy
from dz_mts_scraper_wiki.items import FilmItem

class WikiSpider(scrapy.Spider):
    name = "wiki"
    allowed_domains = ["ru.wikipedia.org"]
    start_urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"]

    def parse(self, response):
        for selector in response.css('div.mw-category-group li'):
            film_name = selector.css('a::attr(title)').get()
            film_page = selector.css('a::attr(href)').get()
            
            if film_page:
                yield response.follow(
                    film_page,
                    callback=self.parse_film_info,
                    meta={'name': film_name}
                )
            else: 
                yield film_name

            

        next_page_link = response.css('a:contains("Следующая страница")::attr(href)').get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)

    def parse_film_info(self, response):
        item = FilmItem()

        item['name'] = response.meta.get('name', 'Unknown')
    
        selector_genre = response.css('span[data-wikidata-property-id="P136"]')
        item['genre'] = selector_genre.css('a::attr(title)').get()
    
        selector_director = response.css('span[data-wikidata-property-id="P57"]')
        item['director'] = selector_director.css('a::attr(title)').get()
    
        selector_county = response.css('span[data-wikidata-property-id="P495"]')
        item['country'] = selector_county.css('a::attr(title)').get()

        selector_id_imdb = response.css('span[data-wikidata-property-id="P345"]')
        item['id_imdb'] = selector_id_imdb.css('a::attr(title)').get()
    
    
        selector_year = response.css('tbody tr:contains("Год")')
        if selector_year:
            item['year'] = selector_year.css('span.dtstart::text').get()
        else:
            selector_year = response.css('tbody tr:contains("Дата")')
            item['year'] = selector_year.css('td.plainlist::text').get().replace("\n", "")
    
        yield item