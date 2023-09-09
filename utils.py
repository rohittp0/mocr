import cv2


def show(*images):
    for i, image in enumerate(images):
        cv2.imshow(str(i)+' image '+str(image.shape), image)
    cv2.waitKey(0)
