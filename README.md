# Telescopium
Observatory Automation

Telescopium is an observatory automation program written in Python and dependent only upon TheSkyX. Telescopium provides, 24/7 ongoing management of observatory and job scheduling. The project goal is to create a personalized observaroty control solution giving the user complete control of how the observatory is used building upon the complex functions provided by TheSkyX. It runs on Linux and Windows. 

Example, if you would like to run a dual sensor piggy back systm with coordinated exposures then this is within grasp with Telescopium.

Supported devices which comprise the observatory are: Mount, Main Focuser, Main Filter Wheel, Main Sensor, Guider Sensor, DC Power Switch, Weather Monitor, Dome (roll off roof control), and Park detector
    
Telescopium uses absolute and astronomical time based triggers and related input data to direct the observatory through a set of defined states each evening and night. The main states are IdlePM, PoweredUpPM, AllConnectedPM, ReadyToOpen, Open, OpenAndHomed, TakeFlats, ReadyToObserve, Observing, AllConnectedAM, and PoweredUpAM.

Each of these states is responsible to bring the observarory from idle towards observing and back to idle in prepration for next day.

A NeedToClose state triggered by weather is be entered into at multiple opportunities as needed.

Additional states of PreCheck, Initializing, and PANIC are provided for sanity check, and error recovery.

-----------------------------------------------------------------
MAIN STATES

IdlePM state is a powered down state, suitable for spending day light hours.

PoweredUpPM state is triggered by sunset - userOffset, and at this time all devides are powered up

AllConnectedPM state is time triggered and at this time, communicaitons to all devices are established and checked.

ReadyToOpen state is entered if all devices connect as expected. Exiting ReadyToOpen is time triggered. 

Open state, is as it suggests, however mount homing is not done if slew would result in arriving within a user defined sky seperation from the sun. From this state onward the NeedToClose state can be triggered by weather.

OpenAndHomed state is as it suggest.  

TakeFlats state is entered into based on time and will execute skyflats, OSC and filtered setups are supported.

ReadyToObserve, is entered into based on astronimical sunset. It is in this state that the work list is loaded and a work item is selected.

Observing state is entered into if a workitem is identified. Observing involves, plate solved slew, focusing, filter and main sensor operation. Images are calibrated by TheSkyX and save accordingly.

AllConnectedAM state is entered into realted to the end of astronomical night and will involde homing/parking, and closing dome.

PoweredUpAM state involves closing control communicaitons to devices in preparation for power off

Exiting PoweredUpAM states returns the observatory to IdlePM.

-----------------------------------------------------------------
PROGRAM PARTS

telescopiumMain.py is the main program it runs as a endless loop until terminated or closes due to PANIC

telescopium.py is the include file with classes for Observatory, DCPowerSwitch, ParkDetector, DomeController, WxMonitor, Mount, MainFiler, MainCamera, Guider, and Focuser 

-----------------------------------------------------------------
Credits

The packet passing function to TheSkyX is inspired from  https://github.com/RMcDOttawa/pySkyDarks3.git 

