"""
Capcoin server

Author:         (modified by) Josh Kerber
Date:           24 May 2018
Description:    Capcoin server for decentralized blockchain backend
Based on:       https://medium.com/crypto-currently/lets-make-the-tiniest-blockchain-bigger-ac360a328f4d
"""

# local imports
from packages.CapcoinBlock import CapcoinBlock
from packages.Resources import *
from packages.Database import *

# system imports
import sys
import json
import requests
import datetime as date

# package imports
from flask import Flask
from flask import request

# connect to db
MLAB = MLabIO()
MLAB.connect()

# instantiate node
app = Flask('Capcoin')

@app.route('/', methods=['GET'])
def apiRoot():
    """api root"""
    obj = { 'endpoints': [
        { 'url': '/blockchain',
        'method': 'GET',
        'description': 'get current blockchain (of verified balances)' },
        { 'url': '/balances',
        'method': 'GET',
        'description': 'get current balances (waiting to be mined)' },
        { 'url': '/mine',
        'method': 'POST',
        'params': ['userId'],
        'description': 'mine balances' },
        { 'url': '/add',
        'method': 'POST',
        'params': ['userId', 'capcoin'],
        'description': 'add a balance' } ] }
    return json.dumps(obj)

@app.route('/blockchain', methods=['GET'])
def getBlocks():
    """display node's blocks"""
    # get blockchain from db
    blockchain = MLAB.getBlockchain()

    # parse json
    return getResponse(blockchain)

@app.route('/balances', methods=['GET'])
def getBalances():
    """display node's balances in queue"""
    # get balances from db
    balances = MLAB.getBalances()

    # parse json
    return getResponse(balances)

@app.route('/mine', methods = ['POST'])
def mine():
    """mine Capcoin blocks"""
    # validate request body
    reqBody = request.get_json()
    if not reqBody:
        return getResponse('Invalid mine request: no params', success=False)
    elif 'user' not in reqBody:
        return getResponse('Invalid mine request: missing "user" param', success=False)
    userId = reqBody['user']

    # load objects from db
    blockchain = MLAB.getBlockchain()
    balances = MLAB.getBalances()

    # ensure balances are available to mine
    if userId not in balances or not balances[userId]:
        return getResponse('no balances to mine', success=False)

    # add dummy block if blockchain is empty
    if userId not in blockchain:
        blockData = {
            'proof-of-work': POW_CONST,
            'balances': None }
        dummyBlock = CapcoinBlock(0, date.datetime.now(), blockData, '0').getAsDict()
        blockchain[userId] = [dummyBlock]

    # get proof of work for block being mined
    lastBlock = blockchain[userId][len(blockchain[userId]) - 1]
    lastProof = lastBlock['data']['proof-of-work']
    proof = proofOfWork(lastProof)

    # instantiate new block
    newBlockData = {
        'proof-of-work': proof,
        'balances': list(balances[userId]) }
    newBlockIndex = lastBlock['index'] + 1
    newBlockTimestamp = thisTimestamp = date.datetime.now()
    lastBlockHash = lastBlock['hash']

    # create new block
    balances[userId][:] = []
    minedBlock = CapcoinBlock(
        newBlockIndex,
        newBlockTimestamp,
        newBlockData,
        lastBlockHash).getAsDict()
    blockchain[userId].append(minedBlock)

    # write data to db
    MLAB.setBlockchain(json.dumps(blockchain))
    MLAB.setBalances(json.dumps(balances))

    # return mined block to client as string
    return getResponse({
        'index': newBlockIndex,
        'timestamp': str(newBlockTimestamp),
        'data': newBlockData,
        'hash': lastBlockHash })

@app.route('/add', methods=['POST'])
def addBalance():
    """submit a balance"""
    # validate request body
    reqBody = request.get_json()
    if not reqBody:
        return getResponse('Invalid balance request: no params', success=False)
    elif 'balances' not in reqBody:
        return getResponse('Invalid balance request: missing "balances" param', success=False)

    # load balances from db
    balances = MLAB.getBalances()

    # verify all capcoin in balanes are numbers
    entries = reqBody['balances']
    for entry in entries:
        userId = entry['user']
        try:
            float(entry['capcoin'])

            # add balance to list if valid
            userId = entry['user']
            balances[userId] = [entry]
        except ValueError:
            return getResponse('Invalid balance entry: "capcoin" param is not number', success=False)

    # write list back to db
    MLAB.setBalances(json.dumps(balances))

    # display balances back to client
    output = { 'balances': reqBody['balances'] }
    return getResponse(output)
