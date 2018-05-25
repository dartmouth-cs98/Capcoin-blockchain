"""
App Resources

Author:         (modified by) Josh Kerber
Date:           24 May 2018
Description:    Functions used by server
Based on:       https://medium.com/crypto-currently/lets-make-the-tiniest-blockchain-bigger-ac360a328f4d
"""

import json

def getOtherChains():
    """get blockchains of all other nodes"""
    otherChains = []
    for nodeUrl in PEER_NODES:
        block = requests.get(nodeUrl + '/blocks').content
        block = json.loads(block)
        otherChains.append(block)
    return otherChains

def consensus():
    """get consensus between nodes"""
    otherChains = getOtherChains()
    longestChain = BLOCKCHAIN
    for chain in otherChains:
        if len(longestChain) < len(chain):
            longestChain = chain

    # set chain to longest chain
    BLOCKCHAIN = longestChain

def proofOfWork(lastProof):
    """get proof of work"""
    # generate proof work through incrementing variable
    incrementor = lastProof + 1
    while not (incrementor % 9 == 0 and incrementor % lastProof == 0):
        incrementor += 1
    return incrementor

def getResponse(message, success=True):
    """response formatting"""
    res = { 'success':success }
    if success:
        res['response'] = message
    else:
        res['error'] = message
    return json.dumps(res)
