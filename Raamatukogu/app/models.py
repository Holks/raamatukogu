#!/usr/bin/env python
# encoding: utf-8
from app import db
from datetime import datetime
from enum import Enum

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d")]
    
class Status(Enum):
    archived = 0
    present = 1
    borrowed = 2
    maintenance = 3
    procesessing = 4
    
    def __repr__(self):
        return [{row.value+1:row.name} for row in self]
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True, nullable=False)
    status = db.Column(db.Integer, default=1)
    location_tag=db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), index=True, nullable=False)
    publish_date = db.Column(db.String(5), nullable=False)
    lend_date = db.Column(db.DateTime, index=True)
    return_date = db.Column(db.DateTime, index=True )
    isbn = db.Column(db.String(30), index=True, nullable=False)
    description = db.Column(db.String(1000), default='')
    
    def __repr__(self):
        return {'id':self.id, 'title': self.title, 'status':self.status}
    
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'             : self.id,
           'title'          : self.title,
           'status'         : self.status,
           'location_tag'   : self.location_tag,
           'author'         : self.author,
           'publish_date'   : self.publish_date,
           'lend_date'      : dump_datetime(self.lend_date),
           'return_date'    : dump_datetime(self.return_date),
           'isbn'           : self.isbn,
           'description'    : self.description,
       }