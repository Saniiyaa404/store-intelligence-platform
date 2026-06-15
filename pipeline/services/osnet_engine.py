import torch
from torchreid import models
import cv2
import numpy as np


MODEL = models.build_model(
    name="osnet_x1_0",
    num_classes=1000,
    pretrained=True
)

MODEL.eval()

def preprocess_crop(crop):

    if crop is None:
        return None

    if crop.size == 0:
        return None

    crop = cv2.resize(
        crop,
        (128, 256)
    )

    crop = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2RGB
    )

    crop = crop.astype(
        np.float32
    ) / 255.0

    crop = np.transpose(
        crop,
        (2, 0, 1)
    )

    crop = torch.tensor(
        crop
    ).unsqueeze(0)

    return crop


def get_osnet_embedding(crop):

    tensor = preprocess_crop(
        crop
    )

    if tensor is None:
        return None

    with torch.no_grad():

        embedding = MODEL(
            tensor
        )

    embedding = (
        embedding
        .cpu()
        .numpy()
        .flatten()
    )

    return embedding

def cosine_similarity(
    emb1,
    emb2
):

    if emb1 is None:
        return 0

    if emb2 is None:
        return 0

    norm1 = np.linalg.norm(
        emb1
    )

    norm2 = np.linalg.norm(
        emb2
    )

    if norm1 == 0:
        return 0

    if norm2 == 0:
        return 0

    return float(

        np.dot(
            emb1,
            emb2
        )

        /

        (

            norm1
            *
            norm2

        )
    )