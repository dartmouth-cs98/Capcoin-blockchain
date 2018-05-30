"""
App Resources

Author:         Josh Kerber
Date:           29 May 2018
Description:    Functions for storing and retrieving data
"""

import sys
import pymongo
import json

class MLabIO:
    def __init__(self):
        self.client = None
        self.db = None

        # db location
        self.dbPort = 39940
        self.dbUrl = 'ds239940.mlab.com'
        self.dbName = 'heroku_xs4zfwkm'

        # credentials
        self.username = 'jakerber96@gmail.com'
        self.password = 'password12345'
    def connect(self):
        """connect to mlab db"""
        try:
            self.client = pymongo.MongoClient(self.dbUrl, self.dbPort)
            self.db = self.client[self.dbName]
            self.db.authenticate(self.username, self.password)
        except Exception as e:
            print('unable to connect to mongo', e)
            sys.exit()
    def setBlockchain(self, blockchain):
        self.db.blockchain.remove()
        self.db.blockchain.insert_one({'data': blockchain})
    def setBalances(self, balances):
        self.db.balances.remove()
        self.db.balances.insert_one({'data': balances})
    def getBlockchain(self):
        res = self.db.blockchain.find()[0]['data']
        return json.loads(res)
    def getBalances(self):
        res = self.db.balances.find()[0]['data']
        return json.loads(res)
