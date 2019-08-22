# -*- coding: utf-8 -*-
import models
from main import classes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
DBENGINE = 'mysql://ipshiv:Wssedr556@localhost/db_gymapp_020119'
engine = create_engine(DBENGINE, encoding='utf-8', convert_unicode=True)
models.Model.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
for i, cl in enumerate(classes):
    new_cl = models.Courses(id = cl['id'], title = cl['name'], slug = cl['name'], desc_short = cl['url'], desc_full = u'NULL', img = u'/static/img/logo_old.png', age = 10, difficulty = 1, published = 1)
    session.add(new_cl)
    session.commit()

