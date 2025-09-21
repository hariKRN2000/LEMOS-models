import sys
import logging
import pyautogui
import time
from watchdog.observers import Observer
import watchdog.events
import datafile_manager
import ble_comms
import numpy as np

measurement_interval = 600
default_on_time = (measurement_interval - 120) / 2
max_on_time = measurement_interval - 120
FL_by_OD_max_old = 30000
FL_by_OD_max_new = 25000
conv_factor = FL_by_OD_max_new/FL_by_OD_max_old

p_gain = (0.1 / 1.875)*(1/conv_factor)

started = False
start_time = 0
overall_start = 0

ctrl_wells = ['A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11',
              'H9',  'G9',  'F9',  'E9',  'D9',  'C9',  'B9',  'A9']

neg_well = 'A11'
g_ctrl_wells = ['B11', 'C11', 'D11']
r_ctrl_wells = ['E11', 'F11', 'G11']
stpt2_wells  = [ 'A9',  'B9',  'C9', 'D9']
stpt1_wells  = [ 'E9',  'F9',  'G9']
impulse_wells =[ 'H9',  'A11', 'H11']
neg_index = ctrl_wells.index(neg_well)

ctrl_times = [default_on_time, default_on_time+0.5, default_on_time+1, default_on_time+1.5,
              default_on_time+0.1, default_on_time + 0.2, default_on_time + 0.3, default_on_time + 0.4,
              default_on_time, default_on_time, default_on_time, default_on_time,
              default_on_time, default_on_time, default_on_time, default_on_time]

# CHANGE THIS TO DESIRED VALUES PRIOR TO RUN
# make this a curve with respect to time
ctrl_setpts = [20, 20, 20, 20, 20, 20, 20, 20,
               20, 20, 20, 20, 20, 20, 20, 20]

# blanks = [0.118, 0.145, 0.145, 0.145, 0.122, 0.182, 0.197, 0.145, 0.145, 0.155, 0.190, 0.200, 0.138, 0.128, 0.134, 0.000]
blanks = np.ones(16) * 0.13

ctrl_pts =  {(0,20)  : 400,
             (20,40) : 500,
             (40,60) : 600,
             (60,80) : 800,
             (80,100): 1000,
             (100,660): 5000}

filename = input("Enter a filename for the runlog: ")

# bluetooth communication intialization
log_file = open(input("Enter a filename for the bluetooth communication log: ") + ".out", 'a')
ble_comms.connect_device('COM5', 115200, 0.1)

path_to_datafile = sys.argv[1] + '/Datafile' if len(sys.argv) > 1 else './Datafile'
datafile_filename = 'Datafile/test_040625.csv'

def run_experiment():
    global started
    global start_time
    global overall_start
    print("Starting in 2 seconds...")
    time.sleep(2)

    
    

    # Adding this error handling condition to press on OK if the "There are no compatible readers..." error pops up.
    # This error pops when the pyautogui clicks on run when an interval is already started
    try: 
        OK_loc = pyautogui.center(pyautogui.locateOnScreen("search_targets/compatible_reader_OK.PNG"))
        pyautogui.click(x = OK_loc.x, y = OK_loc.y)
        time.sleep(1)
    except BaseException:
        run_loc = pyautogui.center(pyautogui.locateOnScreen("search_targets/1.run.PNG"))
        pyautogui.click(x=run_loc.x, y=run_loc.y)
        time.sleep(2)
    else:
        run_loc = pyautogui.center(pyautogui.locateOnScreen("search_targets/1.run.PNG"))
        pyautogui.click(x=run_loc.x, y=run_loc.y)
        time.sleep(2)
    
    continue_loc = pyautogui.center(pyautogui.locateOnScreen("search_targets/2.continue.PNG"))
    pyautogui.click(x=continue_loc.x, y=continue_loc.y)
    time.sleep(7)

    load_plate_loc = pyautogui.center(pyautogui.locateOnScreen("search_targets/3.loadplate.PNG"))
    pyautogui.click(x=load_plate_loc.x, y=load_plate_loc.y)

    
    start_time = time.time()
    if(not started):
        overall_start = start_time
        print("starting run...")
    started = True

# set up file system watcher
logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

class FileHandler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, filename):
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=[filename])

    def on_created(self, event):
        print("Datafile was created! - % s" % event.src_path)
        # extract the values and re-run the experiment
        run_experiment()

    def on_modified(self, event):
        print("Datafile was modified! - % s" % event.src_path)
        time.sleep(3)

        # extract the values and re-run the experiment
        try:
            datafile_manager.read_and_save(datafile_filename)
        except BaseException as error:
            print("Error reading csv export...")
            print(error)
            return

        # get latest rows of each table
        fl_latest = datafile_manager.get_fl_latest()
        od_latest = datafile_manager.get_od_latest()
        od_blank = blanks[0]
        fl_blank = 30

        newest_index = list(fl_latest.get(ctrl_wells[neg_index]).keys())[-1]

        neg_fl = int(fl_latest.get(ctrl_wells[neg_index])[newest_index]) - fl_blank
        neg_od = float(od_latest.get(ctrl_wells[neg_index])[newest_index]) - od_blank
        # use these values to do something
        for i in range(len(ctrl_wells)):
            od_blank = blanks[i]
            od = od_latest.get(ctrl_wells[i])[newest_index]
            if od == 'OVRFLW' or od == "OVRFLW": # Sometimes OD can be OVRFLW if there is something in the well (like stuck well mold)
                od = 1
            od = min(float(od), 32) - od_blank
            fl = fl_latest.get(ctrl_wells[i])[newest_index]
            if fl == 'OVRFLW' or fl == "OVRFLW":
                fl = 100000
            fl = int(fl) - fl_blank

            

            print("processing well", ctrl_wells[i], "with fl", str(fl), "and od", str(od))

            curr_time = (time.time() - overall_start) / 60
            fl_by_od = (fl/od) - (neg_fl/neg_od)
            # ctrl_pt = 1.875 * get_ctrl_pt(curr_time)
            st_pt_1 = 11500
            st_pt_2 = 18500
            ctrl_pt = st_pt_1
            if ctrl_pt == st_pt_1 and ctrl_wells[i] in stpt2_wells:
                ctrl_pt = st_pt_2
            on_time = p_gain * (ctrl_pt - fl_by_od)

            print("calculated raw on_time of:", on_time, "seconds")
            if on_time > max_on_time:
                on_time = max_on_time
            elif on_time < 0:
                on_time = 0
            ctrl_times[i] = on_time
            print()

        print("New duration setpoints calculated: ", ctrl_times)

        
        # delete the datafile, a new one will be created in the next iteration
        try:
            datafile_manager.remove()
        except BaseException as error:
            print("Error deleting csv export...")
            print(error)
            return

        # run again
        try:
            run_experiment()
        except BaseException as error:
            print("Error running a new experiment...")
            print(error)


def get_ctrl_pt(t):
    for i in ctrl_pts.keys():
        if t > i[0] and t <= i[1]:
            return ctrl_pts[i]

    return ctrl_pts[i]


def handleTiming():
    if not started:
        print("not started yet!")
        return

    to_send = ""
    curr_time = time.time() - start_time
    corrected_time = curr_time % measurement_interval
    for i in range(len(ctrl_wells)):
        if i in (17,18):
            to_send += "o"
        elif (corrected_time > 60 and corrected_time < (measurement_interval - 60)) and (ctrl_wells[i] in g_ctrl_wells):
            to_send += "g"
        elif (corrected_time > 60 and corrected_time < (measurement_interval - 60)) and (ctrl_wells[i] in r_ctrl_wells):
            to_send += "r"
        elif (ctrl_wells[i] in impulse_wells) and False and (overall_start == start_time) and (corrected_time > 60) and (corrected_time < 120):
            print(start_time)
            print(overall_start)
            print("starting impulse")
            to_send += "g"
        elif (ctrl_wells[i] in impulse_wells) and (corrected_time > 60) and False and (corrected_time < (measurement_interval - 60)):
            to_send += "r"
        elif(corrected_time < ctrl_times[i] + 60 and corrected_time > 60):
            to_send += "g"
        elif (corrected_time > 60 and corrected_time < (measurement_interval - 60)):
            to_send += "r"
        else:
            to_send += "o"
    to_send += "\n"
    ble_comms.write_data(to_send, log_file, curr_time + start_time - overall_start)
        


datafile_event_handler = FileHandler(datafile_filename)
datafile_observer = Observer()
datafile_observer.schedule(datafile_event_handler, path_to_datafile, recursive = True)
datafile_observer.start()

if len(ctrl_wells) != len(ctrl_times) or len(ctrl_wells) != len(ctrl_setpts):
    print("Check setpoint and on-time arrays. Stopping execution...")

try:
    run_experiment()
    while True:
        handleTiming()
        serial_str = ble_comms.read_data()
        if serial_str != "":
            print(serial_str)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Stopping experiment.")
    datafile_observer.stop()
    log_file.close()

datafile_observer.join()
