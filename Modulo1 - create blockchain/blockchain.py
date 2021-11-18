#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 14:24:45 2021

@author: masquer

Módulo 1 -  Crear una cadena de bloques

    Parte 1 - Crear la cadena
    
    Parte 2 - Minado de bloques de la cadena
"""

# Import libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify


# Create blockchains
class Blockchain:
    """
    Class to make the blockchains objects and they behavoiur
    """
    
    def __init__(self):
        self.chain = []
        self.create_block(proof_of_work = 1, previous_hash = 0)
    
    def create_block(self, proof_of_work, previous_hash):
        """
        Create a block, receive a valid proof of work and the hash of the 
        previous block as params
        """
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof_of_work,
            "previous_hash": previous_hash, }
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        """
        Return the last block of the block chain
        """
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        """
        return a valid proof of work for the new block of the block chain, and 
        receive the proof of work of the previous block.
        """
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = make_proof(new_proof, previous_proof)
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

    def make_proof(proof_value, previous_proof_value):
        """
        Receive the previous valid proof and new try of proof then return a hash
        made with both proof.
        """
        return hashlib.sha256(str(proof_value**2 - previous_proof_value**3).encode()).hexdigest()

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


# Minig a block of the chain

# Start Flask Webapp
flash_app = Flask(__name__)

# Init blockchain
blockchain = Blockchain()
