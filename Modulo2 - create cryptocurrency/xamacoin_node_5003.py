#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 14:24:45 2021

@author: masquer

Módulo 1 -  Crear una crypto moneda
"""

# Import libraries
import datetime
import hashlib
import json
from uuid import uuid4
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request



# Create blockchains
class Blockchain:
    """
    Class to make the blockchains objects and they behavoiur
    """
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof_of_work = 1, previous_hash = 0)
        self.nodes = set()
    
    def create_block(self, proof_of_work, previous_hash):
        """
        Create a block, receive a valid proof of work and the hash of the 
        previous block as params
        """
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof_of_work,
            "previous_hash": previous_hash, 
            "transactions": self.transactions, }
        self.chain.append(block)
        self.transactions = []
        return block
    
    def get_previous_block(self):
        """
        Return the last block of the block chain
        """
        return self.chain[-1]
    
    def make_proof(self, proof_value, previous_proof_value):
        """
        Receive the previous valid proof and new try of proof then return a hash
        made with both proof.
        """
        return hashlib.sha256(str(proof_value**2 - previous_proof_value**3).encode()).hexdigest()

    def proof_of_work(self, previous_proof):
        """
        return a valid proof of work for the new block of the block chain, and 
        receive the proof of work of the previous block.
        """
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = self.make_proof(new_proof, previous_proof)
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof
                    
    def hash_of_block(self, block):
        """
        Return the hash SHA256 of block received as param
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        """
        Validate if the block chain recieved as param is valid. This method validate
        if each block of the chain have a valid proof, and have the correct previous
        hash.
        """
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
            previous_block_hash = self.hash_of_block(previous_block)
            if current_block['previous_hash'] != previous_block_hash:
                return False
            previous_block_proof = previous_block['proof']
            current_block_proof = current_block['proof']
            current_block_hash = self.make_proof(current_block_proof, previous_block_proof)
            if current_block_hash[:4] != '0000':
                return False
            block_index += 1
            previous_block = current_block
        return True

    def add_transaction(self, sender, reciver, amount):
        """
        Add transaccion to the list of transactions
        """
        self.transactions.append({
            "sender": sender,
            "receiver": reciver,
            "amount": amount,
            })
        prev_block = self.get_previous_block()
        return prev_block["index"] + 1
    
    def add_node(self, address):
        """
        Add node to the blockchain nodes 
        """
        parsed_address = urlparse(address)
        self.nodes.add(parsed_address.netloc)
        
    def replace_chain(self):
        """
        Replace the blockchain for the longest valid chain in the network
        """
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    longest_chain = chain
                    max_length = length
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# Minig a block of the chain

# Start Flask Webapp
flask_app = Flask(__name__)


# Address for the node, unique
node_address = str(uuid4()).replace('-', '')

# Init blockchain
blockchain = Blockchain()



@flask_app.route('/mine_block', methods=['GET'])
def mine_block():
    """
    Mining a new block from a Flask request
    """
    previous_block = blockchain.get_previous_block()
    previous_block_proof = previous_block['proof']
    new_proof = blockchain.proof_of_work(previous_block_proof)
    previous_block_hash = blockchain.hash_of_block(previous_block)
    blockchain.add_transaction(node_address, "Hadelin", 12)
    block = blockchain.create_block(new_proof, previous_block_hash)
    response = dict({"message": "!!!!ENHORABUENA, has minado un Nuevo bloque!"},
                    **block)
    return jsonify(response), 200

@flask_app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    """
    Get the full blockchain
    """
    response = {
            'blockchain': blockchain.chain,
            'length': len(blockchain.chain)
        }
    return jsonify(response)


@flask_app.route('/is_valid', methods=['GET'])
def is_valid():
    """
    Verify is the blockchain is valid from Flask and return a boolean with the result
    """
    if blockchain.is_chain_valid(blockchain.chain):
        message = 'Te blockchain is valid'
    else:
        message = 'Te blockchain is not valid'
    response = {
        'valid': blockchain.is_chain_valid(blockchain.chain),
        'message': message
        }
    return jsonify(response)


@flask_app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """
    Add a transaction to the pool of transactions

    Returns Http Json response with message of success added transaction

    """
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return "Error, missing or malformed data", 400
    
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'Transaction added, must be appear in block {index}'}
    return jsonify(response), 201

    
# Decentralize the blockchain

# add new nodes
@flask_app.route('/connect_node', methods=['POST'])
def connect_node():
    """
    Allow to Connect a new node o varios new nodes to the blockchain network
    
    Returns a Http Json response with a messages and in success the list of nodes too
    """
    json = request.get_json()
    nodes = json.get('node')
    message = "There are no nodes to add"
    if nodes is None or len(nodes) == 0:
        return jsonify({'message': message}), 400
    for node in nodes:
        blockchain.add_node(node)

    message = """added correctly the new nodes to the blockchain, now these are 
                the members of the blockchain:"""
    response = {
            'message': message,
            'list_of_nodes': list(blockchain.nodes),
        }
    return jsonify(response), 201

# Replace the chain for for the longest chain
@flask_app.route('/replace_chain', methods=['GET'])
def replace_chain():
    if blockchain.replace_chain():
        response = {
            'message': "the chain was replaced with the longest chain on the network",
            'new_chain': blockchain.chain,          
            }
    else:
        response = {
            'message': "Chain OK all nodes have already have the longest chain",
            'current_chain': blockchain.chain,          
            }
    return jsonify(response), 200
    

flask_app.run(host='0.0.0.0', port=5003)
