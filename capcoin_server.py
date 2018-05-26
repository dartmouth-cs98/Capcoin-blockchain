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
BLOCKCHAIN = {}
BALANCES = {}

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
    res = {}
    for key in BLOCKCHAIN:
        chainToSend = BLOCKCHAIN[key][:]
        for i in range(len(chainToSend)):
            chainToSend[i] = chainToSend[i].getAsDict()
        res[key] = chainToSend
    return getResponse(res)

@app.route('/balances', methods=['GET'])
def getBalances():
    """display node's balances in queue"""
    res = {}
    for key in BALANCES:
        res[key] = BALANCES[key][:]
    return getResponse(res)

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

    # ensure balances are available to mine
    if userId not in BALANCES or not BALANCES[userId]:
        return getResponse('no balances to mine', success=False)

    # add dummy block if blockchain is empty
    if userId not in BLOCKCHAIN:
        blockData = {
            'proof-of-work': 9,
            'balances': None }
        dummyBlock = CapcoinBlock(0, date.datetime.now(), blockData, '0')
        BLOCKCHAIN[userId] = [dummyBlock]

    # get proof of work for block being mined
    lastBlock = BLOCKCHAIN[userId][len(BLOCKCHAIN) - 1]
    lastProof = lastBlock.data['proof-of-work']
    proof = proofOfWork(lastProof)

    # TODO: reward miner

    # instantiate new block
    newBlockData = {
        'proof-of-work': proof,
        'balances': list(BALANCES[userId]) }
    newBlockIndex = lastBlock.index + 1
    newBlockTimestamp = thisTimestamp = date.datetime.now()
    lastBlockHash = lastBlock.hash

    # create new block
    BALANCES[userId][:] = []
    minedBlock = CapcoinBlock(
        newBlockIndex,
        newBlockTimestamp,
        newBlockData,
        lastBlockHash )
    BLOCKCHAIN[userId].append(minedBlock)

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

    # add balance to list
    BALANCES[userId] = [newBalance]

    # display balance to client
    output = 'Balance submission successful\n'
    output += '\tAMOUNT: {}\n'.format(newBalance['amount'])
    output += '\tUSER: {}\n'.format(newBalance['user'])
    return getResponse(output)
