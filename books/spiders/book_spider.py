import scrapy
from scrapy.http import Response


class BookSpiderSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Response:
        for book in response.css("li.col-xs-6"):
            detail_page = book.css(
                "h3 a::attr(href)"
            ).get()
            yield response.follow(
                detail_page, callback=self.parse_book
            )

        next_page = response.css(
            "li.next a::attr(href)"
        ).get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("div.col-sm-6 h1::text").get(),
            "price": float(
                response.css(
                    "div.col-sm-6 p.price_color::text"
                ).get().replace("£", "")
            ),
            "amount_in_stock": int("".join(
                response.css("div.col-sm-6 p.instock *::text").getall()
            ).strip().split("(")[1].split()[0]),
            "rating": self._word_to_number(
                response.css(
                    "div.col-sm-6 p.star-rating::attr(class)"
                ).get().split()[1]
            ),
            "category": response.css(
                "ul.breadcrumb li"
            ).getall()[2].split('html">')[1].split("</a")[0],
            "description": response.css(
                "article.product_page p::text"
            ).getall()[10],
            "upc": response.css(
                "table.table tr"
            ).getall()[0].split("td>")[1].split("<")[0]
        }

    def _word_to_number(self, word: str) -> int:
        words_to_digits = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10
        }
        return words_to_digits.get(word.lower(), "Invalid input")
