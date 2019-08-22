#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from bs4 import BeautifulSoup
import codecs
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#from time import sleep

from models import *

DRIVER_PATH = 'C:\py_projects\chromedriver\chromedriver.exe'
#DRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'
#DRIVER_PATH = '/home/ipshiv/bin/chromedriver'
DOJO_URL = 'https://teach.classdojo.com/#/login?redirect=%2Flaunchpad'
DBENGINE = 'mysql://ipshiv:Wssedr556@localhost/db_gymapp_020119?charset=utf8'

LOGIN = ""
PASSWD = ""


def connect_to_db(dburl):
    engine = create_engine(dburl, encoding='utf-8', echo=False)
    engine.execute('SET NAMES utf8')
    engine.execute('SET character_set_connection=utf8;')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

'''
class_day_time uses ISO days:
1 - Monday
2 - Thuesday
3 -  Wednsday
4 - Thursday
5 - Friday
6 - Saturday
7 - Sunday
'''

def login_class(login, passwd):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(DRIVER_PATH, chrome_options=chrome_options)
    wait = WebDriverWait(driver, 10)
    driver.get(DOJO_URL)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

    input_login = driver.find_element_by_xpath("//input[@type='text']").send_keys(login)
    input_pass = driver.find_element_by_xpath("//input[@type='password']").send_keys(passwd)
    login_button = driver.find_element_by_xpath("//button[@type='submit']").click()
    driver.implicitly_wait(25)
    return driver

def split_by_capitals(string):
    capitals = []
    parts = []
    for i, letter in enumerate(string):
        if letter.isupper():
            capitals.append(i)
    for i, index in enumerate(capitals):
        if i == 0 and index != 0:
            parts.append(string[0:index])
            parts.append(string[index:capitals[i+1]])
        elif i == len(capitals) - 1:
            parts.append(string[index:])
        else:
            parts.append(string[index:capitals[i+1]])
    return parts

def get_class_info_no_login(driver, url):
    driver.get(url)
    data = []
    #element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-test-name='wholeClassTileSmall']")))
    try:
        driver.implicitly_wait(150)
        divs = driver.find_elements_by_xpath("//div[@data-test-name]")
        imgs = driver.find_elements_by_xpath("//div[@data-test-name]//img")
    except:
        print ("Emprty class!")
    else:
        for i, div in enumerate(divs):
            data.append([div.text, div.get_attribute('data-test-name'), imgs[i].get_attribute('src')])
    return data

def get_class_info(login, passwd,  url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(DRIVER_PATH, chrome_options=chrome_options)
    wait = WebDriverWait(driver, 10)
    driver.get(DOJO_URL)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

    input_login = driver.find_element_by_xpath("//input[@type='text']").send_keys(login)
    input_pass = driver.find_element_by_xpath("//input[@type='password']").send_keys(passwd)
    login_button = driver.find_element_by_xpath("//button[@type='submit']").click()
    driver.implicitly_wait(25)
    driver.get(url)
    data = []
    try:
        element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-test-name='wholeClassTileSmall']")))
        driver.implicitly_wait(50)
        divs = driver.find_elements_by_xpath("//div[@data-test-name]")
    except:
        print("Empty class")
    else:
        for div in divs:
            data.append([div.text, div.get_attribute('data-test-name')])
    driver.close()
    return data

if __name__ == '__main__':
    #browser = login_class(LOGIN, PASSWD)
    f_log = open('log.txt', 'a')
    f_log.write(str(datetime.datetime.now()).encode('utf-8'))
    f_log.write('\t')
    err = []
    new_users = 0
    cards_added = 0
    updated_rows = 0
    session = connect_to_db(DBENGINE)
    dbclasses = session.query(Courses).all()
    users = session.query(User_Bio).all()
    #users_courses = session.query(Users_Courses).all()
    #print users
    id = 0
    uhs_id = 0
    if users:
        last_user = users[-1]
        #print last_user
        id = last_user.user_id
        ##print id
    browser = login_class(LOGIN, PASSWD)
    for c in dbclasses:
        print c.title
        class_info = get_class_info_no_login(browser, c.desc_short)
        for info in class_info[1:-1]:
            id += 1
            uhs_id += 1
            if info != []:
                name = info[1].replace('studentTile-','')
                parts = split_by_capitals(name)
                surname =  parts[1]
                name =  parts[0]
                photo = info[2]
                is_new = True
                card_data = u'none' + str(id).encode('utf-8')
                '''
                for data in class_data:
                    if data['name'] == name.encode('utf-8') or data['surname'] == surname.encode('utf-8') or \
                    data['surname'] == name.encode('utf-8') or data['name'] == surname.encode('utf-8'):
                        print ('found %s %s in data %s %s' % (surname, name.encode('utf_8'), data['surname'], data['name']))
                        print 'Data ok?'
                        choice = raw_input()
                        if choice == u'y':
                            card_data = data['card_id']
                            break
                '''
                if users:
                    for user in users:
                        if user.name == name and user.surname == surname:
                            is_new = False
                            exist_id = user.user_id
                            #print ('found user %s %s in db %s %s with id %i' % (surname, name, user.surname, user.name, user.user_id))
                if is_new == True:
                    new_users += 1
                    print 'New one'
                    new_user = User(id = id, card_id = card_data, finger_id = id, registered_on = datetime.date.today(), role = 1)
                    new_user_bio = User_Bio(id = id, user_id = id, name = name.encode('utf-8'), surname = surname.encode('utf-8'), photo = photo)
                    #whatisthis(name)
                    #users.append("{'user_id': %s, 'name': '%s', 'surname': '%s'}" % (str(id).encode('utf-8'), unicode(name), unicode(surname)))
                    point_data = info[0].strip()
                    try:
                        points = int(point_data.split(' ')[-1])
                    except:
                        points = int(point_data.split('\n')[-1])
                    else:
                        pass
                    new_uhs = Users_Courses(left_id = id, right_id = c.id, earned_xp = points, last_update = datetime.date.today())
                    #user_courses.append("{'left_id': %s, 'right_id': %s, 'earned_xp': %s}" % (str(id).encode('utf-8'), str(c['id']).encode('utf-8'), str(points).encode('utf-8')))
                    session.add(new_user)
                    session.commit()
                    session.add(new_user_bio)
                    session.commit()
                    session.add(new_uhs)
                    session.commit()
                else:
                    point_data = info[0].strip()
                    try:
                        points = int(point_data.split(' ')[-1])
                    except:
                        points = int(point_data.split('\n')[-1])
                    else:
                        pass
                    last_update = session.query(Users_Courses).filter(Users_Courses.left_id == exist_id).order_by(Users_Courses.id.desc()).first()
                    if last_update == None:
                        print ('added %i points, for %i %s' % (points, exist_id, user.surname))
                        new_uhs = Users_Courses(left_id = exist_id, right_id = c.id, earned_xp = points, last_update = datetime.date.today())
                        session.add(new_uhs)
                        session.commit()
                        updated_rows += 1
                    else:
                        if last_update.earned_xp != points and c.id == last_update.right_id:
                            print ('last update had %i points, now %i' % (last_update.earned_xp, points))
                            if (last_update.last_update.year != datetime.date.today().year and \
                                last_update.last_update.month != datetime.date.today().month and \
                                last_update.last_update.day != datetime.date.today().day):
                                new_uhs = Users_Courses(left_id = exist_id, right_id = c.id, earned_xp = points, last_update = datetime.date.today())
                                session.add(new_uhs)
                                session.commit()
                                updated_rows += 1
                            else:
                                print ('today update had %i points, now %i' % (last_update.earned_xp, points))
                                last_update.earned_xp = points
                                #last_update.last_update = datetime.date.today()
                                session.commit()
                                updated_rows += 1
    f_log.write('New users added %i\tNew cards added %i\tRows updated %i\n' % (new_users, cards_added, updated_rows))
    f_log.close()
    session.close()
    #print('New users added %i\tNew cards added %i\tRows updated %i\n' % (new_users, cards_added, updated_rows))
    browser.close()
