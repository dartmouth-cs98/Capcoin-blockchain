"""
Capcoin block object

Author:         (modified by) Josh Kerber
Date:           24 May 2018
Description:    Single block of Capcoin
Based on:       https://medium.com/crypto-currently/lets-make-the-tiniest-blockchain-bigger-ac360a328f4d
"""

import hashlib as hasher

class CapcoinBlock:
    """Single Capcoin block, defines Capcoin schema"""
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hashBlock()
    def hashBlock(self):
        """hash this block"""
        sha = hasher.sha256()
        data = (str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode('utf-8')
        sha.update(data)
        return sha.hexdigest()
    def getAsDict(self):
        blockDict = { 'index': str(self.index),
            'timestamp': str(self.timestamp),
            'data': str(self.data),
            'hash': self.hash }
        return blockDict
