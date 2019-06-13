# coding: utf-8
import re
import pandas as pd
import shutil
import os
import subprocess

cmd = 'Audi_CVT_Azure_lan.bat>output_ju.txt'
os.system(cmd)
output = open('output_ju.txt', 'r' ).read()