#!/usr/bin/env python
"""P2C Tests

For Plant Detection.
"""
import os
import sys
import cv2
import json
import unittest
from PD.P2C import Pixel2coord
from PD.DB import DB


def rotate(image, angle):
    rows, cols = image.shape[:2]
    mtrx = cv2.getRotationMatrix2D((int(cols / 2), int(rows / 2)), angle, 1)
    image = cv2.warpAffine(image, mtrx, (cols, rows))
    return image


def image_file(filename, image):
    cv2.imwrite(filename, image)
    return filename


class P2CcountTest(unittest.TestCase):
    """Check calibration count"""

    def setUp(self):
        self.outfile = open('p2c_text_output_test.txt', 'w')
        sys.stdout = self.outfile
        self.db = DB()
        self.two_objects = cv2.imread('PD/p2c_test_calibration.jpg', 1)
        self.three_objects = self.two_objects.copy()
        self.one_object = self.two_objects.copy()
        self.zero_objects = self.two_objects.copy()
        cv2.circle(self.zero_objects,
                   (600, 300), int(1000),
                   (255, 255, 255), -1)
        cv2.circle(self.one_object,
                   (175, 475), int(50),
                   (255, 255, 255), -1)
        cv2.circle(self.three_objects,
                   (600, 300), int(25),
                   (0, 0, 255), -1)

    def test_zero_objects(self):
        """Detect zero objects during calibration"""
        db = DB()
        p2c = Pixel2coord(
            db, calibration_image=image_file('zero.jpg', self.zero_objects))
        exit_flag = p2c.calibration()
        self.assertEqual(db.object_count, 0)
        self.assertTrue(exit_flag)

    def test_one_object(self):
        """Detect one object during calibration"""
        db = DB()
        p2c = Pixel2coord(
            db, calibration_image=image_file('one.jpg', self.one_object))
        exit_flag = p2c.calibration()
        self.assertEqual(db.object_count, 1)
        self.assertTrue(exit_flag)

    def test_two_objects(self):
        """Detect two objects during calibration"""
        db = DB()
        p2c = Pixel2coord(
            db, calibration_image=image_file('two.jpg', self.two_objects))
        exit_flag = p2c.calibration()
        self.assertEqual(db.object_count, 2)
        self.assertFalse(exit_flag)

    def test_three_objects(self):
        """Detect three objects during calibration"""
        db = DB()
        p2c = Pixel2coord(
            db, calibration_image=image_file('three.jpg', self.three_objects))
        exit_flag = p2c.calibration()
        self.assertEqual(db.object_count, 3)
        self.assertFalse(exit_flag)

    def tearDown(self):
        self.outfile.close()
        sys.stdout = sys.__stdout__
        os.remove('p2c_text_output_test.txt')
        try:
            os.remove('zero.jpg')
            os.remove('one.jpg')
            os.remove('two.jpg')
            os.remove('three.jpg')
        except OSError:
            pass


class P2CorientationTest(unittest.TestCase):
    """Check calibration orientation"""

    def setUp(self):
        self.outfile = open('p2c_text_output_test.txt', 'w')
        sys.stdout = self.outfile

    def test_orientation(self):
        """Detect calibration objects based on image origin.

                  |  top (0)  | bottom (1) |
                    ---------   ----------
        left  (0) |    00     |     01     |
                    ---------   ----------
        right (1) |    10     |     11     |
                    ---------   ----------
        """
        orientations = [[0, 0], [0, 1], [1, 0], [1, 1]]
        expectations = [
            [{"x": 1300, "y": 800}, {"x": 300, "y": 800}],
            [{"x": 1300, "y": 200}, {"x": 300, "y": 200}],
            [{"x": 300, "y": 800}, {"x": 1300, "y": 800}],
            [{"x": 300, "y": 200}, {"x": 1300, "y": 200}]
        ]
        for orientation, expectation in zip(orientations, expectations):
            image_origin = '{} {}'.format(
                ['top', 'bottom'][orientation[1]],
                ['left', 'right'][orientation[0]])
            os.environ['PLANT_DETECTION_calibration'] = json.dumps({
                'image_bot_origin_location': orientation})
            p2c = Pixel2coord(
                DB(), calibration_image='PD/p2c_test_calibration.jpg',
                load_data_from='env_var')
            p2c.calibration()
            coordinates = p2c.determine_coordinates()
            for axis in ['x', 'y']:
                for obj in range(2):
                    self.assertAlmostEqual(
                        coordinates[obj][axis],
                        expectation[obj][axis], delta=5,
                        msg="[{}][{}]: {} != {} within 5 delta for {}"
                            " image origin".format(
                            obj, axis,
                            coordinates[obj][axis], expectation[obj][axis],
                            image_origin))

    def test_location_rotation(self):
        """Detect using different calibration object locations and rotations."""
        i = 0
        for flip in range(3):
            for angle in [-10, 10]:
                img = 'test_objects_{}.jpg'.format(i)
                i += 1
                calibration_img = cv2.imread('PD/p2c_test_calibration.jpg', 1)
                if flip > 1:
                    cv2.circle(calibration_img,
                               (465, 290), int(1000),
                               (255, 255, 255), -1)
                    cv2.circle(calibration_img,
                               (172, 290), int(25),
                               (0, 0, 255), -1)
                    cv2.circle(calibration_img,
                               (755, 290), int(25),
                               (0, 0, 255), -1)
                elif flip:
                    calibration_img = cv2.flip(calibration_img, 0)
                calibration_img = rotate(calibration_img, angle)
                cv2.imwrite(img, calibration_img)
                p2c = Pixel2coord(DB(), calibration_image=img)
                p2c.calibration()
                self.assertAlmostEqual(
                    p2c.calibration_params['total_rotation_angle'],
                    -angle, delta=1)
                self.assertAlmostEqual(
                    p2c.calibration_params['coord_scale'],
                    1.7, delta=0.1)

    def tearDown(self):
        self.outfile.close()
        sys.stdout = sys.__stdout__
        os.remove('p2c_text_output_test.txt')
        try:
            for i in range(6):
                os.remove('test_objects_{}.jpg'.format(i))
        except OSError:
            pass
