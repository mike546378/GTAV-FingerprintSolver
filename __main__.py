import numpy as np
import cv2
import subprocess
import time
import mss
import sys
import os 

def run():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    size = []
    pos = []
    if sys.platform == "win32":
        import win32gui
        hwnd = win32gui.FindWindow(None, "Grand Theft Auto V")
        rect = win32gui.GetWindowRect(hwnd)
        pos = [rect[0], rect[1]]
        size = [rect[2], rect[3]]
        print(rect)
    else:
        print("Focus GTAV window...")
        time.sleep(3)
        res = str(subprocess.check_output(["xdotool", "getwindowfocus", "getwindowgeometry"]))
        res = res.split("\\n")
        pos = res[1]
        pos = pos[pos.index(":")+2:]
        pos = pos[:pos.index(" ")]
        size = res[2]
        size = size[size.index(":")+2:]
        print("GTA at: " + pos + ", " + size)
        pos = pos.split(",")
        pos = [int(pos[0]), int(pos[1])]
        size = size.split("x")
        size = [int(size[0]), int(size[1])]
    with mss.mss() as sct:
        w = int(float(size[0]) * 0.8)
        h = int(float(size[1]) * 0.8)
        x = int(pos[0] + (size[0]-w)/2)
        y = int(pos[1] + (size[1]-h)/2)

        monitor = {"top": y, "left": x, "width": w, "height": h}
        print(monitor)
        
        prints = []
        for i in range(0,4):
            prints.append(cv2.imread(dir_path + "/print_"+str(i)+".png"))
        while True:
            img = np.array(sct.grab(monitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, (0,0,0), (255, 160, 255))
            img = cv2.bitwise_and(img, img, mask=mask)
            
            (h, w) = img.shape[:2]
            new_width = 800
            r = float(new_width)/float(w)
            img = cv2.resize(img, (new_width, int(h*r)), interpolation = cv2.INTER_CUBIC)
            
            regionPrint = img[10:300, 400:600].copy()

            maxPos = 0
            maxVal = 0
            maxLoc = 0
            for i in range(0,4):
                res = cv2.matchTemplate(regionPrint, prints[i], cv2.TM_CCOEFF)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                if max_val > maxVal :
                    maxVal = max_val
                    maxLoc = max_loc
                    maxPos = i
            
            (ph, pw) = prints[i].shape[:2]
            if maxLoc and maxVal > 30000000:
                cv2.rectangle(img, (maxLoc[0]+400, maxLoc[1]+10), (maxLoc[0]+pw+400, maxLoc[1]+ph+10), (255,0,0), 5)
                regSolution = img[80:380,135:290].copy()
                for i in range(0,4):
                    p = cv2.imread(dir_path + "/" + str(maxPos) + "/" + str(i) + ".png")
                    res = cv2.matchTemplate(regSolution, p, cv2.TM_CCOEFF)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                    cv2.rectangle(img, (max_loc[0]+135, max_loc[1]+80), (max_loc[0]+135+60, max_loc[1]+80+60), (0,0,255), 2)
            else:
               time.sleep(1)
            cv2.waitKey(1)
            cv2.imshow("frame", img)




if __name__ == "__main__":
    run()