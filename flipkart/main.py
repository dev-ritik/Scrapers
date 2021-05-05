#!/usr/bin/python3
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib import parse
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

FEED_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title type="text">{title}</title>
    <id>{feed_src}</id>
    <updated>{time}</updated>
    <author>
        <name>dev-ritik</name>
    </author>
    <link rel="alternate" type="text/html" href="{url_target}" />
    <link rel="self" type="application/atom+xml" href="{feed_src}" />
    <entry>
        <title type="html">{title}</title>
        <published>{time}</published>
        <updated>{time}</updated>
        <id>{url_target}</id>
        <link rel="alternate" type="text/html" href="{url_target}"/>
        <content type="html">&lt;img width="300" style="max-width:300;max-height:300" src="{image_url}" alt="{title}" 
        /&gt;&lt;br/&gt;Price: {price} INR&lt;br&gt;{attrs_str}</content>
    </entry>
</feed>
"""
HOST = 'localhost'
PORT = 12564


def price_check(url: str):
    """
    Scrape and get product details
    """
    res = requests.get(url, timeout=8)
    content = BeautifulSoup(res.content, "html.parser")
    price_div = content.find('div', attrs={"class": "_30jeq3 _16Jk6d"}).text
    price = int((price_div.replace(",", ""))[1:])
    name = content.find('span', attrs={"class": "B_NuCI"}).text
    image_url = content.find('div', attrs={"class": "q6DClP"})["style"].lstrip('background-image:url(')[:-1]
    return name, price, image_url


def escape_url(url) -> str:
    return url.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def extract_params(query):
    params = dict(parse.parse_qsl(query))
    attrs = {}
    extra_keys = set(params.keys()) - {'link', 'pid', 'lid'}
    for e in extra_keys:
        attrs[e] = params[e]
        del params[e]
    base_url = params['link']
    del params['link']
    return base_url + '&' + urlencode(params), attrs


class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = parse.urlparse(self.path)
        if parsed_path.path == '/flipkart':
            url, attrs = extract_params(parsed_path.query)
            try:
                name, price, image_url = price_check(url)
            except:
                name = price = image_url = 'Error'
            self.send_response(200)
            self.send_header('Content-Type',
                             'text/plain; charset=utf-8')
            self.end_headers()
            time = datetime.now(timezone.utc)
            full_url = ''.join([f'http://{HOST}:{PORT}/', self.path])
            attrs_str = ''.join(f'{key.title()}: {value}&lt;br&gt;' for key, value in attrs.items())
            self.wfile.write(
                FEED_TEMPLATE.format(title=name, time=time.isoformat(), url_target=escape_url(url),
                                     feed_src=escape_url(full_url),
                                     image_url=image_url, price=price, attrs_str=attrs_str).encode('utf-8'))
        else:
            self.send_error(404, "Path not found {}".format(self.path))


if __name__ == '__main__':
    from http.server import HTTPServer

    server = HTTPServer((HOST, PORT), GetHandler)
    server.serve_forever()
