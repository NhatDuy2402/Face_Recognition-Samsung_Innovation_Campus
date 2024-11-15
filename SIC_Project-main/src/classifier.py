from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
import tensorflow as tf
import numpy as np
# import argparse
import facenet
# import sys
import math
import pickle
from sklearn.svm import SVC

MODE = "TRAIN" # "TRAIN"or "CLASSIFY"
MODEL_PATH = os.path.join(os.getcwd(), "models/20180402-114759.pb")
CLASSIFIER_FILENAME = os.path.join(os.getcwd(),"models/classifier.pkl")
DATA_DIR = os.path.join(os.getcwd(),"dataset/processed")
BATCH_SIZE = 1024
IMAGE_SIZE = 160
SEED = 666
TEST_DIR = os.path.join(os.getcwd(),"dataset/processed_test")
# Số ảnh tối thiểu trong mỗi lớp
MIN_NROF_IMAGES_PER_CLASS = 20
# Số ảnh train trong mỗi lớp
NROF_TRAIN_IMAGES_PER_CLASS = 12


def classifier(mode = MODE, data_dir=DATA_DIR, model_path=MODEL_PATH, classifier_filename=CLASSIFIER_FILENAME, use_split_dataset=False, test_data_dir=TEST_DIR, batch_size=BATCH_SIZE, image_size=IMAGE_SIZE, seed=SEED, min_nrof_images_per_class=20, nrof_train_images_per_class=NROF_TRAIN_IMAGES_PER_CLASS):  
    with tf.Graph().as_default():      
        with tf.compat.v1.Session() as sess:      
            # Read the dataset and split it into a training and test set     
            np.random.seed(seed=seed)            
            if use_split_dataset:
                dataset_tmp = facenet.get_dataset(data_dir)
                # lấy ra 2 tập train và test từ dataset gốc với số ảnh tối thiểu là min_nrof_images_per_class và số ảnh train là nrof_train_images_per_class
                train_set, test_set = split_dataset(dataset_tmp, min_nrof_images_per_class, nrof_train_images_per_class)
                # dataset = train_set
                if (mode=='TRAIN'):
                    dataset = train_set
                elif (mode=='CLASSIFY'):
                    dataset = test_set
            else:
                dataset = facenet.get_dataset(data_dir)
             
            paths, labels = facenet.get_image_paths_and_labels(dataset)
            
            print('Số lớp (nhãn): %d' % len(dataset))
            print('Số ảnh: %d' % len(paths))
            
            # Load the model
            print('Đang tải mô hình...')
            facenet.load_model(model_path)
            
            # Get input and output tensors
            images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
            
            embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
            embedding_size = embeddings.get_shape()[1]
            
            # Run forward pass to calculate embeddings
            print('Đang tính toán...')
            nrof_images = len(paths)
            nrof_batches_per_epoch = int(math.ceil(1.0*nrof_images / batch_size))
            emb_array = np.zeros((nrof_images, embedding_size))
            for i in range(nrof_batches_per_epoch):
                start_index = i*batch_size
                end_index = min((i+1)*batch_size, nrof_images)
                paths_batch = paths[start_index:end_index]
                images = facenet.load_data(paths_batch, False, False, image_size)
                feed_dict = { images_placeholder:images, phase_train_placeholder:False }
                emb_array[start_index:end_index,:] = sess.run(embeddings, feed_dict=feed_dict)            

            if (mode=='TRAIN'):
                # Train classifier
                if os.path.exists(classifier_filename):
                    # Load existing classifier
                    with open(classifier_filename, 'rb') as infile:
                        (model, class_names, old_emb_array, old_labels) = pickle.load(infile)
                    print("Loaded existing classifier from", classifier_filename)
                    emb_array = np.concatenate((old_emb_array, emb_array))
                    labels = np.concatenate((old_labels, labels))
                else:                
                    # Use SVM classifier to train the model 
                    model = SVC(kernel='linear', probability=True)                   
                    class_names = [ cls.name for cls in dataset]
                # Training classifier
                model.fit(emb_array, labels)
                # Saving classifier model
                with open(classifier_filename, 'wb') as outfile:
                    pickle.dump((model, class_names, emb_array, labels), outfile)
                print('Đã lưu mô hình phân lớp thành công! "%s"' % classifier_filename)
                
            elif (mode=='CLASSIFY'):
                # Classify images
                print('Testing classifier')
                with open(classifier_filename, 'rb') as infile:
                    (model, class_names, emb_array, labels) = pickle.load(infile)

                print('Loaded classifier model from file "%s"' % classifier_filename)

                predictions = model.predict_proba(emb_array)
                best_class_indices = np.argmax(predictions, axis=1)
                best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
                
                for i in range(len(best_class_indices)):
                    print('%4d  %s: %.3f' % (i, class_names[best_class_indices[i]], best_class_probabilities[i]))
                    
                accuracy = np.mean(np.equal(best_class_indices, labels))
                print('Accuracy: %.3f' % accuracy)
                
            
def split_dataset(dataset, min_nrof_images_per_class, nrof_train_images_per_class):
    train_set = []
    test_set = []
    for cls in dataset:
        paths = cls.image_paths
        # Remove classes with less than min_nrof_images_per_class
        if len(paths)>=min_nrof_images_per_class:
            np.random.shuffle(paths)
            train_set.append(facenet.ImageClass(cls.name, paths[:nrof_train_images_per_class]))
            test_set.append(facenet.ImageClass(cls.name, paths[nrof_train_images_per_class:]))
    return train_set, test_set

            
if __name__ == '__main__':
    classifier(mode="TRAIN")
    # classifier(mode="CLASSIFY")
