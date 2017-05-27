#!/usr/bin/python
import signal
import numpy as np
import picamera
import picamera.array
import datetime
import logging
from os.path import join, dirname
from watson_developer_cloud import VisualRecognitionV3


logging.basicConfig(level=logging.INFO, format="%(message)s")
#logging.basicConfig(filename='example.log',level=logging.DEBUG)
LOG = logging.getLogger("capture_motion")

def signal_term_handler(signal, frame):
  LOG.info('shutting down ...')
  # this raises SystemExit(0) which fires all "try...finally" blocks:
  sys.exit(0)

# this is useful when this program is started at boot via init.d
# or an upstart script, so it can be killed: i.e. kill some_pid:
signal.signal(signal.SIGTERM, signal_term_handler)

minimum_still_interval = 5
motion_detected = False
last_still_capture_time = datetime.datetime.now()

# The 'analyse' method gets called on every frame processed while picamera
# is recording h264 video.
# It gets an array (see: "a") of motion vectors from the GPU.
class DetectMotion(picamera.array.PiMotionAnalysis):
  def analyse(self, a):
    global minimum_still_interval, motion_detected, last_still_capture_time
    if datetime.datetime.now() > last_still_capture_time + \
        datetime.timedelta(seconds=minimum_still_interval):
      a = np.sqrt(
        np.square(a['x'].astype(np.float)) +
        np.square(a['y'].astype(np.float))
      ).clip(0, 255).astype(np.uint8)
      # experiment with the following "if" as it may be too sensitive ???
      # if there're more than 10 vectors with a magnitude greater
      # than 60, then motion was detected:
#      if (a > 10).sum() > 20:
#        print(a)
     if (a > 10).sum() > 20:
#        LOG.info('motion detected at: %s' % datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S.%f'))

    #  if (a > 10).sum() > 20:
#        LOG.info('motion detected at: %s' % datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S.%f'))
#        print(a)
        motion_detected = True

camera = picamera.PiCamera()
with DetectMotion(camera) as output:
  try:
    #camera.resolution = (1920 , 1080)
    camera.resolution = (640 ,480)
    camera.framerate= 1
    #camera.exposure_mode = 'night'
    # record video to nowhere, as we are just trying to capture images:

    camera.start_recording('/dev/null', format='h264', motion_output=output)
    filename = 'test.jpeg' #+ \
      #  datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S.%f') + '.jpg'

    while True:
      while not motion_detected:
        LOG.info('waiting for brick.')
        camera.wait_recording(1)
      #----------------------------------
      LOG.info('stop recording and capture an image...')
      camera.stop_recording()
      camera.capture(filename, format='jpeg', use_video_port=True)
      LOG.info('image captured to file: %s' % filename)
      #Find out what brick
      visual_recognition = VisualRecognitionV3('2016-05-20', api_key='api key')
      file_path = join(dirname(__file__), 'test.jpeg')
      with open(file_path, 'rb') as image_file:
          part_results = visual_recognition.classify(images_file=image_file,
                         threshold=0.0,
                         classifier_ids=[
                          'LegoPartsSorter_111555016'])

          LOG.info(part_results)
          json_str = json.dumps(part_results)
          resp = json.loads(json_str)
          LOG.info(resp)
          #Decode response
          Part_Number = resp['images'][0]['classifiers'][0]['classes'][0]['class']
          Score =resp['images'][0]['classifiers'][0]['classes'][0]['score']
          print('P/N ',Part_Number,' Score=',Score)
                    Score =resp['images'][0]['classifiers'][0]['classes'][0]['score']
          print('P/N ',Part_Number,' Score=',Score)
          print(part_results)



     #start again
      motion_detected = False

      camera.start_recording('/dev/null', format='h264', motion_output=output)
  except KeyboardInterrupt as e:
    LOG.info("\nreceived KeyboardInterrupt via Ctrl-C")
    pass
  finally:
    camera.close()
    LOG.info("\ncamera turned off!")
    LOG.info("detect motion has ended.\n")


visual_recognition = VisualRecognitionV3('2016-05-20', api_key=')api key'

cap = cv2.VideoCapture(0)
# Capture frame-by-frame
#ret, image = cap.read()
#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
#cv2.imshow('frame',gray)
    
file_path = join(dirname(__file__), 'resources/test.jpeg')
with open(file_path, 'rb') as image_file:
    
    part_results = visual_recognition.classify(images_file=image_file,
                                              threshold=0.6,
                                              classifier_ids=[
                                                  'LegoPartsSorter_111555016'])
    
    json_str = json.dumps(part_results)
    resp = json.loads(json_str)
    Part_Number = resp['images'][0]['classifiers'][0]['classes'][0]['class']
    Score =resp['images'][0]['classifiers'][0]['classes'][0]['score']
    print('P/N ',Part_Number,' Score=',Score)
    print(part_results)
    #cv2.imshow('frame',image_file)
#print(json.dumps(visual_recognition.classify(classifier_id='LegoPartsSorter_111555016'), indent=2),threhold=0.6)

  #  if cv2.waitKey(1) & 0xFF == ord('q'):
   #     break

# When everything done, release the capture
#cap.release()
#cv2.destroyAllWindows()