import cv2


def get_histogram(crop):

    if crop.size == 0:
        return None

    hsv = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2HSV
    )

    hist = cv2.calcHist(
        [hsv],
        [0, 1],
        None,
        [16, 16],
        [0, 180, 0, 256]
    )

    cv2.normalize(
        hist,
        hist
    )

    return hist.flatten()


def appearance_similarity(
    hist1,
    hist2
):

    if hist1 is None:
        return 0

    if hist2 is None:
        return 0

    return cv2.compareHist(
        hist1.astype("float32"),
        hist2.astype("float32"),
        cv2.HISTCMP_CORREL
    )