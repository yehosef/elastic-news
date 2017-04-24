import urllib.request

from bs4 import BeautifulSoup

from text_enrichment.text_enrichment import TextEnricher


class ArticleParser():
    def __init__(self):
        self.parsers = all_parsers()

    def parse_article(self, article_metadata):
        with urllib.request.urlopen(article_metadata['url']) as response:
            article_html = response.read()
        article_soup = BeautifulSoup(article_html, 'lxml')
        return self.parsers[article_metadata['source']](article_metadata, article_soup)

    def add_parser(self, source, parser):
        self.parsers[source] = parser


# TODO move these functions to another file
def reuters_parser(article_metadata, article_soup):
    return {
        **article_metadata,
        'fullText': ''.join([p.get_text() for p in article_soup.select('#article-text > p')])
    }


def cnn_parser(article_metadata, article_soup):
    paragraphs = article_soup.select('.zn-body__paragraph')
    # Remove <cite class="el-editorial-source"> (CNN)</cite> from first paragraph
    if len(paragraphs) > 0:
        citation = paragraphs[0].select(".el-editorial-source")
        if len(citation) > 0:
            citation[0].extract()
    return {
        **article_metadata,
        'fullText': ''.join([p.get_text() for p in paragraphs])
    }


def the_guardian_uk_parser(article_metadata, article_soup):
    if article_soup.find("div", {"class": "content__article-body from-content-api js-article__body"}):
        paragraphs = article_soup.find("div", {"class": "content__article-body from-content-api js-article__body"})
        return {**article_metadata, 'fullText': ''.join([p.get_text() for p in paragraphs.select('p')])}
    else:
        return None


def all_parsers():
    return {
        "reuters": reuters_parser,
        "cnn": cnn_parser,
        "the-guardian-uk": the_guardian_uk_parser
    }


if __name__ == '__main__':
    articles = [{
        'author': 'Lesley Wroughton and Yeganeh Torbati',
        'source': 'reuters',
        'title': 'U.S. air strike gives Tillerson a boost for Moscow talks',
        'description': "U.S. Secretary of State Rex Tillerson's visit to Moscow this week will be an early test of whether the Trump administration can use any momentum generated by striking a Syrian air base to craft and execute a strategy to end the Syrian war.",
        'url': 'http://www.reuters.com/article/us-usa-russia-tillerson-idUSKBN17C0D4',
        'urlToImage': 'http://s3.reutersmedia.net/resources/r/?m=02&d=20170410&t=2&i=1180051153&w=&fh=545px&fw=&ll=&pl=&sq=&r=LYNXMPED39077',
        'publishedAt': '2017-04-10T08:08:52Z'
    },
        {
            "author": "Ben Westcott, CNN",
            "source": "cnn",
            "title": "US warns Russia over support for Assad",
            "description": "Foreign ministers of leading industrialized nations were meeting Monday amid heightened tensions between Russia and the United States over the Trump administration's unexpected military strike on a Syrian airbase.",
            "url": "http://www.cnn.com/2017/04/10/politics/syria-russia-iran-missile-strikes/index.html",
            "urlToImage": "http://i2.cdn.cnn.com/cnnnext/dam/assets/170328141858-russia-jet-syria-tease-super-tease.jpg",
            "publishedAt": "2017-04-10T09:59:38Z"
        },
        {
            "author": "Dan Roberts, Lisa O'Carroll",
            "source": "the-guardian-uk",
            "title": "European parliament chief urges May to agree swift deal on EU citizens",
            "description": "Antonio Tajani presses PM to defend rights of those in UK and strikes more positive note than some on timing of trade talks",
            "url": "https://www.theguardian.com/politics/2017/apr/20/european-parliament-chief-urges-may-to-agree-swift-deal-on-eu-citizens",
            "urlToImage": "https://i.guim.co.uk/img/media/2167d3a064f8c3fecea66292e9f395c58bc69d6a/0_216_5148_3089/master/5148.jpg?w=1200&h=630&q=55&auto=format&usm=12&fit=crop&crop=faces%2Centropy&bm=normal&ba=bottom%2Cleft&blend64=aHR0cHM6Ly91cGxvYWRzLmd1aW0uY28udWsvMjAxNi8wNS8yNS9vdmVybGF5LWxvZ28tMTIwMC05MF9vcHQucG5n&s=355554190462a67ac23423766b5efa3d",
            "publishedAt": "2017-04-20T12:25:00Z"
        }]

    ap = ArticleParser()
    ap.add_parser('reuters', reuters_parser)
    ap.add_parser('cnn', cnn_parser)
    ap.add_parser('the-guardian-uk', the_guardian_uk_parser)

    te = TextEnricher()

    for article in articles[-1:]:
        parsed = ap.parse_article(article)
        annotated = te.enrichDocument(parsed)
        print(annotated)
