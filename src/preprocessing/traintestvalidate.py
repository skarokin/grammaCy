# split into train test validate
# train: 80%
# test: 20%
# validate: 20% of train
import random
import os

def split(data_dir):
    data = []

    for file in os.listdir(data_dir):
        data.append(file)
    
    random.shuffle(data)

    train_size = int(len(data)*0.8)
    validate_size = int(train_size*0.2)
    train_size -= validate_size

    train = data[:train_size]
    validate = data[train_size:train_size+validate_size]
    test = data[train_size+validate_size:]

    os.makedirs(data_dir + "/train", exist_ok=True)
    os.makedirs(data_dir + "/test", exist_ok=True)
    os.makedirs(data_dir + "/validate", exist_ok=True)

    for file in train:
        os.rename(data_dir+"/"+file, data_dir + "/train/" + file)
    for file in test:
        os.rename(data_dir+"/"+file, data_dir + "/test/" + file)
    for file in validate:
        os.rename(data_dir+"/"+file, data_dir + "/validate/" + file)

split(r"data/raw/gum")