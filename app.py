#!/usr/bin/env python3
'''
Name: Hamdy Abou El Anein    
Email: hamdy.aea@protonmail.com
Date of creation: 04.04.2023
Last update:05.04.2023
Version: 1.0.0
Description:  This is the proof of concept of a blockchain in Python with flask.
Example of use: http://astrometry.pythonanywhere.com/
'''
import hashlib
import datetime
import sqlite3
from flask import Flask, jsonify, request, render_template

from os import path

ROOT = path.dirname(path.realpath(__file__))

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect(path.join(ROOT, "blockchain.db"))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS blocks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 timestamp TEXT,
                 previous_hash TEXT,
                 hash TEXT)''')
    conn.commit()
    conn.close()

def calculate_hash(block):
    block_contents = str(block['timestamp']) + str(block['previous_hash'])
    block_hash = hashlib.sha256(block_contents.encode()).hexdigest()
    return block_hash

def create_block(previous_hash):
    block = {
        'timestamp': str(datetime.datetime.now()),
        'previous_hash': previous_hash
    }
    block['hash'] = calculate_hash(block)
    return block

def get_last_block():
    conn = sqlite3.connect(path.join(ROOT, "blockchain.db"))
    c = conn.cursor()
    c.execute("SELECT * FROM blocks ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    conn.close()
    if result:
        block = {
            'id': result[0],
            'timestamp': result[1],
            'previous_hash': result[2],
            'hash': result[3]
        }
        return block
    else:
        return None

def add_block():
    last_block = get_last_block()
    if last_block:
        previous_hash = last_block['hash']
    else:
        previous_hash = '0'
    block = create_block(previous_hash)
    conn = sqlite3.connect(path.join(ROOT, "blockchain.db"))
    c = conn.cursor()
    c.execute("INSERT INTO blocks (timestamp, previous_hash, hash) VALUES (?, ?, ?)",
              (block['timestamp'], block['previous_hash'], block['hash']))
    conn.commit()
    conn.close()
    return block

@app.route('/blocks', methods=['GET'])
def get_blocks():
    conn = sqlite3.connect(path.join(ROOT, "blockchain.db"))
    c = conn.cursor()
    c.execute("SELECT * FROM blocks ORDER BY id")
    rows = c.fetchall()
    conn.close()
    blocks = []
    for row in rows:
        block = {
            'id': row[0],
            'timestamp': row[1],
            'previous_hash': row[2],
            'hash': row[3]
        }
        blocks.append(block)
    return jsonify(blocks)

@app.route('/add_block', methods=['GET'])
def add_block_api():
    block = add_block()
    return jsonify(block)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    connect_db()
    app.run(debug=True)

