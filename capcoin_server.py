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

# system imports
import json
import requests
import datetime as date

# package imports
from flask import Flask
from flask import request

# this node's data stores
BLOCKCHAIN_FILE = 'Blockchain'
BALANCES_FILE = 'Balances'

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
        'params': ['userId', 'amount'],
        'description': 'add a balance' } ] }
    return json.dumps(obj)

@app.route('/blockchain', methods=['GET'])
def getBlocks():
    """display node's blocks"""
    # open blockchain file
    f = open(BLOCKCHAIN_FILE)
    blockchain = json.loads(f.read())
    f.close()

    # parse json
    return getResponse(blockchain)

@app.route('/balances', methods=['GET'])
def getBalances():
    """display node's balances in queue"""
    # open balances file
    f = open(BALANCES_FILE)
    balances = json.loads(f.read())
    f.close()

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

    # load balances from file
    f = open(BLOCKCHAIN_FILE)
    blockchain = json.loads(f.read())
    f.close()

    # load balances from file
    f = open(BALANCES_FILE)
    balances = json.loads(f.read())
    f.close()

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

    # write blockchain back to file
    f = open(BLOCKCHAIN_FILE, 'w')
    f.write(json.dumps(blockchain))
    f.close()

    # write balances back to file
    f = open(BALANCES_FILE, 'w')
    f.write(json.dumps(balances))
    f.close()

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
    newBalance = request.get_json()
    if not newBalance:
        return getResponse('Invalid balance request: no params', success=False)
    elif 'amount' not in newBalance:
        return getResponse('Invalid balance request: missing "amount" param', success=False)
    elif 'user' not in newBalance:
        return getResponse('Invalid balance request: missing "user" param', success=False)
    else:

        # verify amount is number
        userId = newBalance['user']
        try:
            float(newBalance['amount'])
        except ValueError:
            return getResponse('Invalid balance request: "amount" param is not number', success=False)

    # load balances from file
    f = open(BALANCES_FILE)
    balances = json.loads(f.read())
    f.close()

    # add balance to list
    balances[userId] = [newBalance]

    # write list back to file
    f = open(BALANCES_FILE, 'w')
    f.write(json.dumps(balances))
    f.close()

    # display balance to client
    output = 'Balance submission successful\n'
    output += '\tAMOUNT: {}\n'.format(newBalance['amount'])
    output += '\tUSER: {}\n'.format(newBalance['user'])
    return getResponse(output)
