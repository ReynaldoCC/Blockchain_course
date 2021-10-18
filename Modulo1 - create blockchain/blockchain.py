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
class blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof_of_work = 1, previous_hash = 0)