import cv2, os
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'datasets'
sub_data = 'Elon'

path = os.path.join(datasets, sub_data) #datasets/kamali
if not os.path.isdir(path):
    os.mkdir(path)
(width, height) = (130, 100)


face_cascade = cv2.CascadeClassifier(haar_file) # loading haarcascade frontalface algorithm

webcam = cv2.VideoCapture(0)  #camera initialisation, 0- primary cam, 1 - secondary cam

count = 1
while count < 31: # capturing 30 images as data for training
    print(count)
    (_, im) = webcam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 4)
    for (x,y,w,h) in faces:
        cv2.rectangle(im,(x,y),(x+w,y+h),(255,0,0),2) # drawing a rectangle so that it will capture the face
        face = gray[y:y + h, x:x + w] # capturing only the face
        face_resize = cv2.resize(face, (width, height)) # resizing so that all the images are in same size
        cv2.imwrite('%s/%s.png' % (path,count), face_resize)
    count += 1

    cv2.imshow('OpenCV', im)
    key = cv2.waitKey(10)
    if key == 27: # esc key value is 27 and if pressed it will break the loop
        break
webcam.release()
cv2.destroyAllWindows()
