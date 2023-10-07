import cv2


def show(*images, names=()):
    if not isinstance(names, list):
        names = [names]

    for i, image in enumerate(images):
        name = str(names[i]) if i < len(names) else str(i) + ' image ' + str(image.shape)
        cv2.imshow(name, image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
