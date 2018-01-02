import time
import os
import cv2
import numpy as np

i = 0


def centerCoutour(c):
    M = cv2.moments(c)
    if (M["m00"] == 0):
        cntx1 = c[0]
        return 0, np.array([cntx1[0][0], cntx1[0][1]])
    else:
        return np.array([int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])])


lower_green = np.array([110, 10, 1])
upper_green = np.array([140, 255, 120])


def startjump(frameName):
    print frameName
    parent_dir = os.path.abspath(frameName + "/../")
    frame = cv2.imread(frameName)
    print frame.shape
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv[320:620, :])
    avgH = cv2.mean(h)[0]
    avgS = cv2.mean(s)[0]

    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cv2.imwrite(parent_dir + "/mask.jpg", mask)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    chessPit = None
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255))
        print "c = "
        print (w, h)
        if 142 > h > 137 > 78 > w > 74:
            chessPit = (x + w / 2, int(y + 0.85 * h))
            break
        elif 58 <= h <= 61 and 58 <= w <= 61:
            chessPit = (x + w / 2, int(y + 191))
            break

    top = 10000
    hDiff = 12
    print chessPit[1]
    print chessPit[1] - 520 - 5
    while top > chessPit[1] - 191 - 520 - 5 and hDiff > 0:
        bgMask = cv2.inRange(hsv[520:1030, :], np.array([avgH - hDiff, 1, 1]), np.array([avgH + hDiff, 150, 255]))
        hDiff -= 1

        bgMask = cv2.bitwise_not(bgMask)
        bgMask = cv2.erode(bgMask, None, iterations=2)
        bgMask = cv2.dilate(bgMask, None, iterations=2)
        bgMask[chessPit[1] - 520 - 191:chessPit[1] - 520, chessPit[0] - 96/2:chessPit[0] + 96/2] = 0
        cnts = cv2.findContours(bgMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        print ("hDiff = "+str(hDiff))
        print ("len = "+str(len(cnts)))
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            print "lalala"
            print (x, y, w, h)
            if w > 1000:
                continue
            print y
            # cv2.rectangle(bgMask, (x, y), (x + w, y + h), 120, 1)
            if y < top:
                top = y
        cv2.imwrite(parent_dir + "/bgmask.jpg", bgMask)

    slice = bgMask[top:top + 1, :]
    cv2.imwrite(parent_dir + "/slice.jpg", slice)
    _, pointsX = np.nonzero(slice)
    x = np.average(pointsX)
    x = np.int(x)
    y = 520 + top
    print "top = "+str(y)
    targetPoint = (x, y)
    print targetPoint
    targetColor = frame[y + 1, x, :]
    lowerTarC = targetColor - 15
    lowerTarC[lowerTarC > targetColor] = 0
    upperTarC = targetColor + 15
    upperTarC[upperTarC < targetColor] = 255
    print upperTarC
    targetMask = cv2.inRange(frame[520:1130], lowerTarC, upperTarC)
    targetMask = cv2.erode(targetMask, None, iterations=2)
    targetMask = cv2.dilate(targetMask, None, iterations=2)
    cv2.imwrite(parent_dir + "/targetMask.jpg", targetMask)
    cnts = cv2.findContours(targetMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    targetPoint = (targetPoint[0], targetPoint[1] + 10)
    print "len - "+str(len(cnts))
    tp = targetPoint
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        print (x, y, w, h)
        if x < tp[0] < x + w and y < tp[1] - 520 < y + h:
            cv2.rectangle(frame, (x, y + 520), (x + w, y + h + 520), (255, 0, 0))
            if len(cnts) >= 12:
                w, h = cv2.minAreaRect(c)[1]
                if w/h < 1/4 or w/h > 4:
                    targetPoint = (x, y)
                    break
            targetPoint = centerCoutour(c)
            break

    targetPoint = (targetPoint[0], targetPoint[1]+520)
    print targetPoint

    cv2.line(frame, chessPit, (targetPoint[0], targetPoint[1]), (0, 0, 255))
    cv2.imwrite(parent_dir + "/result.jpg", frame)
    distance = ((targetPoint[0] - chessPit[0]) ** 2 + (targetPoint[1] - chessPit[1]) ** 2) ** 0.5
    print distance
    time = int(distance * 1.406097005)
    print time
    return time

os.system("rm -rf /Users/Wen/Desktop/jump")
while True:
    os.system("adb shell screencap /sdcard/screen.png")
    dirPath = "/Users/Wen/Desktop/jump/" + str(i)
    imagePath = dirPath + "/n.png"
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    os.system("adb pull /sdcard/screen.png "+imagePath)
    t = startjump(imagePath)
    os.system("adb shell input touchscreen swipe 170 187 170 187 "+str(t))
    time.sleep(2)
    i += 1
