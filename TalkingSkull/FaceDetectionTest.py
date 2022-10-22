import numpy
import cv2
import io
import picamera

stream = io.BytesIO()

with picamera.PiCamera() as camera:
    camera.capture(stream,format='jpeg')

numparray = numpy.frombuffer(stream.getvalue(),dtype=numpy.uint8)
img = cv2.imdecode(numparray,1)
faceDetectset= cv2.CascadeClassifier('/usr/local/lib/python3.7/dist-packages/cv2/data/haarcascade_frontalface_default.xml');

#convert to gray scale
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#now we can look for faces
faces = faceDetectset.detectMultiScale(gray,1.3,5);
for (x,y,w,h) in faces:
    #draw box on original
    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,0),2)
    print("Face:", x, y, w, h,"\n")

#show the output in window
cv2.imshow("Detected",img)

while True:
    if cv2.waitKey()==ord('q'):
        break;

stream.truncate(0)
cv2.destroyAllWindows()
