import trafilatura
from bs4 import BeautifulSoup


class GeneralHTMLParser:
    """
    For further processing, process the HTML such that junk is removed.
    """

    def foo(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        trafilatura.extract(html)
        downloaded = trafilatura.fetch_url('https://github.blog/2019-03-29-leader-spotlight-erin-spiceland/')
        trafilatura.extract(downloaded)

        return
