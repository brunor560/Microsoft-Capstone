"""Local-only server for previewing the feature matrix page with draft data.

Serves dashboard/ read-only on 127.0.0.1 and maps matrix.preview.json and
matrix.demo.json data URLs to assessment/preview/. Draft and fictional fixture
files therefore stay outside dashboard/ (the Pages upload root).
dashboard/serve.mjs is not used or changed. Standard library only.
"""
import functools
import http.server
import os

from . import publish

PREVIEW_URL = '/feature-matrix/data/matrix.preview.json'
PREVIEW_FILE = publish.DEFAULT_OUT['preview']
DEMO_URL = '/feature-matrix/data/matrix.demo.json'
DEMO_FILE = os.path.join(publish.PREVIEW_DIR, 'matrix.demo.json')


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map,
                          **{'.mjs': 'text/javascript', '.json': 'application/json'})

    def translate_path(self, path):
        if path.split('?')[0] == PREVIEW_URL:
            return PREVIEW_FILE
        if path.split('?')[0] == DEMO_URL:
            return DEMO_FILE
        return super().translate_path(path)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_POST(self):  # read-only
        self.send_error(405)

    do_PUT = do_DELETE = do_POST


def run(store, args):
    """CLI handler: serve-preview."""
    if not os.path.exists(PREVIEW_FILE):
        print('No preview file yet. Run: python3 -m tools.approach_a export-publication --mode preview')
    handler = functools.partial(Handler, directory=publish.DASHBOARD)
    with http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler) as srv:
        print('Draft preview (NOT accepted results): http://127.0.0.1:%d/feature-matrix/?preview=matrix.preview.json'
              % args.port)
        print('Published view (data/matrix.json):    http://127.0.0.1:%d/feature-matrix/' % args.port)
        print('Fictional demo (if generated):        http://127.0.0.1:%d/feature-matrix/?preview=matrix.demo.json' % args.port)
        print('Ctrl+C to stop.')
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print('\nstopped')
    return 0
