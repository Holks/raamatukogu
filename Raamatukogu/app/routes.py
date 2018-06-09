#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from app import app
from werkzeug.urls import url_parse
import sys, os
from app.models import Status, Book

from flask import jsonify
from flask import json
from app import db

import config

@app.route('/', methods=['GET'])
def index():
    books = Book.query.all()
    
    return render_template('index.html',books=books) 

@app.route('/add', methods=['POST'])
def add_book():
    books = request.get_json()
    if books:      
        objects = []
        for book in books:
            book_to_add = Book(title=book['title'], status=Status.procesessing.value ,author=book['author'], isbn=book['isbn'], location_tag='check_in',publish_date=book['publish_date'][0:4])
            objects.append(book_to_add)
        db.session.bulk_save_objects(objects)
        db.session.commit()        
    return '',200 