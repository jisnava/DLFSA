import glob
import json
import os
import re
import shutil

import numpy as np
import tensorflow as tf
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render

helixCord=[]
sheetCord=[]
coilCord=[]

patt=re.compile('(ATOM)\s+([0-9]+)\s+(CA)\s+([A-Z]+)\s+([A-Z]{1})\s+([0-9]+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s+', flags=re.S)

amino_acid_id={'ALA':0, 'CYS':1, 'ASP':2, 'GLU':3, 'PHE':4, 'GLY':5, 'HIS':6, 'ILE':7, 'LYS':8, 'LEU':9, 'MET':10,
              'ASN':11, 'PRO':12, 'GLN':13, 'ARG':14, 'SER':15, 'THR':16, 'VAL':17, 'TRP':18, 'TYR':19}

def get_files(path): #opens each file and extract coordinates of CA+extra 2 values and stores in temp
    arr=[]

    for file in glob.glob(path, recursive=True):
        temp=[]
        with open(file) as fi:
            try:
                for results in patt.findall(fi.read()):
                    val=results[3:9]
                    val_=list(val)
                    del val_[2]
                    del val_[1]
                    if len(val_[0])!=3: #for replacing 4word acid name with 3word
                        name=val_[0][1:]
                        val_[0]=name
                    acid_id=amino_acid_id[val_[0]]
                    val_[0]=acid_id
                    val_final=[float(x) for x in val_]
                    temp.append(val_final)
            except UnicodeDecodeError:
                os.remove(file)
                #check.append(results)
    
        arr.append(temp)    # finally append temp array which contains details of CA of a single file 
                                #into another array
   
    return arr   


def pad(arr):     # pads array with zero
    final=[]
    for val in arr:
        zeros=np.zeros((9,4))
        zeros[:val.shape[0], :val.shape[1]]=val
        final.append(zeros)
    return final


def deepfrag(gpu_use):
	print(gpu_use)
	#train_graph = tf.Graph()
	#Hyperparameters
	epochs=200
	batch_size=512
	display_step=10
	num_classes=3
	tf.reset_default_graph() #for resetting current graph
	train_graph=tf.Graph()

	def get_summary(vars_):
		tf.contrib.slim.model_analyzer.analyze_vars(vars_, print_info=True)

	def model(input_, num_classes, dropout, isTrain): #model (CNN) definition    
		layer0=tf.layers.conv2d(inputs=input_, filters=16, kernel_size=2, padding='SAME',
                                    activation=tf.nn.relu)
		layer1=tf.layers.conv2d(inputs=layer0, filters=16, kernel_size=2, padding='SAME',
                                    activation=tf.nn.relu)
		layer2=tf.layers.conv2d(inputs=layer1, filters=32, kernel_size=2, padding='SAME',
                                    activation=tf.nn.relu)
		layer2=tf.layers.max_pooling2d(layer2, strides=1, pool_size=2)
		layer3=tf.layers.conv2d(inputs=layer2, filters=64, kernel_size=2, padding='SAME',
                                    activation=tf.nn.relu)
		layer4=tf.layers.conv2d(inputs=layer3, filters=64, kernel_size=2, padding='SAME',
                                    activation=tf.nn.relu)
		layer5=tf.layers.conv2d(inputs=layer4, filters=64, kernel_size=2, padding='SAME',
                                    activation=tf.nn.relu)

		#layer4=tf.contrib.layers.max_pool2d(layer4, 2)

		fc1=tf.contrib.layers.flatten(layer5)
    
		fc1=tf.contrib.layers.fully_connected(fc1,128)
		fc1=tf.contrib.layers.dropout(fc1, keep_prob=dropout, is_training=isTrain)

		fc2=tf.contrib.layers.fully_connected(fc1,256)
		fc2=tf.contrib.layers.dropout(fc2, keep_prob=dropout, is_training=isTrain)
		fc3=tf.contrib.layers.fully_connected(fc2,512)
		fc4=tf.contrib.layers.fully_connected(fc3,1024)
		fc4=tf.contrib.layers.dropout(fc4, keep_prob=dropout, is_training=isTrain)

		#drop=tf.contrib.layers.dropout(fc2, keep_prob=dropout, is_training=True)
		#fc3=tf.contrib.layers.fully_connected(fc2,512)
		#fc4=tf.contrib.layers.fully_connected(fc3,1024)
		#drop=tf.contrib.layers.dropout(fc4, keep_prob=dropout, is_training=True)
		logits=tf.contrib.layers.fully_connected(fc2, num_outputs=num_classes, activation_fn=tf.nn.softmax)
		return logits

	with train_graph.as_default():
		x=tf.placeholder(dtype=tf.float32,shape=[None, 9, 4,1])
		y=tf.placeholder(dtype=tf.float32, shape=[None, 3])
		keep_prob=tf.placeholder(dtype=tf.float32)
		isTrain=tf.placeholder(dtype=tf.bool)
    
		logits=model(x, num_classes, keep_prob, isTrain=isTrain)
		loss=tf.losses.softmax_cross_entropy(y, logits)#mention loss function
		optm=tf.train.AdamOptimizer(learning_rate=1e-3).minimize(loss)#mention optimizer with learning rate
		correctPred=tf.equal(tf.argmax(logits,1), tf.argmax(y,1))# an array which stores 1 for each correct prediction and  # 0 for wrong prediction 
		acc=tf.reduce_mean(tf.cast(correctPred, tf.float32)) # acc calculated by taking mean of above array

		tf.summary.scalar('loss', loss)
		tf.summary.scalar('accuracy', acc)
    

		saver=tf.train.Saver()
    
		save_file='./training_logs11.ckpt'
		model_vars=tf.trainable_variables()
		get_summary(model_vars)

    
	#loads sample test cases

	testcases=get_files('5zgg_6/*')
	testcases=[np.array(i) for i in testcases]
	padded=pad(testcases)
	inputs=np.array([2.*(a - np.min(a))/np.ptp(a)-1 for a in padded])
	inputs_=np.array([arr[:, :, np.newaxis] for arr in inputs])
	with tf.Session(graph=train_graph) as sess:
		#sess.run(tf.global_variables_initializer())
		loader = tf.train.import_meta_graph('./training_logs11.ckpt.meta') #restore trained weights
		loader.restore(sess, save_file) 
		predict=[]
		predict.append(sess.run( tf.argmax(logits, 1), feed_dict={x:inputs_, keep_prob:1.0, isTrain:False}))#sample test cases are 
                                                                            #given here
	# given here
	predict=str(predict)
	print(predict[8])
	return predict[8]


def homepage(request):
    if request.method == 'GET':
        return render(request, 'homepage.html')

    if request.method == 'POST':
        gpu_use = request.POST.get('gpu_use');
        if not request.POST.get('cordinates') and not request.FILES.get('datafile'):
            return HttpResponse(
                json.dumps({"status": "0", "message": "You must enter coordinates or should input a file"}),
                content_type="application/json"
            )
        else:
            shutil.rmtree('datafiles')
            datafile = request.FILES['datafile']
            fs = FileSystemStorage()
            filename = fs.save("datafile.txt", datafile)
            uploaded_file_url = fs.url(filename)
            print(uploaded_file_url)
            predicted_value= deepfrag(gpu_use)
            if (predicted_value == 1):
                #print("Working")
                predicted_value='helix'
            
            return HttpResponse(
                json.dumps({"status": "1", "message": predicted_value}),
                content_type="application/json"
            )



