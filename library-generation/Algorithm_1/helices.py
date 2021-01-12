import os
dir_name = os.getcwd()
os.makedirs(os.path.dirname(dir_name+'/helices-new/'), exist_ok=True)
dir_name += "/helices-new/"
with open('mylist-old','r') as newfile:
	lines=newfile.readlines()	    
	for filename in lines:
		try:
		    helix_startstop_list=[]
		    with open('PDB/'+filename.strip()) as f:
		        for line in f:
		            if line[0:5]=='HELIX':
		                helix_startstop_list.append((line.split()[5],line.split()[8],line.split()[4]))
		    for x in helix_startstop_list:
		        with open('PDB/'+filename.strip()) as f:
		            for line in f:
		                if line[0:4]=='ATOM':
		                	if len(line.split())==11:
		                		if ( int(line.split()[4])>=int(x[0]) and int(line.split()[4])<=int(x[1]) and line.split()[3]==x[2]):
		                			with open(dir_name + filename.strip()[0:4]+'_'+line.split()[3]+'_'+ x[0] ,'a+') as myfile:
		                				myfile.write(line)
		                				
		                	elif len(line.split())==12:
		                		if ( int(line.split()[5])>=int(x[0]) and int(line.split()[5])<=int(x[1]) and line.split()[4]==x[2]):
		                			with open(dir_name + filename.strip()[0:4]+'_'+line.split()[4]+'_'+ x[0] ,'a+') as myfile:
		                				myfile.write(line)
    
		except :
			pass
