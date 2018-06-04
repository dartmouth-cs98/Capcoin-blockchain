"""
App Resources

Author:         (modified by) Josh Kerber
Date:           24 May 2018
Description:    Functions used by server
Based on:       https://medium.com/crypto-currently/lets-make-the-tiniest-blockchain-bigger-ac360a328f4d
"""

import json

POW_CONST = 5

def proofOfWork(lastProof):
    """proof of work algorithm"""
    # generate proof of work by incrementing variable
    incrementor = lastProof + 1
    while not (incrementor % POW_CONST == 0 and incrementor % lastProof == 0):
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
