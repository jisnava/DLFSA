import os
dir_name = os.getcwd()
os.makedirs(os.path.dirname(dir_name+'/coil-DB/'), exist_ok=True)
dir_name += "/coil-DB/"
for filename in os.listdir('PDB-DB'):    
	try:
		helix_startstop_list=[]
		with open('PDB-DB/'+filename) as f:
			for line in f:
				if line[0:5]=='SHEET':
					helix_startstop_list.append((line.split()[6],line.split()[9],line.split()[5]))
				if line[0:5]=='HELIX':
					helix_startstop_list.append((line.split()[5],line.split()[8],line.split()[4]))
				if line[0:4]=='ATOM':
					break
		coil_in = sorted(helix_startstop_list, key=lambda x: int(x[0]))
		coil_list = []
		coil_list.append((0,coil_in[0][0],coil_in[0][2]))

		for i in range(len(coil_in)-1):
			coil_list.append((coil_in[i][1],coil_in[i+1][0],coil_in[i][2]))

		coil_list.append((coil_in[-1][1],9999,coil_in[-1][2]))
		
		for x in coil_list:
				with open('PDB-DB/'+filename) as f:
					for line in f:
						if line[0:4]=='ATOM':
							if len(line.split())==11:
								if ( int(line.split()[4])>=int(x[0]) and int(line.split()[4])<=int(x[1]) and line.split()[3]==x[2]):
									with open(dir_name + filename[0:4]+'_'+line.split()[3]+'_'+ str(x[0]) ,'a+') as myfile:
										myfile.write(line)
			                				
							elif len(line.split())==12:
								if ( int(line.split()[5])>=int(x[0]) and int(line.split()[5])<=int(x[1]) and line.split()[4]==x[2]):
									with open(dir_name + filename[0:4]+'_'+line.split()[4]+'_'+ str(x[0]) ,'a+') as myfile:
										myfile.write(line)
	except :
		pass
