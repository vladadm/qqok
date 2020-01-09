#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector


# def creds():
#     return [us, pw]
params = { 'user' : 'root',
           'password' : ''  }


def db_connect(host, select):
    connect = mysql.connector.connect(**params, host=host)
    cursor = connect.cursor(dictionary=True)
    cursor.execute(select)
    result = cursor.fetchall()
    print(result)
    #return result






