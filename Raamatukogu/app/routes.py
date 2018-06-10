#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, make_response
from app import app
from werkzeug.urls import url_parse
import sys, os
from app.models import Status, Book

from flask import jsonify
from flask import json
from app import db

from datetime import datetime, date, timedelta

import config

@app.route('/', methods=['GET'])
def index():
    books_in_library = Book.query.filter(Book.status != Status.archived.value).all()        
    json_list=[book.serialize for i,book in enumerate(books_in_library)]
    resp = make_response(render_template('index.html', data=json_list, status=Status.__repr__(Status)))
    resp.headers['Content-Type'] = 'text/html; application/javascript; charset=utf-8'
    
    return resp
    
@app.route('/add', methods=['POST'])
def add_book():
    books = request.get_json()
    last_id = db.session.query(Book.id).filter(Book.status != Status.archived.value).order_by(Book.id.desc()).first()
    if books:      
        objects = []
        for book in books:
            book_to_add = Book(title=book['title'],   \
                                status=Status.procesessing.value ,  \
                                author=book['author'],   \
                                isbn=book['isbn'],   \
                                location_tag='check_in',  \
                                publish_date=book['publish_date'][0:4])            
            objects.append(book_to_add)
        db.session.bulk_save_objects(objects)
        db.session.commit()
    new_books_in_library = Book.query.filter(Book.id>last_id[0]).filter(Book.status != Status.archived.value).all()
    json_list=[book.serialize for i,book in enumerate(new_books_in_library)]
    return jsonify(json_list)
    
@app.route('/update', methods=['PUT','DELETE'])
def edit_book(): 
    json_obj = request.get_json()
    print(json_obj)
    if json_obj:
        if request.method == 'DELETE':
            for item in json_obj:
                change_book = Book.query.filter(Book.id==json_obj['id']).filter(Book.status != Status.archived.value).first()
                if change_book:
                    change_book.status = Status.archived.value
                #db.session.delete(change_book)
                    db.session.commit()
            change_book = Book.query.filter(Book.id==json_obj['id']).filter(Book.status != Status.archived.value).all()
            if not change_book or change_book.status == Status.archived.value:
                return jsonify({'id':json_obj['id']})
            else:
                return '',402
        elif request.method == 'PUT':
            for item in json_obj:
                print(json_obj,json_obj['id'],json_obj['status'], Status.present.name)
                change_book = Book.query.filter(Book.id==json_obj['id']).filter(Book.status != Status.archived.value).first()
                if json_obj['status'] == Status.present.name:
                    change_book.lend_date = date.today()
                    change_book.return_date = change_book.lend_date + timedelta(days=21)
                elif json_obj['status'] == Status.borrowed.name:
                    change_book.lend_date = None
                    change_book.return_date = None
                db.session.commit()
                change_book = Book.query.filter(Book.id==json_obj['id']).filter(Book.status != Status.archived.value).all()
                json_list=[book.serialize for i,book in enumerate(change_book)]
            return jsonify(json_list)                
        else:
            return '',401
    return '',400

    