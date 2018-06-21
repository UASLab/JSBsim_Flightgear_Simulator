# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:34:42 2018

@author: sunx0486

Input: 1. q-groundcontrol json file (e.g. blah.plan )
          note: only simpleItem for now in q-groundcontrol
       2. a base.xml file to help generation
       3. elevation, speed, etc
Output:        
       1. generate an excutable xml file for JSBsim to go through the waypoints
       2. output it as "initialization.xml"

"""

#import xml.etree.ElementTree as ET
from lxml import etree as ET
import math 
from copy import deepcopy
import json 
import numpy as np

r2d = 180/math.pi;
d2r = math.pi/180; 
m2ft = 3.28084


## Input: 

with open('Trial_3_plan_KS.plan') as f:
    data = json.load(f)

home_lat = data["mission"]['plannedHomePosition'][0]  
home_lon = data["mission"]['plannedHomePosition'][1]  
## input
int_elevation = 950.0 # this is the elevation from sea level at Rosemount
int_alt = 10.0 
int_heading = 270.0 
int_u_velocity = 150.0
tree = ET.parse('base_initialization.xml')
root = tree.getroot()

for child in root:
    if child.tag == 'position':
       child[0].text = str(int_alt) # initial takeoff alt from local ground      
       child[1].text = str(home_lat) # deg
       child[2].text = str(home_lon) # deg
    if child.tag == 'orientation':
       child[0].text = str(int_heading)    #take off heading 
    if child.tag == 'velocity':
       child[0].text = str(int_u_velocity)    
    if child.tag == 'elevation':
       child.text = str(int_elevation)    #take off heading   
    print(child.tag, child.attrib)
    
    
tree = ET.ElementTree(root)
tree.write('rosemount.xml', pretty_print=True, xml_declaration=True,   encoding="utf-8")    