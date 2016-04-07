import pygame
from StringIO import StringIO
import cv2
import os
import numpy


class Image(object):

    """
    Image object
    """

    def __init__(self):
        self.display = None

    def show_image(self, image, width, height):
        """
        Show image
        """
        size = (width, height)
        self.display = pygame.display.set_mode(size, 0)
        self.snapshot = pygame.surface.Surface(size, 0, self.display)
        img = pygame.image.load(StringIO(image))
        self.display.blit(img, (0, 0))
        pygame.display.flip()

    def detect_face(self, image):
        linux_prefix = "/usr/share/opencv"
        mac_prefix = "/usr/local/share/OpenCV"
        suffix = "/haarcascades/haarcascade_frontalface_default.xml"
        linux_path = linux_prefix + suffix
        mac_path = mac_prefix + suffix
        
        if os.path.exists(linux_path) :
            cpath = linux_path
        elif os.path.exists(mac_path) :
            cpath = mac_path
        else :
            raise Exception("No Haarcascade found")
        classifier = cv2.CascadeClassifier(cpath)

        jpg = numpy.fromstring(image, numpy.int8)
        image = cv2.imdecode(jpg, 1)
        faces = classifier.detectMultiScale(image)
        if len(faces) > 0 :
            for (x,y,w,h) in faces :
                if w < 120 :
                    # Too small to be a nearby face
                    continue
                return True
        return False

    def close(self):
        """
        Close display
        """
        if not self.display is None:
            pygame.display.quit()
