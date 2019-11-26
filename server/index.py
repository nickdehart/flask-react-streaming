from flask import Flask, Response
import cv2
import threading
app = Flask(__name__)

# initialize a lock used to ensure thread-safe
# exchanges of the frames (useful for multiple browsers/tabs
# are viewing tthe stream)
lock = threading.Lock()

@app.route('/stream',methods = ['GET'])
def stream():
   return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

def generate():
   # grab global references to the lock variable
   global lock
   # initialize the video stream
   vc = cv2.VideoCapture(0)
   
   # check camera is open
   if vc.isOpened():
      rval, frame = vc.read()
   else:
      rval = False

   # while streaming
   while rval:
      # wait until the lock is acquired
      with lock:
         # read next frame
         rval, frame = vc.read()
         # if blank frame
         if frame is None:
            continue

         # encode the frame in JPEG format
         (flag, encodedImage) = cv2.imencode(".jpg", frame)

         # ensure the frame was successfully encoded
         if not flag:
            continue

      # yield the output frame in the byte format
      yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
   # release the camera
   vc.release()

if __name__ == '__main__':
   host = "127.0.0.1"
   port = 8000
   debug = False
   options = None
   app.run(host, port, debug, options)