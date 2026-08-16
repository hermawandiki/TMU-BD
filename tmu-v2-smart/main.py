import threading
import subprocess
import time
import datetime
import os
import sys
import logging
import data_stream
from toolboxTMU import initTkinter

ts = time.strftime("%Y%m%d")
logName = r'/home/pi/tmu-v2-smart/assets/sysdata-test/syslog-' + ts + '.log'
logging.basicConfig(
    filename=logName,
    format='%(asctime)s | %(levelname)s: %(message)s',
    level=logging.DEBUG
)

os.chdir('/home/pi/tmu-v2-smart/')

class App:
    def __init__(self):
        self.data_stream = data_stream.DataStream()
        try:
            logging.info("Initializing App")
            self.timeThen = time.time()
            self.pageNow = 0
            self.progStat = [True, True, False]
            self.streamsHB = ["init", "init", "init"]
            self.streamsDebug = ["", ""]

            logging.debug("Start module_IO")
            self.proc2 = self.start_proc("module_IO.py")

            logging.debug("Sleep 1s then start data_handler.py")
            time.sleep(1)
            self.proc1 = self.start_proc("data_handler.py")

            logging.debug("Sleep 1s then start displayGUI.py")
            time.sleep(1)
            self.proc3 = self.start_proc("displayGUI.py")
              
            logging.debug("Sleep 1s then start modbusTcpServer.py")
            time.sleep(1)
            self.proc4 = self.start_proc("modbusTcpServer.py")

            logging.debug("Init GUI Tkinter")
            self.main_screen = initTkinter()
            self.main_screen.restartBtn["command"] = self.restart
            self.main_screen.stopBtn1["command"] = self.stop_proc1
            self.main_screen.stopBtn2["command"] = self.stop_proc2
            self.main_screen.stopBtn3["command"] = self.stop_proc3
            self.main_screen.stopBtn3["state"] = 'disabled'
            #self.main_screen.after(0, self.main_Screen.iconify)

            logging.debug("Start Threads - Streaming proc 1 and 2 + Watchdog")

            self.thread1 = threading.Thread(
                target=self.stream_proc, args=(self.proc1, 0), daemon=True)
            self.thread2 = threading.Thread(
                target=self.stream_proc, args=(self.proc2, 1), daemon=True)
            self.thread3 = threading.Thread(
                target=self.stream_proc, args=(self.proc3, 1), daemon=True)
            self.thread4 = threading.Thread(
                target=self.stream_proc, args=(self.proc4, 1), daemon=True)
            self.thread5 = threading.Thread(
                target=self.watchdog, args=(60,), daemon=True)

            self.update_tk()
            self.main_screen.screen.mainloop()
            self.thread1.start()
            self.thread2.start()
            self.thread3.start()
            self.thread4.start()
            self.thread5.start()
            
        except Exception as e:
            logging.error(f"Error during App initialization: {e}")
            self.terminate_procs()
            sys.exit(1)

    def start_proc(self, script):
        logging.debug(f"Starting process: {script}")
        try:
            proc = subprocess.Popen(
                ["python3", script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            logging.debug(f"Process {script} started with PID: {proc.pid}")
            return proc
        except Exception as e:
            logging.error(f"Failed to start process {script}: {e}")
            return None

    def stream_proc(self, proc, index):
        try:
            if not proc or not proc.stdout:
                logging.error(f"Process {index} is None")
                return

            for line in iter(proc.stdout.readline, ''):
                line = line.strip()

                if len(line) < 3:
                    continue

                code = line[0]
                msg_type = line[1]
                message = line[3:]

                if code == '1':
                    if msg_type == 'T':
                        self.streamsHB[0] = message
                    elif msg_type == 'D':
                        self.streamsDebug[0] = message
                        logging.debug("proc1 " + message)

                elif code == '2':
                    if msg_type == 'T':
                        self.streamsHB[1] = message
                    elif msg_type == 'D':
                        self.streamsDebug[1] = message
                        logging.debug("proc2 " + message)

                else:
                    logging.error("Child Output: " + line)

        except Exception as e:
            logging.error(f"Error in stream_proc {index}: {e}")
    
    def update_tk(self):
        autoscroll = self.data_stream.get_autoscroll()
        try:
            self.main_screen.data9Txt['text'] = "Autoscroll : %ss" % autoscroll
            
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

        except Exception as e:
            logging.error(f"Error in update_tk: {e}")

        self.main_screen.screen.after(1000, self.update_tk)

    def watchdog(self, interval):
        try:
            anchor_day = datetime.datetime.now().day
            lastHB1 = self.streamsHB[0]
            lastHB2 = self.streamsHB[1]

            while True:
                time.sleep(interval)
                now = datetime.datetime.now()

                if self.streamsDebug[0] == "Restart" or self.streamsDebug[1] == "Restart":
                    logging.info("Restart triggered by child request")
                    self.restart()

                if (lastHB1 == self.streamsHB[0] or
                        lastHB2 == self.streamsHB[1] or
                        anchor_day != now.day):

                    if self.progStat[0] and self.progStat[1]:
                        logging.info("Restart triggered by watchdog freeze detection")
                        self.restart()
                else:
                    lastHB1 = self.streamsHB[0]
                    lastHB2 = self.streamsHB[1]

        except Exception as e:
            logging.error(f"Error in watchdog: {e}")

    def restart(self):
        try:
            self.terminate_procs()
            time.sleep(2)
            os.execv(sys.executable, [sys.executable] +
                     ['/home/pi/tmu-v2-smart/main.py'])
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
            if self.proc2:
                self.proc2.terminate()
                self.progStat[2] = False
        except Exception as e:
            logging.error(f"Error stopping proc3: {e}")

    def terminate_procs(self):
        try:
            if self.proc1:
                self.proc1.terminate()
            if self.proc2:
                self.proc2.terminate()
            if self.proc3:
                self.proc3.terminate()
            if self.proc4:
                self.proc4.terminate()
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
