# JSBsim_Flightgear_Simulator

Objective: Enable users to create a mission from Qgroundcontrol and output an executable xml file for JSBsim
Created: 06/21/2018
Last updated: 06/21/2018

# Required Software:
The following softwares are required:
    1. Qgroundcontrol ( http://qgroundcontrol.com/ )
    2. JSBsim ( http://jsbsim.sourceforge.net/)
    3. FlightGear ( http://home.flightgear.org/ )
    4. Spyder or some IDE you can edit your python script
    
# Procedure: 
    
    1. Open Qgroundcontrol and create a mission.
    2. Add waypoints graphically to complete a mission (currently only support simpleItem)
    3. save the file as .plan file (JSON file)
    
    4. Open script json2xml.py in Python IDE spyder and give the .plan file
    5. Run json2xml.py, and this would create an executable xml file for JSBsim. It's named as "output.xml" 
          Note: the base.xml file is needed a baseline to create the executable xml file
    6. Similarly, run json2xml_init.py to create an initialization xml file
    
    7. Open 2 terminals for JSBsim and Flightgear respectively 
       In one terminal, launch Flightgear using the following command: 
       
       fgfs --native-fdm=socket,in,60,,5550,udp --fdm=external --enable-terrasync --httpd=8080
       
       Note: if this doesn't work, perhaps port wasn't setup correctly.
             You can check this by going into the folder jsbsim/data_output/flighgear.xml file 
             You can also open PHI map in a broswer (enabled by -httpd=8080)
       In one terminal, if you have a linux machine, then do the following:
       $ cd jsbsim
       $ mkdir build_linux
       $ cd build_linux
       $ cmake .. 
       $ make
       $ cd ..
             
       then you can enter the following command to start the simulation:
       
       jsbsim $ ./build_linux/src/JSBSim --script=scripts/output.xml --realtime --logdirectivefile=data_output/flightgear.xml
