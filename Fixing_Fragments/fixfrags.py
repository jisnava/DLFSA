import os
import random
dir_name = os.getcwd()
psi_pred_file = "psipred.ss2"
sslist = []
helix = 0
sheet = 0
coil = 0
cord = []
seq = ''
# Current values of the x,y,z coords as they move
curr_x = 0
curr_y = 0
curr_z = 0
curr_atomno = 0
curr_aminono = 0
mycalling = []


offx = 0.849
offy = 0.812
offz = 0.576

def onetothree(protlet):	# One letter to three letter mapping of amino acids and protlet is the one letter
	prot_dict={ 'A':'ALA', 'R':'ARG', 'N':'ASN', 'D':'ASP', 'C':'CYS', 'Q':'GLN', 'E':'GLU', 'G':'GLY', 'H':'HIS', 'I':'ILE', 'L':'LEU', 'K':'LYS', 'M':'MET', 'F':'PHE', 'P':'PRO', 'S':'SER', 'T':'THR', 'W':'TRP', 'Y':'TYR', 'V':'VAL'}
	if protlet in prot_dict:
		return prot_dict[protlet]
	else :
		return 'ERR'	# Return error, that is we weren't able to find the one letter


def checkval(clen, f9, f6, f5 ,f3): # Check the validity of the string
	if( clen<=2 ):
		return False
	elif( clen <5 ):
		if(f3):
			return True
		else:
			return False
	elif( clen < 6 ):
		if(f3 or f5):
			return True
		else:
			return False
	elif( clen < 9 ):
		if(f3 or f5 or f6):
			return True
		else:
			return False
	elif( clen >=9 ):
		if( f3 or f5 or f6 or f9 ):
			return True
		else:
			return False

# Check if the fragment has been used before
def checkifused(ranbag):
	answ = random.choice(ranbag)
	found = False
	with open('usedfrags',"a+") as file:
		for i in range(10):
			if(i>0 and not found):
				break
			else:
				# answ = random.choice(ranbag)
				for line in file:
					if line == answ:
						answ = random.choice(ranbag)
						found = True
						continue
				found = False
		file.write(answ)
		file.close()
	return answ

#----------------------------------------------Functions
# Fixing helices
def work(sstring, eorh, inx, iny, inz, inatomno, inaminono): # "Search string" and structure in which to look for , eorh is structure info i.e helix or sheet
	clen = len(sstring) # current length
	olen = len(sstring) # old length
	fanswer = []
	# Initial values of x y z atomno, seq no
	f9=f6=f5=f3=True

	while checkval(clen, f9, f6, f5, f3): #(f9+f6+f5+f3)
# Looking for 9 length frags
		# print("Going for " + sstring)
		if clen > 8  and f9:
			with open("/mnt/pspdata/.init/frag-"+eorh+"/sol/"+"9fragfile") as f:
				print('Searching in 9 for '+eorh+" for "+ sstring[0:9])
				ranbag = []
				ranfile=''
				for line in f:
					if line.split()[0]==sstring[0:9]:
						ranbag.append(line)
				if len(ranbag) > 0:
					ranfile	= checkifused(ranbag)	#Random file got from that function
				if len(ranfile):
					clen -= 9
					f9=f6=f5=f3=True
					with open("/mnt/pspdata/.init/frag-"+eorh+"/9frag/" + ranfile.split()[1]) as frag:
						lines = []
						for l in frag:
							if l.split()[2] in ('N','CA','C','O'):
								lines.append(l)
						x = float(lines[0].split()[6])
						y = float(lines[0].split()[7])
						z = float(lines[0].split()[8])
						atomno = int(lines[0].split()[1])
						aminno = int(lines[0].split()[5])
# Setting origin of x,y,z to zero and doing the same for atom no and seq number and adding the offset
						newlines = []
						for i in lines:
							tupleline = i.split()
							tempstr = (tupleline[0] + 
								(6-len(tupleline[0]))*" " + 
								str(int(tupleline[1]) - atomno + inatomno) + 
								(12 - (6+len(str(int(tupleline[1]) - atomno + inatomno))))*" " + 
								tupleline[2] + 
								(17-(12+len(tupleline[2])))*" " + 
								tupleline[3] + 
								(21-(17+len(tupleline[3])))*" " + 
								tupleline[4] + " " + 
								str(int(tupleline[5]) - aminno + inaminono) + 
								(30-(23+len(str(int(tupleline[5]) - aminno + inaminono))))*" " + 
								str(round((float(tupleline[6]) - x + inx + offx),3)) + 
								(38-(30+len(str(round((float(tupleline[6]) - x + inx + offx),3)))))*" " + 
								str(round((float(tupleline[7]) - y+ iny + offy),3)) + 
								(46-(38+len(str(round((float(tupleline[7]) - y + iny + offy),3)))))*" " + 
								str(round((float(tupleline[8]) - z + inz + offz),3)) + 
								(55-(46+len(str(round((float(tupleline[8]) - z + inz + offz),3)))))*" " + 
								tupleline[9] + 
								(60-(55+len(tupleline[9])) )*" " + 
								tupleline[10] + 
								(76-(60+len(tupleline[10])))*" " + 
								tupleline[11] + "\n")

							newlines.append(tempstr)
						inx = float(newlines[len(newlines)-1].split()[6])
						iny = float(newlines[len(newlines)-1].split()[7])
						inz = float(newlines[len(newlines)-1].split()[8])
						inatomno = int(newlines[len(newlines)-1].split()[1]) + 1
						inaminono = int(newlines[len(newlines)-1].split()[5]) + 1

						fanswer.extend(newlines)

						sstring = sstring[9:]

				if clen==olen:
					f9=False
				print('Done searching in 9 for '+eorh+" for "+ sstring[0:9])
#-------------------------------------------------------------------------------------------
# Looking for 6 length frags
		elif clen > 5  and f6:
			with open("/mnt/pspdata/.init/frag-"+eorh+"/sol/"+"6fragfile") as f:
				print('Searching in 6 for '+eorh+" for "+ sstring[0:6])
				ranbag = []
				ranfile=''
				for line in f:
					if line.split()[0]==sstring[0:6]:
						ranbag.append(line)
				if len(ranbag) > 0:
					ranfile	= checkifused(ranbag)	#Random file got from that function
				if len(ranfile):
					clen -= 6
					f9=f6=f5=f3=True
					with open("/mnt/pspdata/.init/frag-"+eorh+"/6frag/" + ranfile.split()[1]) as frag:
						lines = []
						for l in frag:
							if l.split()[2] in ('N','CA','C','O'):
								lines.append(l)
						x = float(lines[0].split()[6])
						y = float(lines[0].split()[7])
						z = float(lines[0].split()[8])
						atomno = int(lines[0].split()[1])
						aminno = int(lines[0].split()[5])
# Setting origin of x,y,z to zero and doing the same for atom no and seq number and adding the offset
						newlines = []
						for i in lines:
							tupleline = i.split()
							tempstr = (tupleline[0] + 
								(6-len(tupleline[0]))*" " + 
								str(int(tupleline[1]) - atomno + inatomno) + 
								(12 - (6+len(str(int(tupleline[1]) - atomno + inatomno))))*" " + 
								tupleline[2] + 
								(17-(12+len(tupleline[2])))*" " + 
								tupleline[3] + 
								(21-(17+len(tupleline[3])))*" " + 
								tupleline[4] + " " + 
								str(int(tupleline[5]) - aminno + inaminono) + 
								(30-(23+len(str(int(tupleline[5]) - aminno + inaminono))))*" " + 
								str(round((float(tupleline[6]) - x + inx + offx),3)) + 
								(38-(30+len(str(round((float(tupleline[6]) - x + inx + offx),3)))))*" " + 
								str(round((float(tupleline[7]) - y+ iny + offy),3)) + 
								(46-(38+len(str(round((float(tupleline[7]) - y + iny + offy),3)))))*" " + 
								str(round((float(tupleline[8]) - z + inz + offz),3)) + 
								(55-(46+len(str(round((float(tupleline[8]) - z + inz + offz),3)))))*" " + 
								tupleline[9] + 
								(60-(55+len(tupleline[9])) )*" " + 
								tupleline[10] + 
								(76-(60+len(tupleline[10])))*" " + 
								tupleline[11] + "\n")

							newlines.append(tempstr)
						inx = float(newlines[len(newlines)-1].split()[6])
						iny = float(newlines[len(newlines)-1].split()[7])
						inz = float(newlines[len(newlines)-1].split()[8])
						inatomno = int(newlines[len(newlines)-1].split()[1]) + 1
						inaminono = int(newlines[len(newlines)-1].split()[5]) + 1

						fanswer.extend(newlines)

						sstring = sstring[6:]

				if clen==olen:
					f6=False
				print('Done searching in 6 for '+eorh+" for "+ sstring[0:6])
#------------------------------------------------------------------------------------------
# Looking for 5 length frags
		elif clen > 4  and f5:
			with open("/mnt/pspdata/.init/frag-"+eorh+"/sol/"+"5fragfile") as f:
				print('Searching in 5 for '+eorh+" for "+ sstring[0:5])
				ranbag = []
				ranfile=''
				for line in f:
					if line.split()[0]==sstring[0:5]:
						ranbag.append(line)
				if len(ranbag) > 0:
					ranfile	= checkifused(ranbag)	#Random file got from that function
				if len(ranfile):
					clen -= 5
					f9=f6=f5=f3=True
					with open("/mnt/pspdata/.init/frag-"+eorh+"/5frag/" + ranfile.split()[1]) as frag:
						lines = []
						for l in frag:
							if l.split()[2] in ('N','CA','C','O'):
								lines.append(l)
						x = float(lines[0].split()[6])
						y = float(lines[0].split()[7])
						z = float(lines[0].split()[8])
						atomno = int(lines[0].split()[1])
						aminno = int(lines[0].split()[5])
# Setting origin of x,y,z to zero and doing the same for atom no and seq number and adding the offset
						newlines = []
						for i in lines:
							tupleline = i.split()
							tempstr = (tupleline[0] + 
								(6-len(tupleline[0]))*" " + 
								str(int(tupleline[1]) - atomno + inatomno) + 
								(12 - (6+len(str(int(tupleline[1]) - atomno + inatomno))))*" " + 
								tupleline[2] + 
								(17-(12+len(tupleline[2])))*" " + 
								tupleline[3] + 
								(21-(17+len(tupleline[3])))*" " + 
								tupleline[4] + " " + 
								str(int(tupleline[5]) - aminno + inaminono) + 
								(30-(23+len(str(int(tupleline[5]) - aminno + inaminono))))*" " + 
								str(round((float(tupleline[6]) - x + inx + offx),3)) + 
								(38-(30+len(str(round((float(tupleline[6]) - x + inx + offx),3)))))*" " + 
								str(round((float(tupleline[7]) - y+ iny + offy),3)) + 
								(46-(38+len(str(round((float(tupleline[7]) - y + iny + offy),3)))))*" " + 
								str(round((float(tupleline[8]) - z + inz + offz),3)) + 
								(55-(46+len(str(round((float(tupleline[8]) - z + inz + offz),3)))))*" " + 
								tupleline[9] + 
								(60-(55+len(tupleline[9])) )*" " + 
								tupleline[10] + 
								(76-(60+len(tupleline[10])))*" " + 
								tupleline[11] + "\n")

							newlines.append(tempstr)
						inx = float(newlines[len(newlines)-1].split()[6])
						iny = float(newlines[len(newlines)-1].split()[7])
						inz = float(newlines[len(newlines)-1].split()[8])
						inatomno = int(newlines[len(newlines)-1].split()[1]) + 1
						inaminono = int(newlines[len(newlines)-1].split()[5]) + 1

						fanswer.extend(newlines)

						sstring = sstring[5:]
						
				if clen==olen:
					f5=False
				print('Done searching in 5 for '+eorh+" for "+ sstring[0:5])
#-------------------------------------------------------------------------------------------
# Looking for 3 length frags
		elif clen > 2  and f3:
			with open("/mnt/pspdata/.init/frag-"+eorh+"/sol/"+"3fragfile") as f:
				print('Searching in 3 for '+eorh+" for "+ sstring[0:3])
				ranbag = []
				ranfile=''
				for line in f:
					if line.split()[0]==sstring[0:3]:
						ranbag.append(line)
				if len(ranbag) > 0:
					ranfile	= checkifused(ranbag)	#Random file got from that function
				if len(ranfile):
					clen -= 3
					f9=f6=f5=f3=True
					with open("/mnt/pspdata/.init/frag-"+eorh+"/3frag/"+ ranfile.split()[1]) as frag:
						lines = []
						for l in frag:
							if l.split()[2] in ('N','CA','C','O'):
								lines.append(l)
						x = float(lines[0].split()[6])
						y = float(lines[0].split()[7])
						z = float(lines[0].split()[8])
						atomno = int(lines[0].split()[1])
						aminno = int(lines[0].split()[5])
# Setting origin of x,y,z to zero and doing the same for atom no and seq number and adding the offset
						newlines = []
						for i in lines:
							tupleline = i.split()
							tempstr = (tupleline[0] + 
								(6-len(tupleline[0]))*" " + 
								str(int(tupleline[1]) - atomno + inatomno) + 
								(12 - (6+len(str(int(tupleline[1]) - atomno + inatomno))))*" " + 
								tupleline[2] + 
								(17-(12+len(tupleline[2])))*" " + 
								tupleline[3] + 
								(21-(17+len(tupleline[3])))*" " + 
								tupleline[4] + " " + 
								str(int(tupleline[5]) - aminno + inaminono) + 
								(30-(23+len(str(int(tupleline[5]) - aminno + inaminono))))*" " + 
								str(round((float(tupleline[6]) - x + inx + offx),3)) + 
								(38-(30+len(str(round((float(tupleline[6]) - x + inx + offx),3)))))*" " + 
								str(round((float(tupleline[7]) - y+ iny + offy),3)) + 
								(46-(38+len(str(round((float(tupleline[7]) - y + iny + offy),3)))))*" " + 
								str(round((float(tupleline[8]) - z + inz + offz),3)) + 
								(55-(46+len(str(round((float(tupleline[8]) - z + inz + offz),3)))))*" " + 
								tupleline[9] + 
								(60-(55+len(tupleline[9])) )*" " + 
								tupleline[10] + 
								(76-(60+len(tupleline[10])))*" " + 
								tupleline[11] + "\n")

							newlines.append(tempstr)
						inx = float(newlines[len(newlines)-1].split()[6])
						iny = float(newlines[len(newlines)-1].split()[7])
						inz = float(newlines[len(newlines)-1].split()[8])
						inatomno = int(newlines[len(newlines)-1].split()[1]) + 1
						inaminono = int(newlines[len(newlines)-1].split()[5]) + 1

						fanswer.extend(newlines)

						sstring = sstring[3:]
				if clen==olen:
					f3=False
				print('Done searching in 3 for '+eorh+" for "+ sstring[0:3])
		olen=clen
#-------------------------------------------------------------------------------------------
	if len(fanswer)==0:
		return fanswer, inx, iny, inz, inaminono, inatomno, False, sstring
	else:
		return fanswer, inx, iny, inz, inaminono, inatomno, True, sstring


def awork(sstring , curr_x, curr_y, curr_z, curr_atomno, curr_aminono):
        print(sstring)
	with open("strdprotseq.pdb") as prot:
		lines = []
		retlines = [] # lines to be returned
		for l in prot:
			lines.append(l)
		for j in sstring:
			amino3 = onetothree(j)
			newlines = []
			for i in lines:
				tupleline = i.split()
				tempstr = (tupleline[0] + 
					(6-len(tupleline[0]))*" " + 
					str(int(tupleline[1]) + curr_atomno) + 
					(12 - (6+len(str(int(tupleline[1]) + curr_atomno))))*" " + 
					tupleline[2] + 
					(17-(12+len(tupleline[2])))*" " + 
					amino3 + 
					(21-(17+len(tupleline[3])))*" " + 
					tupleline[4] + " " + 
					str(int(tupleline[5]) + curr_aminono) + 
					(30-(23+len(str(int(tupleline[5]) + curr_aminono))))*" " + 
					str(round((float(tupleline[6]) + curr_x + offx),3)) + 
					(38-(30+len(str(round((float(tupleline[6]) + curr_x + offx),3)))))*" " + 
					str(round((float(tupleline[7]) + curr_y + offy),3)) + 
					(46-(38+len(str(round((float(tupleline[7]) + curr_y + offy),3)))))*" " + 
					str(round((float(tupleline[8]) + curr_z + offz),3)) + 
					(55-(46+len(str(round((float(tupleline[8]) + curr_z + offz),3)))))*" " + 
					tupleline[9] + 
					(60-(55+len(tupleline[9])) )*" " + 
					tupleline[10] + 
					(76-(60+len(tupleline[10])))*" " + 
					tupleline[11] + "\n")
				newlines.append(tempstr)
			retlines.extend(newlines)
# Usually the last atom is O but we need C, so instead of wrt to last atom go for second last
			curr_x = float(newlines[len(newlines)-2].split()[6])
			curr_y = float(newlines[len(newlines)-2].split()[7])
			curr_z = float(newlines[len(newlines)-2].split()[8])
			curr_atomno = int(newlines[len(newlines)-1].split()[1]) + 1
			curr_aminono = int(newlines[len(newlines)-1].split()[5]) + 1
	return retlines, curr_x, curr_y, curr_z, curr_atomno, curr_aminono

#---------------------------------------------------functions close

with open(psi_pred_file) as f:
	num_lines = sum(1 for line in open(psi_pred_file))
	lastline=''
	for i, line in enumerate(f):
# Getting helix coords
		if len(line.split()) == 6:
			# Case when the next eliment is helix
			if(len(lastline.split()) == 6 and lastline.split()[2]=='H' and helix == 0 and sheet != 1 and coil!=1):
				seq += lastline.split()[1]

			if(line.split()[2]=='H' and helix == 0 and sheet != 1 and coil!=1):
				helix=1
				cord.append(i) 
				seq += line.split()[1]
			elif((line.split()[2]!='H' or i==num_lines-1 )and helix == 1 and sheet != 1 and coil!=1 ):
				if i == num_lines-1 and line.split()[2]=='H':
					seq += line.split()[1]
				helix=0
				cord.append(i-1)
				cord.append(seq)
				cord.append('H')
				sslist.append(cord)
				cord = []
				seq = ''
			elif (line.split()[2]=='H' and helix == 1 and sheet != 1 and coil!=1):
				seq += line.split()[1]
# Getting sheet coords
		if len(line.split()) == 6:
			if(len(lastline.split()) == 6 and lastline.split()[2]=='E' and sheet == 0 and helix != 1 and coil!=1):
				seq += lastline.split()[1]

			if(line.split()[2]=='E' and sheet == 0 and helix != 1 and coil!=1):
				sheet=1
				cord.append(i) 
				seq += line.split()[1]
			elif((line.split()[2]!='E' or i==num_lines) and sheet == 1 and helix != 1 and coil!=1):
				if i == num_lines-1 and line.split()[2]=='E':
					seq += line.split()[1]
				sheet=0
				cord.append(i-1)
				cord.append(seq)
				cord.append('E')
				sslist.append(cord)
				cord = []
				seq= ''
			elif (line.split()[2]=='E' and sheet == 1 and helix != 1 and coil!=1):
				seq += line.split()[1]
# Getting coils
		if len(line.split()) == 6:
			if(len(lastline.split()) == 6 and lastline.split()[2]=='C' and coil == 0 and sheet != 1 and helix!=1):
				seq += lastline.split()[1]

			if(line.split()[2]=='C' and coil == 0 and helix != 1 and sheet != 1):
				coil=1
				cord.append(i) 
				seq += line.split()[1]
			elif((line.split()[2]!='C' or i==num_lines) and coil == 1 and helix != 1 and sheet != 1):
				if i == num_lines-1 and line.split()[2]=='C':
					seq += line.split()[1]
				coil=0
				cord.append(i-1)
				cord.append(seq)
				cord.append('C')
				sslist.append(cord)
				cord = []
				seq= ''
			elif (line.split()[2]=='C' and coil == 1 and helix != 1 and sheet != 1):
				seq += line.split()[1]

		lastline=line

# Calling the work function with every secondary structure available in the psipred file
for i in sslist:
	templs = [] # temporary list
	histring = ''
	if i[3]=='C':
		templs, curr_x, curr_y, curr_z, curr_atomno, curr_aminono = awork(i[2],curr_x, curr_y, curr_z, curr_atomno, curr_aminono)	#Don't need to pass the struture info here
	else :
# histring is the string that is returned by the funtion which is the remaining string which is not modelled
		if i[3]=='E':
			templs, curr_x, curr_y, curr_z, curr_atomno, curr_aminono, found, histring = work(i[2], 'sheet',curr_x, curr_y, curr_z, curr_atomno, curr_aminono)		#Need to pass the structure 
			if not found:
				templs, curr_x, curr_y, curr_z, curr_atomno, curr_aminono = awork(i[2],curr_x, curr_y, curr_z, curr_atomno, curr_aminono)	

		else :
			templs, curr_x, curr_y, curr_z, curr_atomno, curr_aminono, found, histring = work(i[2], 'helix',curr_x, curr_y, curr_z, curr_atomno, curr_aminono)
			if not found:
				templs, curr_x, curr_y, curr_z, curr_atomno, curr_aminono = awork(i[2],curr_x, curr_y, curr_z, curr_atomno, curr_aminono)	

	mycalling.extend(templs)
	
	if len(histring)>0:
		templs, curr_x, curr_y, curr_z, curr_atomno, curr_aminono = awork(histring, curr_x, curr_y, curr_z, curr_atomno, curr_aminono)
		mycalling.extend(templs)

# Writing everything to a file
with open("myanswer.pdb","a") as myf:
	for line in mycalling:
		myf.write(line)
myf.close()
