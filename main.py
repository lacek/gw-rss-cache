# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import flask
import logging
import urllib

from google.appengine.api import urlfetch
from xml.etree import cElementTree as ET

RSS_URL = 'https://www.genomeweb.com/%s/rss'
CACHE_URL = 'http://webcache.googleusercontent.com/search?'

app = flask.Flask(__name__)


def handle(url):
    result = urlfetch.fetch(url)
    if result.status_code != 200:
        return 'Error fetching: %s' % url, result.status_code

    root = ET.fromstring(result.content)

    link = root.find('.//{http://www.w3.org/2005/Atom}link')
    link.set('href', flask.request.url)

    for link in root.findall('.//item/link'):
        query = {'num': 1, 'strip': 1, 'vwsrc': 0}
        query['q'] = 'cache:' + link.text
        link.text = CACHE_URL + urllib.urlencode(query)

    return flask.Response(ET.tostring(root, encoding='utf-8', method='xml'),
                          mimetype='application/rss+xml')


@app.route('/')
def main():
    return flask.render_template('index.html')


@app.route('/breaking-news')
def breakingNews():
    return handle(RSS_URL % 'breaking-news')


@app.route('/<channel>')
def channel(channel):
    return handle(RSS_URL % ('channel/' + channel))


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
