import os

import numpy as np
import zarr
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torch.utils.data import random_split
from tqdm import tqdm


def as_array(image):
    return np.asarray(image).swapaxes(2, 0)


def convert_data_set(path, data_set, batch_size=1000):
    loader = DataLoader(
        data_set, batch_size=batch_size, shuffle=False, num_workers=4)

    num_examples = len(data_set)

    os.makedirs(path, exist_ok=True)
    with zarr.LMDBStore(path) as store:
        root = zarr.group(store=store, overwrite=True)
        images_set = root.zeros(
            'images',
            shape=(num_examples, 3, 96, 96),
            chunks=(1, None, None, None),
            dtype='u1')
        labels_set = root.zeros(
            'labels', shape=(num_examples, ), chunks=(1, ), dtype='u1')
        current_iter = 0
        for images, labels in tqdm(loader):
            size = images.shape[0]
            images_set[current_iter:current_iter + size] = images
            labels_set[current_iter:current_iter + size] = labels
            current_iter += size


def main():
    data_set = ImageFolder(root='anime-faces', transform=as_array)

    val_ratio = 0.1
    val_size = int(len(data_set) * val_ratio)
    train_size = len(data_set) - val_size

    train_set, val_set = random_split(data_set, [train_size, val_size])

    confs = [
        ('data/anime_faces/train.lmdb', train_set),
        ('data/anime_faces/val.lmdb', val_set),
    ]
    for path, data_set in confs:
        convert_data_set(path, data_set)


if __name__ == '__main__':
    main()
