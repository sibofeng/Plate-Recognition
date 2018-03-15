import os
import sys

sys.path.append("..")
sys.path.append("../..")
import time
import numpy as np
import tensorflow as tf
from datetime import datetime
import plate_model
from datagenerator import ImageDataGenerator
from utils import mkdirs, deldirs


class plateNet_test(object):
    def __init__(self, image_size, num_epoch, batch_size,
                 num_digit, num_classes, test_file, checkpoint_path,
                 relu_leakiness=0, is_restore=True, device_id='2'):
        self.image_size = image_size
        self.num_epoch = num_epoch
        self.batch_size = batch_size
        self.num_digit = num_digit
        self.num_classes = num_classes
        self.display_step = 20
        self.train_file = test_file
        self.checkpoint_path = checkpoint_path
        mkdirs(self.checkpoint_path)
        self.relu_leakiness = relu_leakiness
        if is_restore:
            ckpt = tf.train.get_checkpoint_state(self.checkpoint_path)
            self.restore_checkpoint = ckpt.model_checkpoint_path
        else:
            self.restore_checkpoint = ''
        os.environ['CUDA_VISIBLE_DEVICES'] = device_id

        self.init_model()

    def init_model(self):
        self.x = tf.placeholder(tf.float32, [None, self.image_size[0], self.image_size[1], 3], name='input')
        self.y = tf.placeholder(tf.float32, [None, self.num_digit, 1, self.num_classes])
        self.model = plate_model.plate_Net(self.x, self.y, num_classes=self.num_classes)
        self.predict = self.model.network_model()
        self.accuracy = self.model.accuracy(self.predict, self.y)
        self.loss = self.model.loss(self.predict, self.y)


    def create_date(self):
        return ImageDataGenerator(self.train_file, scale_size=self.image_size, num_digit=self.num_digit,
                                  num_classes=self.num_classes)

    def test(self):
        self.saver = tf.train.Saver()

        test_generator = self.create_date()
        # Get the number of training/validation steps per epoch
        test_batches_per_epoch = np.floor(test_generator.data_size / self.batch_size).astype(np.int16)

        # Start Tensorflow session
        with tf.Session(config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=True)) as sess:
            sess.run(tf.global_variables_initializer())

            # Load the pretrained weights into the non-trainable layer
            # if restore_checkponit is '' use ariginal weights, else use checkponit
            if not self.restore_checkpoint == '':
                self.saver.restore(sess, self.restore_checkpoint)

            # Validate the model on the entire validation set
            print("{} Start test, valid num batches: {}, total num: {}".format(datetime.now(), test_batches_per_epoch, test_batches_per_epoch * self.batch_size))
            v_loss = 0.
            v_acc = 0.
            count = 0
            t1 = time.time()
            for i in range(test_batches_per_epoch):
                batch_validx, batch_validy = test_generator.next_batch(self.batch_size)
                valid_loss, valid_acc, valid_out = sess.run([self.loss, self.accuracy, self.predict],
                                                            feed_dict={self.x: batch_validx, self.y: batch_validy})

                v_loss += valid_loss
                v_acc += valid_acc
                count += 1

            v_loss /= count
            v_acc /= count
            t2 = time.time() - t1
            print("Validation loss = {:.4f}, acc = {:.4f}".format(v_loss, v_acc))
            print("Test image {:.4f}ms per image".format(t2 * 1000 / (test_batches_per_epoch * self.batch_size)))

            # Reset the file pointer of the image data generator
            test_generator.reset_pointer()


if __name__ == '__main__':
    pt = plateNet_test(image_size=(96, 33),
                        num_epoch=200,
                        batch_size=64,
                        num_digit=8,
                        num_classes=65,
                        test_file="./path/test.txt",
                        checkpoint_path="./tmp/platenet/smooth_checkpoints",
                        relu_leakiness=0,
                        is_restore=True,
                        device_id='0'
                        )

    pt.test()