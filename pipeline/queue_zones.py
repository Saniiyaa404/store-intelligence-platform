import cv2
import numpy as np

QUEUE_ZONES = {

    "CAM5S1": {
        "QUEUE": np.array([
            [188, 390],
            [91, 555],
            [202, 556],
            [394, 290]
        ], dtype=np.int32),
        
        "STAFF": np.array([
            [656, 337],
            [895, 388],
            [829, 927],
            [564, 929]
        ], dtype=np.int32)
    },

    "CAM5S2": {
        "QUEUE": np.array([
            [469, 310],
            [643, 312],
            [665, 525],
            [499, 525]
        ], dtype=np.int32),

        "STAFF": np.array([
            [346, 851],
            [690, 839],
            [717, 9993],
            [328, 997]
        ], dtype=np.int32)
    }

}