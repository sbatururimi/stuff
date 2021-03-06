# [1484615767] time[  0.31] step[      2000] speed[652222]
# [1484615767] time[  0.31] step[      4000] speed[654197]
# [1484615768] time[  0.30] step[      6000] speed[661347]
# [1484615768] time[  0.30] step[      8000] speed[662600]
#
# with_dequeu_many = False
# [1484614505] time[  0.97] step[      2000] speed[205131]
# [1484614506] time[  0.96] step[      4000] speed[208224]
# [1484614507] time[  0.96] step[      6000] speed[208984]
# [1484614508] time[  0.95] step[      8000] speed[209907]

import tensorflow as tf
import time

# try benchmarking
steps_to_validate = 2000
epoch_number = 2
thread_number = 2
batch_size = 100
use_dequeue_many = True


# don't use too high of limit, 10**9 hangs (overflows to negative in TF?)
a_queue = tf.train.range_input_producer(limit=10**3, capacity=1000, shuffle=False)
#a_queue = tf.train.string_input_producer(["hello"])


# use an op that guarantees batch_size dequeues
if use_dequeue_many:
    a_batch = a_queue.dequeue_many(n=batch_size)
    a_batch_op = a_batch.op
else:
    # otherwise just do batch_size dequeue ops
    a = a_queue.dequeue()
    a_batch = [a+i for i in range(batch_size)]
    a_batch_op = tf.group(*a_batch)

config = tf.ConfigProto(log_device_placement=False)
config.operation_timeout_in_ms=5000   # terminate on long hangs
sess = tf.InteractiveSession("", config=config)

tf.train.start_queue_runners()

step = 0
start_time = time.time()
while True:
    step+=1
    sess.run(a_batch_op)
    if step % steps_to_validate == 0:
        end_time = time.time()
        sec = (end_time - start_time)
        print("[{}] time[{:6.2f}] step[{:10d}] speed[{:6d}]".format(
            str(end_time).split(".")[0],sec, step,
            int((steps_to_validate*batch_size)/sec)
        ))
        start_time = end_time
