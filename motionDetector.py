import cv2
import numpy as np
import time
from sys import argv
from datetime import datetime
FRAME_SIZE = (1280, 960)


def record():
    print("To change image source type -s <SOURCE>")
    if "-s" in argv:
        i = argv.index("-s")
        IMAGE_SOURCE = argv[argv.index("-s")+1]
        if IMAGE_SOURCE.isnumeric():
           IMAGE_SOURCE = int(IMAGE_SOURCE)
    else:
        IMAGE_SOURCE = 0
    capture = cv2.VideoCapture(IMAGE_SOURCE)
    motion_detector(capture)


def motion_detector(capture):
    dt =  datetime.now().strftime("%b-%d-%Y-%H-%M")
    out = cv2.VideoWriter('out'+dt+'.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 24, FRAME_SIZE)
    previous_frame = None
    while (capture.isOpened()):
        ret, img_rgb = capture.read()
        try:
            if img_rgb.any():
                
                resized_frame = cv2.resize(img_rgb, FRAME_SIZE, interpolation=cv2.INTER_LINEAR)
                parsed_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                parsed_frame = cv2.GaussianBlur(src=parsed_frame, ksize=(5, 5), sigmaX=0)

                if (previous_frame is None):
                    previous_frame = parsed_frame
                    continue

                diff_frame = cv2.absdiff(src1=previous_frame, src2=parsed_frame)
                previous_frame = parsed_frame

                kn = np.ones((5, 5))
                diff_frame = cv2.dilate(diff_frame, kn, 3)
                thresh_frame = cv2.threshold(
                    src=diff_frame, thresh=20, maxval=255, type=cv2.THRESH_BINARY)[1]
                contours, _ = cv2.findContours(
                    image=thresh_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
                # Comment below to stop drawing contours
                # cv2.drawContours(image=resized_frame, contours=contours, contourIdx=-5,
                #                 color=(0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
                #Uncomment 6 lines below to stop drawing rectangles
                for contour in contours:
                  if cv2.contourArea(contour) > 20:
                     (x, y, w, h) = cv2.boundingRect(contour)
                     cv2.rectangle(img=resized_frame, pt1=(x, y), pt2=(x + w+w, y + h+h), color=(0, 255, 0), thickness=1)
                if len(contours)>0:
                    cv2.imshow('Motion detector', resized_frame)
                    out.write(resized_frame)
                if (cv2.waitKey(30) == 27):
                    out.release()
                    capture.release()
                    cv2.destroyAllWindows()
                    time.sleep(1)
                    break
        except AttributeError:
            pass    

        # Cleanup

if __name__ == '__main__':
    record()
