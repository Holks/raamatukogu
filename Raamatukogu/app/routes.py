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
import math
 
from sqlalchemy import or_
from datetime import datetime, date, timedelta

import config
from config import logger


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    try:
        book_count = Book.query.filter(Book.status != Status.archived.value).count()
        pages = math.ceil(book_count/app.config['BOOKS_PER_PAGE'])
        
        return render_template('index.html', pages=pages)
    except Exception as e:
        logger.error("\n===========================\nroutes.py:index:ERROR\n{0}".format(e))  
    
@app.route('/data', methods=['GET'])
def get_data():
    try:
        logger.info("\n===========================\nroutes.py:get_data:method{0}\n{1}".format(request.method, request.args))
        page = request.args.get('page', 1, type=int) 
        search_key = request.args.get('search_string', '')
        if search_key:        
            book_count = Book.query.filter(Book.status != Status.archived.value).filter(or_(Book.id.ilike('%{0}%'.format(search_key)),Book.author.ilike('%{0}%'.format(search_key)),Book.title.ilike('%{0}%'.format(search_key)),Book.isbn.ilike('%{0}%'.format(search_key)))).count()
            books_in_library = Book.query.filter(Book.status != Status.archived.value).filter(or_(Book.id.ilike('%{0}%'.format(search_key)),Book.author.ilike('%{0}%'.format(search_key)),Book.title.ilike('%{0}%'.format(search_key)),Book.isbn.ilike('%{0}%'.format(search_key)))).paginate(page, app.config['BOOKS_PER_PAGE'], False).items
        else:
            book_count = Book.query.filter(Book.status != Status.archived.value).count()
            books_in_library = Book.query.filter(Book.status != Status.archived.value).paginate(page, app.config['BOOKS_PER_PAGE'], False).items
        pages = math.ceil(book_count/app.config['BOOKS_PER_PAGE'])     
        json_list=[book.serialize for book in books_in_library]
        return jsonify({'data':json_list,'paginator':{'page':page,'pages':pages}})
    except Exception as e:
        logger.error("\n===========================\nroutes.py:get_data:ERROR\n{0}".format(e))
        
@app.route('/add', methods=['POST'])
def add_book():
    try:
        books = request.get_json()
        logger.info("\n===========================\nroutes.py:add_book:method{0}\n{1}".format(request.method, books))
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
            if last_id:
                new_books_in_library = Book.query.filter(Book.id>last_id[0]).filter(Book.status != Status.archived.value).all()
            else:
                new_books_in_library = Book.query.filter(Book.status != Status.archived.value).all()
            json_list=[book.serialize for i,book in enumerate(new_books_in_library)]
            
            return jsonify(json_list)
        else:
            return '',400
    except Exception as e:
        logger.error("\n===========================\nroutes.py:add_book:ERROR\n{0}".format(e))
    
    
@app.route('/update', methods=['PUT','DELETE'])
def update_book(): 
    json_obj = request.get_json()
    print(json_obj)
    logger.info("\n===========================\nroutes.py:update_book:method{0}\n{1}".format(request.method, json_obj))
    try:
        if json_obj:
            json_list = []
            if request.method == 'DELETE':
                for item in json_obj['data']:
                    print(item)
                    change_book = Book.query.filter(Book.id==item['id']).filter(Book.status != Status.archived.value).first()
                    if change_book:
                        change_book.status = Status.archived.value
                        #db.session.delete(change_book)
                        db.session.commit() 
                if json_obj['paginator']:
                    page = int(json_obj['paginator']['page'])
                else:
                    page = 1
                if json_obj['search_string']:
                    search_key = json_obj['search_string'] 
                else:
                    search_key = ""
                print(page, search_key)
                if search_key:        
                    book_count = Book.query.filter(Book.status != Status.archived.value).filter(or_(Book.id.ilike('%{0}%'.format(search_key)),Book.author.ilike('%{0}%'.format(search_key)),Book.title.ilike('%{0}%'.format(search_key)),Book.isbn.ilike('%{0}%'.format(search_key)))).count()
                    books_not_deleted = Book.query.filter(Book.status != Status.archived.value).filter(or_(Book.id.ilike('%{0}%'.format(search_key)),Book.author.ilike('%{0}%'.format(search_key)),Book.title.ilike('%{0}%'.format(search_key)),Book.isbn.ilike('%{0}%'.format(search_key)))).paginate(page, app.config['BOOKS_PER_PAGE'], False).items
                else:
                    book_count = Book.query.filter(Book.status != Status.archived.value).count()
                    books_not_deleted = Book.query.filter(Book.status != Status.archived.value).paginate(page, app.config['BOOKS_PER_PAGE'], False).items
                pages = math.ceil(book_count/app.config['BOOKS_PER_PAGE'])
                json_list=[book.serialize for book in books_not_deleted]    
                return jsonify({'data':json_list,'paginator':{'page':page,'pages':pages}})
                
            elif request.method == 'PUT':            
                for item in json_obj:
                    print(Status.borrowed.name,item['id'],item['status'])
                    change_book = Book.query.filter(Book.id==item['id']).filter(Book.status != Status.archived.value).first()
                    if item['status'] == Status.borrowed.name:
                        change_book.lend_date = date.today()
                        change_book.return_date = change_book.lend_date + timedelta(days=21)
                    elif item['status'] == Status.present.name:
                        change_book.lend_date = None
                        change_book.return_date = None
                    db.session.commit()
                    change_book = Book.query.filter(Book.id==item['id']).filter(Book.status != Status.archived.value).first()
                    json_list.append(change_book.serialize)
                print(json_list)
                return jsonify(json_list)                
            else:
                return '',401
        return '',400
    except Exception as e:
        logger.error("\n===========================\nroutes.py:update_book:ERROR\n{0}".format(e))
    
@app.route('/edit', methods=['PUT'])
def edit_book():  
    try:   
        json_obj = request.get_json()
        logger.info("\n===========================\nroutes.py:edit_book:method{0}\n{1}".format(request.method, json_obj))
        print(json_obj)    
        if json_obj:
            json_list = []
            for item in json_obj:
                print(item,item['id'])
                book = Book.query.filter(Book.id==item['id']).filter(Book.status != Status.archived.value).first()
                book.title = item['title']
                book.location_tag = item['location_tag']
                book.isbn = item['isbn']
                book.author = item['author']
                book.publish_date = item['publish_date']
                if item['description']:
                    book.description = item['description']
                db.session.commit()            
                changed_book = Book.query.filter(Book.id==item['id']).filter(Book.status != Status.archived.value).first()
                json_list.append(changed_book.serialize)
            print(json_list)
            return jsonify(json_list)                
            
        return '',400
    except Exception as e:
        logger.error("\n===========================\nroutes.py:edit_book:ERROR\n{0}".format(e))