#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: hamdy.aea@protonmail.com
"""Local educational hash chain; not a cryptocurrency or consensus protocol."""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import sqlite3
from flask import Flask, jsonify, render_template


def calculate_hash(block):
    return hashlib.sha256((str(block["timestamp"]) + str(block["previous_hash"])).encode()).hexdigest()


def create_block(previous_hash):
    block = {"timestamp": datetime.now(timezone.utc).isoformat(), "previous_hash": previous_hash}
    block["hash"] = calculate_hash(block)
    return block


def initialize(database):
    with closing(sqlite3.connect(database)) as db:
        with db:
            db.execute("CREATE TABLE IF NOT EXISTS blocks (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, previous_hash TEXT, hash TEXT)")


def add_block(database):
    with closing(sqlite3.connect(database, timeout=10)) as db:
        with db:
            db.execute("BEGIN IMMEDIATE")
            last = db.execute("SELECT hash FROM blocks ORDER BY id DESC LIMIT 1").fetchone()
            block = create_block(last[0] if last else "0")
            result = db.execute("INSERT INTO blocks (timestamp, previous_hash, hash) VALUES (?, ?, ?)",
                                (block["timestamp"], block["previous_hash"], block["hash"]))
            block["id"] = result.lastrowid
    return block


def create_app(database=None, allow_writes=False):
    app = Flask(__name__)
    app.config["DATABASE"] = str(database or os.environ.get("CRYPTOPYTHON_DB", Path(app.instance_path) / "blockchain.db"))
    app.config["ALLOW_WRITES"] = allow_writes
    # Initialize only on first request, never while importing this module.
    @app.before_request
    def ensure_database():
        path = Path(app.config["DATABASE"])
        path.parent.mkdir(parents=True, exist_ok=True)
        initialize(path)

    @app.get("/blocks")
    def blocks():
        with closing(sqlite3.connect(app.config["DATABASE"])) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM blocks ORDER BY id LIMIT 1000").fetchall()
        return jsonify([dict(row) for row in rows])

    @app.post("/add_block")
    def append_block():
        if not app.config["ALLOW_WRITES"]:
            return jsonify(error="Writes disabled; enable only in a trusted local demo."), 403
        return jsonify(add_block(app.config["DATABASE"])), 201

    @app.get("/")
    def home():
        return render_template("home.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run()
