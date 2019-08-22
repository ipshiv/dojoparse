#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# --- IMPORTS
from selenium import webdriver

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import connect_to_db, DBENGINE
from models import *

from time import sleep

import serial

# --- CONFIG PART
#DRIVER_PATH = '/home/ipshiv/bin/chromedriver'
DRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'
MAINURL = "http://0.0.0.0:5000/"
SERIAL_PORT = '/dev/ttyACM0'
#SERIAL_PORT = '/dev/ttyUSB0'
#BAUDRATE = 9600
BAUDRATE = 115200

# --- FUNCTIONS
def init_all(serial_port, baudrate, db_engine, driver_path):
     #db
     session = connect_to_db(db_engine)
     print session
     #serial port
     serial_connection = serial.Serial(serial_port, baudrate)
     serial_connection.readline()
     sleep(.1)
     
     #chrome driver
     chrome_options = webdriver.ChromeOptions()
     chrome_options.add_argument("--kiosk")
     chrome_options.add_argument("--no_sandbox")
     chrome_options.add_argument("--disable-infobars")
     driver = webdriver.Chrome(driver_path, chrome_options=chrome_options)
     
     return serial_connection, driver, session

def read_card(serial_port):
     data = ''
     if (serial_port.in_waiting > 0):
          data = serial_port.read(serial_port.in_waiting)
          data = ser_data_decode1(data)
          print data
     return data

def ser_data_decode(string_data):
     card_number = ''
     card_number = string_data.split(u': ')[-1].replace('\n', '').strip()
     return card_number

def ser_data_decode1(string_data):
     card_number = ''
     card_number = string_data.split(u'\n')[0].strip()
     return card_number


def find_user(db_access, card_data):
     user = db_access.query(User).filter_by(card_id=card_data).first()
     return user

def get_user_info(db_access, user):
     url = ''
     user_info = db_access.query(User_Bio).filter_by(user_id=user.id).first()
     p_data = db_access.query(Users_Courses).filter_by(left_id=user.id).order_by(Users_Courses.last_update.asc()).first()                     
     text = user_info.surname + '_00_' + user_info.name + '_00_' + str(p_data.earned_xp).encode('utf_8') + '_00_'
     if user_info.photo.endswith('png'):
          text += '/static/img/logo_old.png'
     else:
          text += user_info.photo
     url = MAINURL + 'bio?data=' + text
     return url

users = [{'card_id': u'0x69 0x3F 0x74 0x29',
          'name': u'Тестовый',
          'surname': u'Персонаж',
          'photo': u'/static/img/logo_old.png'}]

def find_user1(card_data):
     user_return = None
     for user in users:
          if user['card_id'] == card_data:
               user_return = user
     return user_return

def get_user_info1(user):
     url = MAINURL + 'bio?data=' + user['name'] + '_00_' + user['surname'] + '_00_' + u'10' + '_00_' + user['photo']
     return url

if __name__ == '__main__':
     f_data = open('card_data.txt', 'a') 
     f_data.write('TEST\n')
     f_data.close()
     
     ser, driver, session = init_all(SERIAL_PORT, BAUDRATE, DBENGINE, DRIVER_PATH)
     card_data = None
     driver.get(MAINURL)
     sleep(3)
     print 'inited'
     card_data = read_card(ser)     
     while True:
          if card_data:
               session = connect_to_db(DBENGINE)
               print card_data
               card_data = ser_data_decode(card_data)
               user = find_user(session, card_data)
               if user is None:
                    url = MAINURL + "pin?data=" + card_data
                    driver.get(url)
                    card_data = read_card(ser)
                    card_data = None
                    #sleep(5)
                    while True:
                         card_data = read_card(ser)
                         if u'bio' in driver.current_url.encode('utf-8') \
                          or driver.current_url.encode('utf-8') == MAINURL\
                          or card_data:
                              break;
                         else:
                              sleep(0.1)
                              pass
                    print 'Passed'
                    i = 0
                    while i < 100:
                         card_data = read_card(ser)
                         if card_data:
                              break
                         else:
                              i += 1
                              sleep(0.1)
               else:
                    url = get_user_info(session, user)
                    driver.get(url)
                    card_data = None
                    i = 0
                    while i < 100:
                         card_data = read_card(ser)
                         if card_data:
                              break
                         else:
                              i += 1
                              sleep(0.1)
               session.close()
          else:
               if driver.current_url != MAINURL:
                    driver.get(MAINURL)
               else:
                    card_data = read_card(ser)
               sleep(0.1)
     driver.close()
     
