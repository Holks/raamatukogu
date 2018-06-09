#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from app import app
from werkzeug.urls import url_parse
import sys, os

@app.route('/', methods=['GET'])
def index():
    
    
    return render_template('index.html') 