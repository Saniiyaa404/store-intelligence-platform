import cv2
import numpy as np


CAMERA_ZONES = {

    "CAM1S1": {

        "SKINCARE": np.array([
            [12, 325],
            [1647, 195],
            [1637, 482],
            [168, 984]
        ], dtype=np.int32),

        "FRAGRANCE": np.array([
            [1186, 719],
            [1454, 589],
            [1662, 784],
            [1459, 948]
        ], dtype=np.int32)

    },

    "CAM2S1": {

        "MAKEUP": np.array([
            [749, 254],
            [1873, 519],
            [1342, 1045],
            [716, 707]
        ], dtype=np.int32),

        "HAIRCARE": np.array([
            [519, 210],
            [736, 253],
            [692, 651],
            [497, 510]
        ], dtype=np.int32)

    },

    "CAM1S2": {

        "SKINCARE": np.array([

            [40, 70],
            [790, 70],
            [790, 760],
            [40, 760]

        ], dtype=np.int32)

    }

}

ALL_ZONES = [

    "SKINCARE",
    "FRAGRANCE",

    "MAKEUP",
    "HAIRCARE"

]



def get_zone(camera_id, x, y):

    zones = CAMERA_ZONES.get(
        camera_id,
        {}
    )

    for zone_name, polygon in zones.items():

        if cv2.pointPolygonTest(
            polygon,
            (int(x), int(y)),
            False
        ) >= 0:

            return zone_name

    return None