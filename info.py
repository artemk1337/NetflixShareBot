#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import *


# @ShareNetflixTestBot
# token = '753049718:AAGj4gB9MPJy2SDF8s48KUCvOdWtf6JBty8'
# @NetflixShareBot
# token = '760993666:AAHGgG-VYHBjey2NvwJAYhC5rS32wUHQXpQ'
# @ShareNetflixBot
token = '795247915:AAFoXz3_-pmpWGiLC4fLSkh_ZV-xyLd583o'


VK = 'https://vk.com/netflixshare'

password = 156723

ls = [['Netflix'],
      ['YouTube']]

lslink = [['https://www.netflix.com/'],
          ['https://www.youtube.com/']]

lscount = [['3', '5', '6'],
           ['2', '3', '4']]

datafile = ['data_0.yaml', 'serv_0.yaml', 'admins.yaml', 'archive.yaml']


prof = Database(f'{datafile[0]}')
serv = Database(f'{datafile[1]}', {str(ls[0][0]): {3: [], 5: [], 6: []},
                                  str(ls[1][0]): {2: [], 3: [], 4: []}})
admins = Database(f'{datafile[2]}', {'admins': [], 'chat_for_admins': []})
archive = Database(f'{datafile[3]}')


