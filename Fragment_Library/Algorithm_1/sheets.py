import os
dir_name = os.getcwd()
os.makedirs(os.path.dirname(dir_name+'/sheet-DB/'), exist_ok=True)
dir_name += "/sheet-DB/"
for filename in os.listdir('PDB-DB'):    
	try:
	    helix_startstop_list=[]
	    with open('PDB-DB/'+filename) as f:
	        for line in f:
	            if line[0:5]=='SHEET':
	                helix_startstop_list.append((line.split()[6],line.split()[9],line.split()[5]))
	            if line[0:4]=='ATOM':
	                break 
	    for x in helix_startstop_list:
	        with open('PDB-DB/'+filename) as f:
	            for line in f:
	                if line[0:4]=='ATOM':
	                	if len(line.split())==11:
	                		if ( int(line.split()[4])>=int(x[0]) and int(line.split()[4])<=int(x[1]) and line.split()[3]==x[2]):
	                			with open(dir_name + filename[0:4]+'_'+line.split()[3]+'_'+ x[0] ,'a+') as myfile:
	                				myfile.write(line)
	                				
	                	elif len(line.split())==12:
	                		if ( int(line.split()[5])>=int(x[0]) and int(line.split()[5])<=int(x[1]) and line.split()[4]==x[2]):
	                			with open(dir_name + filename[0:4]+'_'+line.split()[4]+'_'+ x[0] ,'a+') as myfile:
	                				myfile.write(line)
    
	except :
		pass
