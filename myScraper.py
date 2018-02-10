# from command line run with: scrapy runspider myScraper.py -o out.json -t json
#
import scrapy


class myScraper(scrapy.Spider):
    name = "table"

    def start_requests(self):
        urls = ['https://myimmitracker.com/en/ca/trackers/consolidated-e-apr-tracker-express-entry-permanent-residency-application/cases/case-' + str(x) for x in range(0, 50000)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            pass
        pass

    def parse_comments(self, response):
        table = response.meta["table"]
        C = response.css('div.comments')
        CV = [(''.join(td.xpath('.//text()').extract())).replace('\xa0', ' ') for td in C.xpath('div/div[re:test(@class, "text")]')]
        table["Comments"] = table["Comments"] + CV

        next_page = response.xpath('.//a[@rel="next"]/@href').extract_first()
        if next_page is not None:
            request = response.follow(next_page, callback=self.parse_comments)
            request.meta['table'] = table
            yield request
        else:
            if "Username" in table:
                yield(table)

    def parse(self, response):
        R = response.css('div.row')
        V = [''.join(td.xpath('.//text()').extract()) for td in R.xpath('div')]
        table = {}
        table_len = int(len(V) / 2)
        H = response.css('h1::text').extract_first()
        C = response.css('div.comments')
        #CV = [(''.join(td.xpath('.//text()').extract())).replace('\xa0', ' ') for td in C.xpath('div/div[re:test(@class, "text")]')]
        for i in range(table_len):
            table[V[i]] = V[i + table_len]
            pass

        table["case"] = H
        table["URL"] = response.url
        #table["Comments"] = CV
        # first follow the comments
        #next_page = response.xpath('.//a[@rel="next"]/@href').extract_first()
        #if next_page is not None:
        #    request = response.follow(next_page, callback=self.parse_comments)
        #    request.meta['table'] = table
        #    yield request
        #else:
        if "Username" in table:
            yield(table)
