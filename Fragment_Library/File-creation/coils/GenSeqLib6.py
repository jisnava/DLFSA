import os
prot_dict={'ALA':'A', 'ARG':'R', 'ASN':'N', 'ASP':'D', 'CYS':'C', 'GLN':'Q', 'GLU':'E', 'GLY':'G', 'HIS':'H', 'ILE':'I', 'LEU':'L', 'LYS':'K', 'MET':'M', 'PHE':'F', 'PRO':'P', 'SER':'S', 'THR':'T', 'TRP':'W', 'TYR':'Y', 'VAL':'V'}
file_errs = ''# string for storing file errors
fragfile = open("/mnt/pspdata/.init/frag-coils/sol/6fragfile", "a+")
errfile = open("/mnt/pspdata/.init/frag-coils/sol/6errfile", "a+")

for file in os.listdir('/mnt/pspdata/.init/frag-coils/6frag/'):
	try:
	    f= open('/mnt/pspdata/.init/frag-coils/6frag/'+file,"r")
	    am_num = None # Amino acid number
	    am_pre = None # Previous amino acid number
	    out_str = ''# final output string, the sequence
	    print(file+"\n")

	    for line in f:
	        y = line.split()
	        am_num = y[5]
	        if len(y[3])==3:
	            if am_num!=am_pre:
	                if y[3] in prot_dict:
	                    out_str += prot_dict[y[3]]
	                else:
	                    file_errs+=f.name
	        else:
	            file_errs+=f.name

	        am_pre=am_num
	    
	    f.close()

	    fragfile.write(out_str + " " + file + "\n")
	except:
		pass




errfile.close()
fragfile.close()
