# coding=utf-8
import locale
import webbrowser

import click
from flask import Flask
from gevent.pywsgi import WSGIServer

from sacredboard.app.config import jinja_filters
from sacredboard.app.config import routes
from sacredboard.app.data.mongodb import PyMongoDataAccess

locale.setlocale(locale.LC_ALL, '')
app = Flask(__name__)


@click.command()
@click.option("--debug", is_flag=True, default=False)
@click.option("--no-browser", is_flag=True, default=False)
@click.option("-m", default="sacred")
def run(debug, no_browser, m):
    add_mongo_config(app, m)
    app.config['DEBUG'] = debug
    app.debug = debug
    jinja_filters.setup_filters(app)
    routes.setup_routes(app)
    app.config["data"].connect()
    #print("Try to navigate to http://127.0.0.1:5000")
    if debug:
        app.run(host="0.0.0.0", debug=True)
    else:
        for port in range(5000, 5050):
            http_server = WSGIServer(('0.0.0.0', port), app)
            try:
                http_server.start()
            except OSError as e:
                if "in use" in str(e):
                    # try next port
                    continue
            print("Starting sacredboard on port %d" % port)
            if not no_browser:
                webbrowser.open_new_tab("http://127.0.0.1:%d" % port)
            http_server.serve_forever()
            break


def add_mongo_config(app, connection_string):
    split_string = connection_string.split(":")
    config = {"host": "localhost", "port": 27017, "db": "sacred"}
    if len(split_string) > 0 and len(split_string[-1]) > 0:
        config["db"] = split_string[-1]
    if len(split_string) > 1:
        config["port"] = int(split_string[-2])
    if len(split_string) > 2:
        config["host"] = split_string[-3]
    app.config["data"] = PyMongoDataAccess(
        config["host"], config["port"], config["db"])


if __name__ == '__main__':
    run()
