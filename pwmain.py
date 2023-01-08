import pypowerwall
from datetime import datetime
import time
import curses
#dependacy init
stdscr = curses.initscr()
htmlFail = 0
#login credits
password = '' #last 5 digits of your gateway serial
email = '' #login email
host = '' #local ip address for your powerwall
timezone = 'America/Los_Angeles' #ex; America/Los_Angeles

#connection
print("connecting...")
pw = pypowerwall.Powerwall(host, password, email, timezone)
print("connected to PowerWall+!")
# Some System Info
print("Site Name: %s - Firmware: %s - DIN: %s" % (pw.site_name(), pw.version(), pw.din()))
print("System Uptime: %s\n" % pw.uptime())

# Fetching  Sensor PWR data
grid = pw.grid()
solar = pw.solar()
battery = pw.battery()
home = pw.home()
bat_temp = pw.temps()
pwr = pw.power()

#ASCII MSG
outWARN1 = '''
 ██████  ██████  ██ ██████  
██       ██   ██ ██ ██   ██ 
██   ███ ██████  ██ ██   ██ 
██    ██ ██   ██ ██ ██   ██ 
 ██████  ██   ██ ██ ██████  
                                                  
'''
outWARN2 = '''
 ██████  ██    ██ ████████  █████   ██████  ███████ ██ 
██    ██ ██    ██    ██    ██   ██ ██       ██      ██ 
██    ██ ██    ██    ██    ███████ ██   ███ █████   ██ 
██    ██ ██    ██    ██    ██   ██ ██    ██ ██         
 ██████   ██████     ██    ██   ██  ██████  ███████ ██ 
                                                                                                 
'''
outWARN3 = '''
 █████  ██      ███████ ██████  ████████ 
██   ██ ██      ██      ██   ██    ██    
███████ ██      █████   ██████     ██    
██   ██ ██      ██      ██   ██    ██    
██   ██ ███████ ███████ ██   ██    ██    
'''
outSYNC = '''
███████ ██    ██ ███    ██  ██████       
██       ██  ██  ████   ██ ██            
███████   ████   ██ ██  ██ ██            
     ██    ██    ██  ██ ██ ██            
███████    ██    ██   ████  ██████ ██ ██ 
                                                                        
'''


t1 = 0
def outagewarn():
    global outWARN1, outWARN2, outWARN3, outSYNC, alrtRes, t1, alrtSyn
    if pw.grid_status("numeric") == -1:
        stdscr.addstr(outSYNC + "\n")           
    elif pw.grid_status("numeric") == 0:
        if t1 == 0:
            stdscr.addstr(outWARN1 + "\n")
        elif t1 == 1:
            stdscr.addstr(outWARN2 + "\n")
        elif t1 == 2:
            stdscr.addstr(outWARN3 + "\n")
            t1 = 0
    t1 += 1

 

def calculation(mode):
    global pw
    if mode == 1: #Discharge
        return (13.5*((pw.level()/100)-.145))/abs(pw.power()["battery"]/1000)
    if mode == 0: #charge
        return (13.5-(13.5*(pw.level()/100)))/(abs(pw.power()["battery"]/1000))

def dms_trans(dms):
    global datetime
    test = dms #in hours
    hours = int(test)
    minutes = (test-int(test))*60
    seconds = (minutes-int(minutes))*60
    lst_tm = [0,0,0,0] #day,hour,minute,second
    if (round(seconds) + int(datetime.now().strftime("%S"))) > 60:
        lst_tm[2] = 1
        lst_tm[3] = round(seconds) + int(datetime.now().strftime("%S")) - 60
    else:  
        lst_tm[3] = round(seconds) + int(datetime.now().strftime("%S"))
    if (int(minutes) + int(datetime.now().strftime("%M"))) > 60:
        lst_tm[1] += 1
        lst_tm[2] += int(minutes) + int(datetime.now().strftime("%M")) - 60
    else:
        lst_tm[2] += int(minutes) + int(datetime.now().strftime("%M"))
    if (hours + int(datetime.now().strftime("%H"))) > 24:
        lst_tm[0] = 1
        lst_tm[1] += (int(test) + int(datetime.now().strftime("%H"))) - 24
    else:
        lst_tm[1] += (int(test) + int(datetime.now().strftime("%H")))
    calculatedtm = datetime.now().strftime("%Y-%m-") + str(lst_tm[0]+int(datetime.now().strftime("%d"))) + " " + str(lst_tm[1]) + ":" + str(lst_tm[2]) + ":" + str(lst_tm[3])
    return calculatedtm
    

#Calculating ETA

def dataStat(typ):
    global htmlFail
    try:
        match typ:
            case "Grid":
                stdscr.addstr("Grid Usage: %0.3fkW\n" % (float(pw.grid())/1000.0))
            case "Solar":
                stdscr.addstr("Solar Power: %0.3fkW\n" % (float(pw.solar())/1000.0))
            case "Battery":
                stdscr.addstr("Battery Usage: %0.3fkW\n" % (float(pw.battery())/1000.0))
            case "Home":
                stdscr.addstr("Home Usage: %0.3fkW\n" % (float(pw.home())/1000.0))
            case "BTemp":
                stdscr.addstr("Battery Temperature: %0.2fC\n" % (float(*pw.temps().values())))
    except:
        htmlFail += 1
        match typ:
            case "Grid":
                stdscr.addstr("Grid Usage: ERROR")
            case "Solar":
                stdscr.addstr("Solar Power: ERROR")
            case "Battery":
                stdscr.addstr("Battery Usage: ERROR")
            case "Home":
                stdscr.addstr("Home Usage: ERROR")
            case "BTemp":
                stdscr.addstr("Battery Temperature: ERROR")

def pwrStat(typ):
    global htmlFail
    try:
        match typ:
            case "btLvl":
                stdscr.addstr("Battery level: %0.0f%%\n" % pw.level())
            case "btLvld":
                stdscr.addstr("Battery level Detailed: %s%%\n" % pw.level())
            case "pwrMetrics":
                stdscr.addstr("Combined power metrics: %r\n" % pw.power())
    except:
        htmlFail += 1
        match typ:
            case "btLvl":
                stdscr.addstr("Battery level: ERROR")
            case "btLvld":
                stdscr.addstr("Battery level Detailed: ERROR")
            case "pwrMetrics":
                stdscr.addstr("Combined power metrics: ERROR")


while(True): 
    # Display Data
    pwrStat("btLvl")
    pwrStat("btLvld")
    pwrStat("pwrMetrics")
    stdscr.addstr("\n")

    # Display Power in kW
    dataStat("Grid")
    dataStat("Solar")
    dataStat("Battery")
    dataStat("Home")
    dataStat("BTemp")
    stdscr.addstr("\n")
    try:
        stdscr.addstr("Grid Status: %s" % pw.grid_status("string"))
    except:
        stdscr.addstr("Grid Status: UNKNOWN ERROR")
    stdscr.addstr("\n")
    stdscr.addstr("Time Local: %s\n" %(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    #function calculation(int), set the parameter equal to 1 when dischargings or 0 when charging
    try: 
        if pw.power()["battery"] == 0:
            stdscr.addstr("On standby...\n")
        elif pw.power()["battery"] > 0:
            stdscr.addstr("Discharging....\n")
            stdscr.addstr("ETA Til 15%: " + str(calculation(1)) + " hours\n") 
            stdscr.addstr("ETA Til 15%: " + dms_trans(calculation(1)) + "\n")
        else:
            stdscr.addstr("Charging....\n")
            stdscr.addstr("ETA Til Full: " + str(calculation(0)) + " hours\n")
            stdscr.addstr("ETA Til Full: " + dms_trans(calculation(0)) + "\n")
    except:
        stdscr.addstr("UNKNOWN\n")
        stdscr.addstr("ETA Til Full: ERROR\n")
        stdscr.addstr("ETA Til Full: ERROR\n")
    stdscr.addstr("Failed Connections: %s\n" %str(htmlFail))
    stdscr.addstr("\n")
    outagewarn()
    stdscr.refresh()
    time.sleep(5)
    stdscr.clear()
'''
# Raw JSON Payload Examples
print("Grid raw: %r\n" % pw.grid(verbose=True))
print("Solar raw: %r\n" % pw.solar(verbose=True))

# Display Device Vitals
print("Vitals: %r\n" % pw.vitals())

# Display String Data
print("String Data: %r\n" % pw.strings())
'''