import cv2
import numpy as np


def is_staff_store2(crop):

    if crop is None:
        return False

    if crop.size == 0:
        return False

    hsv = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2HSV
    )

    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(
        hsv,
        lower_red1,
        upper_red1
    )

    mask2 = cv2.inRange(
        hsv,
        lower_red2,
        upper_red2
    )

    red_mask = mask1 + mask2

    red_ratio = (
        np.count_nonzero(red_mask)
        /
        red_mask.size
    )

    return bool(red_ratio > 0.20)


def is_staff_store1(crop):

    if crop is None:
        return False

    if crop.size == 0:
        return False

    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    dark_pixels = np.sum(
        gray < 50
    )

    dark_ratio = (
        dark_pixels /
        gray.size
    )

    return bool(
        dark_ratio > 0.55
    )

def is_staff(
    crop,
    store_id
):
    
    if store_id == "STORE_002":

        return is_staff_store2(
            crop
        )

    return False