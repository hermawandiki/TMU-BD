import threading
import subprocess
import time
import datetime
import os
import sys
import logging
from toolboxTMU import initTkinter

ts = time.strftime("%Y%m%d")
logName = r'/home/pi/tmu-v2-smart/assets/sysdata-test/syslog-' + ts + '.log'
logging.basicConfig(filename=logName, format='%(asctime)s | %(levelname)s: %(message)s', level=logging.DEBUG)

os.chdir('/home/pi/tmu-v2-smart/')

class App:
    def __init__(self):
        try:
            logging.info("Initializing App")
            self.progStat = [True, True, False]
            self.stopFlag = [False, False, False]
            self.streamsHB = ["init", "init", "init"]
            self.streamsDebug = ["", ""]
            
            logging.debug("Start module_IO")
            self.proc2 = self.start_proc("module_IO.py")
            logging.debug("Sleep 1s then start data_handler.py")
            time.sleep(1)
            self.proc1 = self.start_proc("data_handler.py")
            
            logging.debug("Init GUI Tkinter")
            self.main_screen = initTkinter()
            self.main_screen.restartBtn["command"] = self.restart
            self.main_screen.stopBtn1["command"] = self.stop_proc1
            self.main_screen.stopBtn2["command"] = self.stop_proc2
            self.main_screen.stopBtn3["command"] = self.stop_proc3
            self.main_screen.stopBtn3["state"] = 'disabled'

            logging.debug("Start Threads - Streaming proc 1 and 2, update TK, Watchdog Program")
            self.thread1 = threading.Thread(target=self.stream_proc, args=(self.proc1, 0))
            self.thread2 = threading.Thread(target=self.stream_proc, args=(self.proc2, 1))
            self.thread3 = threading.Thread(target=self.update_tk, args=(1,))
            self.thread4 = threading.Thread(target=self.watchdog, args=(60,))
            self.thread1.start()
            self.thread2.start()
            self.thread3.start()
            self.thread4.start()
            
            self.main_screen.screen.mainloop()
        except Exception as e:
            logging.error(f"Error during App initialization: {e}")
            self.terminate_procs()
            sys.exit(1)

    def start_proc(self, script):
        logging.debug(f"Starting process: {script}")
        try:
            proc = subprocess.Popen(["python3", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.debug(f"Process {script} started with PID: {proc.pid}")
            return proc
        except Exception as e:
            logging.error(f"Failed to start process {script}: {e}")
            return None

    def stream_proc(self, proc, index):
        try:
            if not proc:
                logging.error(f"Process {index} is None, skipping stream_proc")
                return
            with proc.stdout:
                for line in iter(proc.stdout.readline, b''):
                    code = line[0:1]
                    type = line[1:2]
                    message = line[3:].decode("utf-8").strip()
                    if code == b'1':
                        if type == b'T':
                            self.streamsHB[0] = message
                        elif type == b'D':
                            self.streamsDebug[0] = message
                            logging.debug("proc1 " + message)
                    elif code == b'2':
                        if type == b'T':
                            self.streamsHB[1] = message
                        elif type == b'D':
                            self.streamsDebug[1] = message
                            logging.debug("proc2 " + message)
                    else:
                        logging.error(f"Unexpected code: {code}")
        except Exception as e:
            logging.error(f"Error in stream_proc {index}: {e}")

    def update_tk(self, interval):
        try:
            while True:
                self.main_screen.lastHB1Lbl['text'] = self.streamsHB[0]
                self.main_screen.lastHB2Lbl['text'] = self.streamsHB[1]
                self.main_screen.lastHB3Lbl['text'] = self.streamsHB[2]

                self.main_screen.debug1Lbl['text'] = self.streamsDebug[0]
                self.main_screen.debug2Lbl['text'] = self.streamsDebug[1]
                
                self.main_screen.prog1Lbl['text'] = "Running" if self.progStat[0] else "Stop"
                self.main_screen.stopBtn1['state'] = 'normal' if self.progStat[0] else 'disabled'

                self.main_screen.prog2Lbl['text'] = "Running" if self.progStat[1] else "Stop"
                self.main_screen.stopBtn2['state'] = 'normal' if self.progStat[1] else 'disabled'

                self.main_screen.prog3Lbl['text'] = "Running" if self.progStat[2] else "Stop"
                self.main_screen.stopBtn3['state'] = 'normal' if self.progStat[2] else 'disabled'
                
                time.sleep(interval)
        except Exception as e:
            logging.error(f"Error in update_tk: {e}")
    
    def watchdog(self, interval):
        try:
            anchorDays = datetime.datetime.now().day
            lastLabel1 = self.main_screen.lastHB1Lbl['text']
            lastLabel2 = self.main_screen.lastHB2Lbl['text']
            while True:
                nowTime = datetime.datetime.now()
                time.sleep(interval)
                currentLabel1 = self.main_screen.lastHB1Lbl['text']
                currentLabel2 = self.main_screen.lastHB2Lbl['text']
                if self.streamsDebug[0] == "Restart" or self.streamsDebug[1] == "Restart":
                    logging.info(f"Restarting from process: {nowTime}")
                    self.restart()
                if lastLabel1 == currentLabel1 or lastLabel2 == currentLabel2 or anchorDays != nowTime.day:
                    if self.progStat[0] and self.progStat[1]:
                        logging.info(f"Restarting machine: {nowTime}")
                        self.restart()
                    else:
                        pass
                else:
                    lastLabel1 = currentLabel1
                    lastLabel2 = currentLabel2
        except Exception as e:
            logging.error(f"Error in watchdog: {e}")

    def restart(self):
        try:
            self.terminate_procs()
            time.sleep(2)
            os.execv(sys.executable, [sys.executable] + ['/home/pi/tmu-v2-smart/main.py'])
        except Exception as e:
            logging.error(f"Error during restart: {e}")

    def stop_proc1(self):
        try:
            if self.proc1:
                self.proc1.terminate()
                self.progStat[0] = False
        except Exception as e:
            logging.error(f"Error stopping proc1: {e}")

    def stop_proc2(self):
        try:
            if self.proc2:
                self.proc2.terminate()
                self.progStat[1] = False
        except Exception as e:
            logging.error(f"Error stopping proc2: {e}")
    
    def stop_proc3(self):
        try:
            self.progStat[2] = False
        except Exception as e:
            logging.error(f"Error stopping proc3: {e}")

    def terminate_procs(self):
        try:
            if self.proc1:
                self.proc1.terminate()
            if self.proc2:
                self.proc2.terminate()
        except Exception as e:
            logging.error(f"Error during terminate_procs: {e}")

if __name__ == "__main__":
    try:
        logging.debug("Starting App")
        app = App()
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")
        sys.exit(1)
