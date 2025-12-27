import cv2
img = cv2.imread("novitech.png") #reading the image
cv2.imshow('show',img) #displaying the image
cv2.imwrite('photo.jpg',img) #saving the image to different format (png to jpg)

#cv2.waitkey(10000)#wait till 10sec
#cv2.destroyAllWindows() #close the image window
