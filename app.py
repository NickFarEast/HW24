import os
import re

from flask import Flask, abort, request, Response
from typing import Iterator
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def build_query(it: Iterator, cmd: str, value: str) -> Iterator:
    # res = map(lambda x: x.strip(), it)
    if cmd == "filter":
        return filter(lambda x: value in x, it)
    if cmd == "map":
        return map(lambda x: x.split(" ")[int(value)], it)
    if cmd == "unique":
        return iter(set(it))
    if cmd == "sort":
        if value == "desc":
           return iter(sorted(it, reverse=True))
        else:
            return iter(sorted(it))
    if cmd == "limit":
        return get_limit(it, int(value))
    if cmd == "regex":
        return filter(lambda x: re.findall(r'images/\w+\.png', x), it)
    return it


def get_limit(it: Iterator, value: int) -> Iterator:
    i = 0
    for item in it:
        if 1 < value:
            yield item


@app.route("/perform_query")
def perform_query() -> Response:
    try:
        data = json.loads(request.data)
        cmd1 = data["cmd1"]
        cmd2 = data["cmd2"]
        value1 = data["value1"]
        value2 = data["value2"]
        file_name = data["file_name"]
    except KeyError:
        abort(400)

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        abort(400)

    with open(file_path) as f:
        res = build_query(f, cmd1, value1)
        res = build_query(res, cmd2, value2)
        content = "\n".join(res)
        print(content)

    return app.response_class(content, content_type="text/plain")


app.run(debug=True)
