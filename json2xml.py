# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 12:24:49 2018
1. see the following for .plan format
https://dev.qgroundcontrol.com/en/file_formats/plan.html

2. ID, params, etc 
http://mavlink.org/messages/common#MISSION_ITEM
@author: sunx0486

Input: 1. q-groundcontrol json file (e.g. blah.plan )
          note: only simpleItem for now in q-groundcontrol
       2. a base.xml file to help generation
       3. elevation, speed, etc
Output:        
       1. generate an excutable xml file for JSBsim to go through the waypoints
       2. output it as "output.xml"
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

NO_tot_wp = len(data["mission"]['items']) -1 ## number of way points minus the initial point 
  
## extract waypoints lat, lon, alt
for i in range(0,no_wp):
    print(data["mission"]['items'][i]['params'][4:7]) ## print all the way points info

wp_lat_hist = np.zeros((1,no_wp))
wp_lon_hist = np.zeros((1,no_wp))
target_alt_hist = np.zeros((1,no_wp))
for i in range(0,no_wp):
    wp_lat_hist[0,i] = data["mission"]['items'][i]['params'][4]*d2r  # rad
    wp_lon_hist[0,i] = data["mission"]['items'][i]['params'][5]*d2r  # rad
    target_alt_hist[0,i] = data["mission"]['items'][i]['params'][6]*m2ft # rad
    
#%% create new xml file based off a base file and .plan from qgroundcontrol 
tree = ET.parse('base.xml')
root = tree.getroot()
    
root.tag
root.attrib

## input
elevation = 950 # this is the elevation from sea level at Rosemount 

end_time = 3600

# velocity (constant throughout right now)
velocity_fps = 145.0

# initialization point (first way point)
int_lat_rad = wp_lat_hist[0,1]
int_lon_rad = wp_lon_hist[0,1]
int_alt_setpoint = elevation+ 650.0
# or you can get it by data["mission"]['plannedHomePosition']

int_heading_deg = 270.0 # deg
heading_setpoint_select = 0

alt_wp_1_threshold = 500.0 # ft height above the ground 
target_alt_1st = elevation + 350
altitude_hold_1st = 1
# second to the second last
wp_lat= wp_lat_hist[0,2:]
wp_lon =wp_lon_hist[0,2:]

target_alt = np.zeros((1,len(wp_lat)))
# target_alt = [1600.0, 1320.0, 1300.0, 1250.0, 1290.0, 1290.0] # from sea-level
target_alt =  target_alt_hist[0,2:]*m2ft + elevation
wp_distance = np.zeros((1,len(wp_lat)))
wp_distance[0,0] = 500
wp_distance = wp_distance + 300
target_alt_hold = [1, 1, 1]



#%% Generate xml executable file 
# Print children notdes 
for child in root:
    if child.tag == 'use':
       aircraft = child.attrib.get('aircraft')
       initialization_file_name = child.attrib.get('initialize')
       child.set('initialize','rosemount')
    if child.tag == 'run':
       dt         = child.attrib.get('dt')
       time_end   = child.attrib.get('end')
       child.set('end',str(end_time))  # set new time 
       time_begin = child.attrib.get('start') 
    print(child.tag, child.attrib)

for event in child:
    
    if event.attrib.get('name') == 'Start engine':
        start_engine_event_len = len(event)
        for i in range(0,start_engine_event_len):
            if event[i].attrib.get('name') == 'ap/altitude_setpoint':     
                altitude_setpoint =  event[i].attrib.get('value') # intiali target alt
                event[i].set('value',str(int_alt_setpoint))   # change alt_setpoint
            if event[i].attrib.get('name') == 'guidance/target_wp_latitude_rad':     
                target_wp_latitude_rad = event[i].attrib.get('value')
                event[i].set('value',str(int_lat_rad))        # set initial waypoint lat
            if event[i].attrib.get('name') == 'guidance/target_wp_longitude_rad':     
                target_wp_longitude_rad = event[i].attrib.get('value')  
                event[i].set('value',str(int_lon_rad))       
            if event[i].attrib.get('name') == 'ap/heading_setpoint':     
                target_wp_longitude_rad = event[i].attrib.get('value')  
                event[i].set('value',str(int_heading_deg))  
            if event[i].attrib.get('name') == 'ap/heading-setpoint-select':     
                target_wp_longitude_rad = event[i].attrib.get('value')  
                event[i].set('value',str(heading_setpoint_select))  
            # set initial waypoint lon
                
    if event.attrib.get('name') =='Set altitude for 1,000 ft.':
         event.set('name',('Set altitude for %s ft.' %int_alt_setpoint))    
         event[0].text = ('velocities/vc-fps ge %s' %str(velocity_fps)) # set velocity threshold
         event[1].set('value','1') # let altitude vary
         
    if event.attrib.get('name') =='Head to first waypoint':
        temp_wp_event = deepcopy(event)
        first_wp_len = len(event)
        event[0].text = ('\n        Set heading hold to selected waypoint (setpoint) instead of\n        previously specified heading when altitude surpasses %s feet.\n      ' %str(alt_wp_1_threshold))
        event[1].text = ('position/h-agl-ft  ge  %s' %str(alt_wp_1_threshold)) # set alt threshold
        event[4].set('name','ap/altitude_hold')
        event[4].set('value',str(altitude_hold_1st))          
        event[5].set('name','ap/altitude_setpoint')
        event[5].set('value',str(target_alt_1st))   
        event[5].set('action','FG_EXP')  
        event[5].set('tc',str(10))  
        alt_wp_1 = event[1].text[23:29] # only 3 digits
        for i in range(0,first_wp_len):
            if  event[i].attrib.get('name') == 'ap/active-waypoint':  
                # <set name="ap/afcs/altitude-trim-ft" value="2650.0" action="FG_RAMP" tc="90.0"/>
                active_wp =  event[i].attrib.get('value')  
    
    if event.attrib.get('name') =='Terminate':
        event[1].text = ('\n        guidance/wp-distance lt 100\n        ap/active-waypoint eq %s\n      ' %NO_tot_wp)
   
    # print(event.tag, event.attrib)

# append new events (waypoint) 

No_append_event =  NO_tot_wp - 1 
event = temp_wp_event
for i in range(No_append_event-1,-1,-1):
  
    child.append(deepcopy(event))
    for event in child:
        if event.attrib.get('name') == 'Terminate': 
            print('append a No.%s waypoint' %(i+2))
    if i == (No_append_event-1):        
        event.set('name', ('set to No.%s waypoint' %(i+2) )) 
        event[0].text =  ('Set to No.%s waypoint'  %(i+2)) 
        event[1].text  = ('\n        guidance/wp-distance lt %s \n        ap/active-waypoint eq %s\n      ' %(wp_distance[0,i],(i+1))) 
        event[2].set('name','guidance/target_wp_latitude_rad')
        event[2].set('value',str(wp_lat[i]))
        event[3].set('name','guidance/target_wp_longitude_rad')
        event[3].set('value',str(wp_lon[i]))
        event[4].set('name','ap/altitude_hold')
        event[4].set('value',str(target_alt_hold[i]))
        event[5].set('name','ap/altitude_setpoint')
        event[5].set('value',str(target_alt[i]))
        event[5].set('action','FG_EXP')  
        event[5].set('tc',str(10)) 
        e = ET.SubElement(event,'set')
        e.set('name',('ap/active-waypoint'))
        e.set('value',str(i+2))
    else:
        event.set('name', ('set to No.%s waypoint' %(i+2) )) 
        event[0].text =  ('Set to No.%s waypoint'  %(i+2)) 
        event[1].text  = ('\n        guidance/wp-distance lt %s \n        ap/active-waypoint eq %s\n      ' %(wp_distance[0,i],(i+1))) 
        event[2].set('name','guidance/target_wp_latitude_rad')
        event[2].set('value',str(wp_lat[i]))
        event[3].set('name','guidance/target_wp_longitude_rad')
        event[3].set('value',str(wp_lon[i]))
        event[4].set('name','ap/altitude_hold')
        event[4].set('value',str(target_alt_hold[i]))        
        event[5].set('name','ap/altitude_setpoint')
        event[5].set('value',str(target_alt[i]))
        event[5].set('action','FG_EXP')  
        event[5].set('tc',str(10)) 
        event[7].set('value',str(i+2))

for event in child:
    print(event.tag, event.attrib)


# output the xml file  

tree = ET.ElementTree(root)
tree.write('output.xml', pretty_print=True, xml_declaration=True,   encoding="utf-8")
