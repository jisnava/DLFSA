inatomno = 1553
inaminono = 218


inx = 13.02
iny = 70.719
inz = 92.658

#Dont touch the next thing
offx = 0.849
offy = 0.812
offz = 0.576

with open("input") as frag:
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

		myfile = open("output",'w')
		for h in newlines:
			myfile.write(h)
		myfile.close()
