import tkinter as tk
from data_stream import DataStream
import time, datetime, sys

debugMsg = False
infoMsg = True

class DisplayGUI:
    def __init__(self, root):
        if infoMsg == True: print("3D|Initialize program")
        self.root = root
        self.root.title("Data Stream")

        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', self.exitEsc)

        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{width}x{height}+0+0")
        self.root.attributes("-topmost", True)
        self.ds = DataStream()

        self.pageNow = 0
        self.timeThen = time.time()

        self.btn_exit = tk.Button(
            self.root,
            text="Exit",
            font=("Arial", 11, "bold"),
            bg="#AF3F3E",
            command=self.exitEsc
        )
        self.btn_exit.pack(pady=10)

        self.data_labels = []
        for i in range(13):
            lbl = tk.Label(
                root,
                text=f"Data{i+1} = Null",
                font=("Consolas", 13),
                anchor="w",
                width=50
            )
            lbl.pack()
            self.data_labels.append(lbl)

        self.autoscrollLbl = tk.Label(
            root,
            text="Autoscroll : 0s",
            font=("Arial", 10, "bold")
        )
        self.autoscrollLbl.pack(pady=10)
        if infoMsg == True: print("3D|Start Loop")
        self.update_loop()

    def exitEsc(self, event=None):
        self.root.attributes('-fullscreen', False)
        self.root.destroy()

    def updatePages(self, snapshot):
        data, colorProp, blinkProp = map(list, zip(*snapshot))
        for i in range(13):
            self.data_labels[i]["text"] = data[i]
            if colorProp[i]:
                self.data_labels[i]["fg"] = "red"
            else:
                self.data_labels[i]["fg"] = "#0F3057"

    def update_loop(self):
        timeNow = time.time()
        autoscroll = (self.ds.get_autoscroll())/10
        self.autoscrollLbl["text"] = f"Autoscroll : {autoscroll}s"
        if autoscroll > 0:
            if timeNow - self.timeThen > autoscroll:
                if self.pageNow == 6:
                    self.pageNow = 0
                else:
                    self.pageNow += 1
                self.timeThen = timeNow
        else:
            self.pageNow = 0
            
        snapshot = self.ds.get_snapshot(self.pageNow)
        if snapshot:
            self.updatePages(snapshot)

        print("3T|%s" % datetime.datetime.now())
        # print("3D|Still Running")
        sys.stdout.flush()
        
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(1000, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = DisplayGUI(root)
    root.mainloop()
