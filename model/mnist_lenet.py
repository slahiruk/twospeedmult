#! /usr/bin/env python

import numpy as np
import tensorflow as tf
import tools.bit_opt as bt
import tools.fxd as fxd
from tensorflow.examples.tutorials.mnist import input_data
import pickle

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

n_weights = {
    'w_conv1': tf.Variable(tf.truncated_normal([5,5,1,32], stddev=0.1), name="w_conv1"),
    'w_conv2': tf.Variable(tf.truncated_normal([5,5,32,64], stddev=0.1), name="w_conv2"),
    #'w_fc1': tf.Variable(tf.truncated_normal([7*7*64,1024], stddev=0.1), name="w_fc1"),
    'w_fc1': tf.Variable(tf.truncated_normal([784,1024], stddev=0.1), name="w_fc1"),
    'w_fc2': tf.Variable(tf.truncated_normal([1024,10], stddev=0.1), name="w_fc2"),
}

n_biases = {
    'b_conv1': tf.Variable(tf.constant(0.1, shape=[32]), name="b_conv1"),
    'b_conv2': tf.Variable(tf.constant(0.1, shape=[64]), name="b_conv2"),
    'b_fc1': tf.Variable(tf.constant(0.1, shape=[1024]), name="b_fc1"),
    'b_fc2': tf.Variable(tf.constant(0.1, shape=[10]), name="b_fc2")
}


# Model
reg_beta = 0.0

# Input Vectors
x = tf.placeholder(tf.float32, [None, 784])

# Expected Labels
y_ = tf.placeholder(tf.float32, [None, 10])

# Input Reshape
x_image = tf.reshape(x, [-1, 28, 28, 1])

# Conv Layer 1
#h_conv1 = tf.nn.relu(conv2d(x_image, n_weights["w_conv1"]) + n_biases["b_conv1"])
#h_pool1 = max_pool_2x2(h_conv1)

# Conv Layer 2
#h_conv2 = tf.nn.relu(conv2d(h_pool1, n_weights["w_conv2"]) + n_biases["b_conv2"])
#h_pool2 = max_pool_2x2(h_conv2)

# FC 1 Layer
#h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
h_fc1 = tf.nn.relu(tf.matmul(x, n_weights["w_fc1"]) + n_biases["b_fc1"])

# Dropout Layer
keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

# FC 2 Layer
y_conv = tf.matmul(h_fc1_drop, n_weights["w_fc2"]) + n_biases["b_fc2"]

# Cross Entropy
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))

# L2 Reg for each Layer
reg = 0
for layer in n_weights:
    reg += tf.nn.l2_loss(n_weights[layer])

loss = tf.add(cross_entropy, tf.multiply(reg_beta,reg))

# Measurements
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# Load the data
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

with tf.Session() as sess:
    # First Train the Network
    # Training Step
    trainer = tf.train.AdamOptimizer(1e-4)
    train_step = trainer.minimize(loss)

    sess.run(tf.global_variables_initializer())

    for i in range(10000):
        batch = mnist.train.next_batch(100)
        if i % 100 == 0:
            p_train_val = sess.run([cross_entropy, accuracy], feed_dict={x: batch[0], y_:batch[1], keep_prob: 1.0})
            print('step %d, loss: %.4f, acc: %.2f' % (i, p_train_val[0], p_train_val[1]))
        train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

    # First do fp32 as a baseline
    p_test_accuracy_fp = accuracy.eval(feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0})
    print('Base: %.6f' % p_test_accuracy_fp)
    
    weights_store = []
    for w in n_weights:
        weights_store.append(n_weights[w].eval())

    file_object = open("lenet.p", 'wb')
    pickle.dump(weights_store, file_object)

