from flask import Flask, Response, request, redirect, url_for
import cv2
import threading
app = Flask(__name__)

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vc = cv2.VideoCapture(0)

@app.route('/stream',methods = ['POST', 'GET'])
def stream():
   return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

def generate():
   # grab global references to the output frame and lock variables
   global lock, vc
   if vc.isOpened():
      rval, frame = vc.read()
   else:
      rval = False

   # loop over frames from the output stream
   while rval:
      # wait until the lock is acquired
      with lock:
         # check if the output frame is available, otherwise skip
         # the iteration of the loop
         rval, frame = vc.read()

         if frame is None:
            continue

         # encode the frame in JPEG format
         (flag, encodedImage) = cv2.imencode(".jpg", frame)

         # ensure the frame was successfully encoded
         if not flag:
            continue

      # yield the output frame in the byte format
      yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
   vc.release()

if __name__ == '__main__':
   host = "127.0.0.1"
   port = 8000
   debug = False
   options = None
   app.run(host, port, debug, options)