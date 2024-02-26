"""Split the kaggle dataset into train/val/test and resize images to 128x128.

The raw dataset comes into the following format:
    train/$label$/
        *****.jpg
        ...
    test/$label$/
        *****.jpg
        ...

Original images have different sizes. We resize them to 64x64 and name the dataset with its size.
Resizing to (64, 64) reduces the dataset size, and loading smaller images makes training faster.

Because we don't have a lot of images and we want that the statistics on the val set be as
representative as possible, we'll take 20% of "train_signs" as val set.
"""

import argparse
import random
import os
import numpy as np

from PIL import Image
from tqdm import tqdm

SIZE = 64

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', default='data\\RawData', help="Directory with the raw dataset")
parser.add_argument('--output_dir', default='data\\{}x{}'.format(SIZE,SIZE), help="Where to write the new data")


def resize_and_save(filename, output_dir, size=SIZE, split='train',labels = None):
    """Resize the image contained in `filename` and save it to the `output_dir`"""
    image = Image.open(filename)
    # Use bilinear interpolation instead of the default "nearest neighbor" method
    image = image.resize((size, size), Image.BILINEAR)
    # In case the image is a .png with an alpha channel, convert it to RGB
    image = image.convert("RGB")  
    if split == 'test':
        image.save(os.path.join(output_dir, filename.split('\\')[-1]))  
    else:
        label = filename.split('\\')[-2]
        label = labels.index(label)
        image.save(os.path.join(output_dir, str(label)+'_'+filename.split('\\')[-1]))


if __name__ == '__main__':
    args = parser.parse_args()

    assert os.path.isdir(args.data_dir), "Couldn't find the dataset at {}".format(args.data_dir)

    # Define the data directories
    train_data_dir = os.path.join(args.data_dir, 'train')
    test_data_dir = os.path.join(args.data_dir, 'test')

    # Get the filenames in train directory 
    labels = os.listdir(train_data_dir)
    filenames = []
    for label in labels:
        pic_path = os.path.join(train_data_dir, label)
        pic_names = [os.path.join(pic_path, f) for f in os.listdir(pic_path) if f.endswith('.png')]
        filenames.extend(pic_names)

    # Get the filenames in test directory 
    test_filenames = os.listdir(test_data_dir)
    test_filenames = [os.path.join(test_data_dir, f) for f in test_filenames if f.endswith('.png')]

    # Split the images in 'train' into 80% train and 20% val
    # Make sure to always shuffle with a fixed seed so that the split is reproducible
    random.seed(2024)
    filenames.sort()
    random.shuffle(filenames)

    split = int(0.8 * len(filenames))
    train_filenames = filenames[:split]
    val_filenames = filenames[split:]

    filenames = {'train': train_filenames,
                 'val': val_filenames,
                 'test': test_filenames}

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    else:
        print("Warning: output dir {} already exists".format(args.output_dir))

    # Preprocess train, val and test
    for split in ['train', 'val', 'test']:
        output_dir_split = os.path.join(args.output_dir, '{}'.format(split))
        if not os.path.exists(output_dir_split):
            os.mkdir(output_dir_split)
        else:
            print("Warning: dir {} already exists".format(output_dir_split))

        print("Processing {} data, saving preprocessed data to {}".format(split, output_dir_split))
        for filename in tqdm(filenames[split]):
            resize_and_save(filename, output_dir_split, size=SIZE,split=split,labels=labels)

    print("Done building dataset")
