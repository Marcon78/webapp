# from HTMLParser import HTMLParser
from html.parser import HTMLParser
from flask_restful import fields


class HTMLStripper(HTMLParser):
    def __init__(self):
        super(HTMLStripper, self).__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return "".join(self.fed)


def strip_tags(html):
    s = HTMLStripper()
    s.feed(html)

    return s.get_data()


class HTMLField(fields.Raw):
    def format(self, value):
        return strip_tags(str(value))
