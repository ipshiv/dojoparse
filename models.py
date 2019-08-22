# -*- coding: utf-8 -*-
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Model = declarative_base()
    
class User(Model):
    
    '''
    roles
    4 - SU
    3 - admin
    2 - teacher
    1 - study
    0 - listener
    
    '''
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    card_id = Column(String(30), unique=True, nullable=False)
    finger_id = Column(Integer, nullable=False, default=0)
    #password = Column(String(240), nullable=False)
    registered_on = Column(DateTime, nullable=False)
    role = Column(Integer, nullable=False, default=0)
    confirmed = Column(Boolean, nullable=False, default=False)
    confirmed_on = Column(DateTime, nullable=True)
    
    # classroom = Column(Integer, ForeignKey('users.id'), nullable = True)
    
    # info = relationship("User_Bio", backref="user", lazy='dynamic')
    
    children = relationship("Users_Courses", back_populates="parent" , cascade="delete, delete-orphan")
    '''
    def __init__(self, email, password, confirmed,
                 paid=False, role=1, confirmed_on=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.role = role
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
    '''
class User_Bio(Model):
    
    __tablename__ = "user_bio"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    name = Column(String(90), nullable=False)
    surname = Column(String(90), nullable=False)
    bio = Column(Text, nullable=True, default=u'Вы пока ничего не рассказали о себе!')
    hobbies = Column(Text, nullable=True, default=u'Мы пока ничего не знаем о Ваших увлечениях!')
    photo = Column(Text, nullable=False, default='/static/img/logo_old.png')
    
    user = relationship("User", backref=backref("info", uselist=False), lazy='joined')
    
    '''
    def __init__(self, name, surname, bio,
                 hobbies, photo):
        self.name = name
        self.surname = surname
        self.bio = bio
        self.hobbies = hobbies
        self.photo = photo
    '''    
class Courses(Model):
    
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    slug = Column(String(120), nullable=False)
    desc_short = Column(String(240), nullable=False)
    desc_full = Column(Text, nullable=False)
    img = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False)
    published = Column(Boolean, default=False)
    
    teacher = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    parents = relationship("Users_Courses", back_populates="child", cascade="save-update, merge, delete")
    
    #lessons = relationship("Lessons", backref=backref("course"), lazy='joined')
    

class Users_Courses(Model):
    
    __tablename__ = 'uhs'
    id = Column(Integer, primary_key=True)
    left_id = Column(Integer, ForeignKey('users.id'))
    right_id = Column(Integer, ForeignKey('courses.id'))
    earned_xp = Column(Integer, nullable=True)
    last_update = Column(DateTime, nullable=False)
    child = relationship("Courses", back_populates="parents")
    parent = relationship("User", back_populates="children")
'''
in_class = Table ('in_class',
                     Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
                     Column('class_id', Integer, ForeignKey('classroom.id'), primary_key=True)
                    )

class ClassRoom (Model):
    
    __tablename__ = "classroom"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    day = Column(Text, nullable=True)
    time = Column(Time, nullable=True)
    course = Column(Integer, ForeignKey('courses.id'), nullable=False)
    
    users = relationship('User', secondary=in_class, lazy='subquery',
        backref=backref('classrooms', lazy=True))
'''


