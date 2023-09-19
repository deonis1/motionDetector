#Copyright Denis Spasyuk
#License MIT
import cv2
import numpy as np
import time
from sys import argv
from datetime import datetime
FRAME_SIZE = [1280, 960]


# cam.set(3 , 640  ) # width        
# cam.set(4 , 480  ) # height       
# cam.set(10, 120  ) # brightness     min: 0   , max: 255 , increment:1  
# cam.set(11, 50   ) # contrast       min: 0   , max: 255 , increment:1     
# cam.set(12, 70   ) # saturation     min: 0   , max: 255 , increment:1
# cam.set(13, 13   ) # hue         
# cam.set(14, 50   ) # gain           min: 0   , max: 127 , increment:1
# cam.set(15, -3   ) # exposure       min: -7  , max: -1  , increment:1
# cam.set(17, 5000 ) # white_balance  min: 4000, max: 7000, increment:1
# cam.set(28, 0    ) # focus          min: 0   , max: 255 , increment:5

def make_4k(cap):
    cap.set(3, 3840)
    cap.set(4, 2160)

def make_2k(cap):
    cap.set(3, 2048)
    cap.set(4, 1080)

def make_1080p(cap):
    cap.set(3, 1920)
    cap.set(4, 1080)

def make_720p(cap):
    cap.set(3, 1280)
    cap.set(4, 720)
    cap.set(cv2.CAP_PROP_FPS, 24)

def make_480p(cap):
    cap.set(3, 640)
    cap.set(4, 480)

def gain(cap):
    cap.set(14, 5)
    cap.set(15, 0) 

def record():
    STACKED = False
    print("To change image source type -s SOURCE")
    print("To change camera resolution type -r 4k or 2k or 1080p or 720p or 480p")
    if "-s" in argv:
        i = argv.index("-s")
        IMAGE_SOURCE = argv[argv.index("-s")+1]
        if IMAGE_SOURCE.isnumeric():
           IMAGE_SOURCE = int(IMAGE_SOURCE)
    else:
        IMAGE_SOURCE = 6

    capture = cv2.VideoCapture(IMAGE_SOURCE)
    
    if "stack" in argv:
       STACKED = True

    if "-r" in argv:
        r = argv.index("-r")
        IMAGE_RESOLUTION = argv[argv.index("-r")+1]
        if IMAGE_RESOLUTION=="4k":
             make_4k(capture)
        if IMAGE_RESOLUTION=="2k":
             make_2k(capture)
        if IMAGE_RESOLUTION=="1080p":
             make_1080p(capture)
        if IMAGE_RESOLUTION=="720p":
             make_720p(capture)
        if IMAGE_RESOLUTION=="480p":
             make_480p(capture)
    else:
        make_720p(capture)
        gain(capture)

    capture.set(cv2.CAP_PROP_FPS, 16)
    #change_res(1280, 720)
    motion_detector(STACKED, capture)

def stackImagesECC(frames):
    M = np.eye(3, 3, dtype=np.float32)
    first_image = None
    stacked_image = None

    for frame in frames:
        image = frame.astype(np.float32) / 255
        if first_image is None:
            # convert to gray scale floating point image
            first_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            stacked_image = image
        else:
            # Estimate perspective transform
            s, M = cv2.findTransformECC(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY), first_image, M, cv2.MOTION_HOMOGRAPHY)
            w, h, _ = image.shape
            # Align image to first image
            image = cv2.warpPerspective(image, M, (h, w))
            stacked_image += image

    stacked_image /= len(frames)
    stacked_image = (stacked_image*255).astype(np.uint8)
    return stacked_image

def motion_detector(STACKED, capture):
    FRAME_SIZE[0] = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    FRAME_SIZE[1] = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    dt =  datetime.now().strftime("%b-%d-%Y-%H-%M")
    out = cv2.VideoWriter('out'+dt+'.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 24, FRAME_SIZE)
    previous_frame = None
    frames = []
    while (capture.isOpened()):
        ret, img_rgb = capture.read()
        try:
            if img_rgb.any():
                cv2.imshow('Motion', img_rgb)
                resized_frame = cv2.resize(img_rgb, FRAME_SIZE, interpolation=cv2.INTER_LINEAR)
                if STACKED:
                    frames.append(resized_frame)
                    try:
                        i = argv.index("stack")
                        stacknumber = int(argv[argv.index("stack")+1])
                    except IndexError:
                        stacknumber =4
                    if len(frames)==stacknumber:
                        r_frame = stackImagesECC(frames)
                        cv2.imshow('stacked', r_frame)
                        frames =[]
               

                parsed_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                parsed_frame = cv2.GaussianBlur(src=parsed_frame, ksize=(5, 5), sigmaX=0)
                
                if (previous_frame is None):
                    previous_frame = parsed_frame
                    continue

                diff_frame = cv2.absdiff(src1=previous_frame, src2=parsed_frame)
                previous_frame = parsed_frame
                
                kn = np.ones((5, 5))
                diff_frame = cv2.dilate(diff_frame, kn, 5)
                thresh_frame = cv2.threshold(
                    src=diff_frame, thresh=30, maxval=255, type=cv2.THRESH_BINARY)[1]
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
