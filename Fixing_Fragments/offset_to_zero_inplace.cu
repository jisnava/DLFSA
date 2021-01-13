#include<string>
#include<fstream>
#include<iostream>
#include<vector>
#include<stdio.h>
#include<algorithm>
using namespace std;
typedef struct cord3d
{
	float x;
	float y;
	float z;
}cord3d;

void fileprop(string, int *, int *, char**);
void setcords(cord3d *, int *, string);
void write_to_file(int *, cord3d *, char*, int, int, string);

__device__ bool isspace(char c)
{
	if(c==' ' || c=='\t' || c=='\n' || c=='\v' || c=='\f' || c=='\r')
		return true;
	return false;
}

__device__ bool isupper(char c)
{
	if(c>='A' && c<='Z')
		return true;
	return false;
}

__device__ bool isdigit(char c)
{
	if(c>='0' && c<='9')
		return true;
	return false;
}

//cords is a pair of 3 numbers in the form ( x1x2, y1y2, z1z2 ) where x1 and x2 are the line offset of start and end of x coordinate 
__global__ void extract_cords(char * file, int lc, int ls, int * cords, bool line_num) 
{

	if( file[(blockIdx.x)*ls]=='A' && file[(blockIdx.x)*ls+1]=='T' && file[(blockIdx.x)*ls+2]=='O' && file[(blockIdx.x)*ls+3]=='M' )
	{	
	int state=0; //state of automata
	int cordno=-1; // the coordinate number that you are currently on		

	for(int i=((blockIdx.x)*ls)+4 ; i<((blockIdx.x)*ls)+ls ; )
        {
	// Atom to state 1, branch 1
		if(state==0 && isspace(file[i]))
		{
			int j=0;
			while(isspace(file[i]) && j<6)
			{
				i++;
				j++;
			}
			state=1;
			continue;
		}
	// Atom to state 2, branch 2; state 1 to state 2 branch 2;
		else if((state==0 || state==1) && isdigit(file[i]))
		{
			if(state==0)
				printf("No space found after ATOM on line %d \n", blockIdx.x);
			int j=0;
			while(isdigit(file[i]) && j<7)
			{
				i++;
				j++;
			}
			state=2;
		}
	// Atom to dead state , branch 3
		else if(state==0 && (!isspace(file[i]) && !isupper(file[i])))
		{
			printf("3rd Branch of state 0 with block id as %d\n",blockIdx.x);
			break;	
		}
	// State 1 to dead state, branch 1; state 10 to dead state, branch 1
		else if((state==1 || state==10) && !isdigit(file[i]))
		{
			printf("1st Branch from state 1 or 10\n");
			break;
		}
	// State 2 to 3 branch 2
		else if(state==2 && isspace(file[i]))
		{
			int j=0;
			while(isspace(file[i]) && j<9)
			{
				i++;
				j++;
			}
			state=3;
		}
	// State 2 to dead state, branch 1; state 5 to dead state branch 1
		else if((state==2 || state==5) && isdigit(file[i]))
		{
			if(state==2)
			printf("State 2 to dead state, branch 1 standing at %c\n",file[i]);
			else
			printf("State 5 to dead state, branch 1\n");
			break;
		}
	// State 2 to state 4, branch 3; state 3 to state 4 branch 2
		else if((state==2 || state==3 ) && isupper(file[i]))
		{
			if(state==2)
				printf("No space found after,State 2 to state 4, branch 3\n");
			int j=0;
			while( isupper(file[i]) && j<4 )
			{
				i++;
				j++;
			}
			state=4;
		}
	// State 3 to dead state, branch 1 ; State 6 to dead state, branch 1; state 8 to dead state, branch 1
		else if((state==3 || state==6) && !isupper(file[i]))
		{
			printf("State 3 or 6 or 8 to dead state, branch 1\n");
			break;
		}
	// State 4 to 5, branch 2
		else if(state==4 && isdigit(file[i]))
		{
			i++;
			state=5;
		}
	// State 4 to 6, branch 1; state 5 to 6 branch 2
		else if((state==4 || state==5) && isspace(file[i]))
		{
			int j=0;
			while(isspace(file[i]) && j<6)
			{
				i++;
				j++;
			}
			state=6;
		}
	// State 4 to 7, branch 3; State 5 to 7 branch 3; state 6 to 7 branch 2
		else if((state==4 || state==5 || state==6) && isupper(file[i]))
		{
			if(state==4 || state ==5)
				printf("State 4 or 5 to 7, branch 3\n ");
			int j=0;
			while(isupper(file[i]) && j<3)
			{
				i++;
				j++;
			}
			state=7;
		}
	// State 7 to 8, branch 2
		else if(state==7 && isspace(file[i]))
		{
			i++;
			state=8;
		}
	// State 7 to dead state; state 9 to dead state; state 11 to dead state
		else if( (state==7 || state==9 || state==11) && !isspace(file[i]))
		{
			printf("State 7 or 9 or 11 to dead state\n");
			break;
		}
	// State 8 to 9
		else if( state==8 && isupper(file[i]))
		{
			i++;
			state=9;
		}
	// State 9 to 10
		else if( state==9 && isspace(file[i]))
		{
			int j=0;
			while(isspace(file[i]) && j<4)
			{
				j++;
				i++;
			}
			state=10;
		}
	// State 10 to 11
		else if( state==10 && isdigit(file[i]))
		{
			int j=0;
			while(isdigit(file[i]) && j<8)
			{
				j++;
				i++;
			}
			state=11;
		}
	// State 11 to 12
		else if( state==11 && isspace(file[i]))
		{
			int j=0;
			while(isspace(file[i]) && j<19)
			{
				j++;
				i++;	
			}
			state=12;
		}

	// From this pint onwards we are storing the value of the coordinates
		else if( state==12 && ( file[i]=='-' || isdigit(file[i]) ) && cordno < 2)
		{
			cordno++;
			cords[(blockIdx.x)*6 + cordno*2]=(i-(blockIdx.x)*ls);
			int j=0;
			i++;
			while((isdigit(file[i]) || file[i]=='.') && j<19)
			{
				j++;
				i++;
			}
			cords[(blockIdx.x)*6+1 + cordno*2]=(i-(blockIdx.x)*ls-1);
		}

		else if( state==12 && isspace(file[i]) && cordno < 3)
		{
			int j=0;
			while(isspace(file[i]) && j<10)
			{
				j++;
				i++;
			}
		}

		else
			break;
	}

	}

}
int main(int arg_count, char** arg_vector) // Arguments : filename 
{
	int ls;
	int lc;
	char *file; 
	
	if(arg_count==2)
		fileprop(arg_vector[1], &ls, &lc, &file);  //Initializes the file in file, have a more thoughtful name
	else
	{	cout<<"arguments wrong, exiting\n";
		exit(0);
	}

	int cords[2*3*lc]; 
	bool line_num[lc]; // Line numbers which have corrdinates, [clean up, didn't use]
	cord3d mycords[lc]; // 3dcords is a structure

	int * cords_d;
	char * file_d;
	bool * line_num_d;

	cudaMalloc((void**)&cords_d, 2*3*lc * sizeof(int)); 
	cudaMalloc((void**)&file_d, (lc*ls+lc)*sizeof(char));
	cudaMalloc((void**)&line_num_d, (lc)*sizeof(bool));

	cudaMemcpy(file_d, file, (lc*ls+lc)*sizeof(char), cudaMemcpyHostToDevice);

	extract_cords<<<lc,1>>>(file_d, lc, ls, cords_d, line_num_d);
	cudaMemcpy(cords, cords_d, 2*3*lc * sizeof(int), cudaMemcpyDeviceToHost);
	cudaMemcpy(line_num, line_num_d, lc * sizeof(bool), cudaMemcpyDeviceToHost);

	setcords( mycords, cords, arg_vector[1] ); // arg_vector[1] is the file name, may be make a separate variable for it

// Set the coordinates to offset it to zero, taking first one as the starting point
	float x = mycords[0].x;
	float y = mycords[0].y;
	float z = mycords[0].z;

	for(int i=0;i<lc;i++)
	{
		mycords[i].x = mycords[i].x - x;
		mycords[i].y = mycords[i].y - y;
		mycords[i].z = mycords[i].z - z;
	}

// Write it out to the file
	write_to_file(cords, mycords, file, lc, ls, arg_vector[1]); // cords in the pair of two values of positions

return 0;
}

void write_to_file(int * cords, cord3d * mycords, char * file, int lc, int ls, string filename)
{
	for(int i =0; i<lc; i++)
	{
		for(int f=0;f<3;f++)
		{
		float myucords;
		int g_i;
		if(f==0)
		{
		myucords=mycords[i].x; // my universal coords
		g_i=0; // global iterator for coords, i.e 0,2,4
		}
		else if(f==1)
		{
		myucords=mycords[i].y; // the universal coords
		g_i=2; // global iterator for coords, i.e 0,2,4
		}
		else
		{
		myucords=mycords[i].z; // the universal coords
		g_i=4; // global iterator for coords, i.e 0,2,4
		}
		
		if(file[i*ls + cords[6*i+g_i]]=='-')
		{
			if(myucords<0)
			{
				string val = to_string(myucords);
				char temp[10];
				int i_temp=0; //iterator for temp
				int i_dot=-1; //position of dot, set only if you have to work on it
				int len = val.length();
				temp[i_temp++]='-';
				int s_dot1=0; // saw dot in the first number? ( already present number )
				int s_dot2=0; // saw dot in the second number? ( number to be placed )
				for(int j=1,k=1; j<= cords[6*i+g_i+1]-cords[6*i+g_i] ; )
				{
					if(val[k]=='.') s_dot2=1;
				
					if(file[i*ls + cords[6*i+g_i]+j]=='.') 
					{
						s_dot1=1;
						if(j!=k)
							i_dot=j;
					}

					if( s_dot1 && !s_dot2 )
					{
						i_dot=j;
						temp[i_temp++]=val[k];
						k++;
						continue;
					}

					else if( s_dot2 && !s_dot1 )
					{
						for(int h=i_temp-1;h>=0;h--)
						{
							temp[h+1]=temp[h];
						}
						temp[0]=' ';
						i_temp++;
						j++;
					}
					else
					{
						if(k>=len)
						{
							file[i*ls + cords[6*i+g_i]+j]=' ';
							continue;
						}
	
						file[i*ls + cords[6*i+g_i]+j]=val[k];
						// Adding chars to the temp array if you have not encountered dot
						if(i_dot<0)
						{
							temp[i_temp++]=val[k];
						}
						// Done adding
						k++;
						j++;
					}
				}
				i_temp--;
				if(i_dot>0)
				{
					for(int j=i_dot-1;i_temp>=0;j--,i_temp--)
					{
						file[i*ls + cords[6*i+g_i]+j]=temp[i_temp];
					}
				}
			}
			else
			{
				string val = to_string(myucords);
				char temp[10];
				int i_temp=0; //iterator for temp
				int i_dot=-1; //position of dot, set only if you have to work on it
				int len = val.length();
				temp[i_temp++]=' ';
				file[i*ls + cords[6*i+g_i]]=' ';
				int s_dot1=0; // saw dot in the first number? ( already present number )
				int s_dot2=0; // saw dot in the second number? ( number to be placed )
				for(int j=1,k=0; j<= cords[6*i+1+g_i]-cords[6*i+g_i] ; )
				{
					if(val[k]=='.') s_dot2=1;
				
					if(file[i*ls + cords[6*i+g_i]+j]=='.') 
					{
						s_dot1=1;
						if((j-1)!=k)
							i_dot=j;
					}

					if( s_dot1 && !s_dot2 )
					{
						i_dot=j;
						temp[i_temp++]=val[k];
						k++;
						continue;
					}

					else if( s_dot2 && !s_dot1 )
					{
						for(int h=i_temp-1;h>=0;h--)
						{
							temp[h+1]=temp[h];
						}
						temp[0]=' ';
						i_temp++;
						j++;
					}
					else
					{
						if(k>=len)
						{
							file[i*ls + cords[6*i+g_i]+j]=' ';
							continue;
						}
	
						file[i*ls + cords[6*i+g_i]+j]=val[k];
						// Adding chars to the temp array if you have not encountered dot
						if(i_dot<0)
						{
							temp[i_temp++]=val[k];
						}
						// Done adding
						k++;
						j++;
					}
				}
				i_temp--;
				if(i_dot>0)
				{
					for(int j=i_dot-1;i_temp>=0;j--,i_temp--)
					{
						file[i*ls + cords[6*i+g_i]+j]=temp[i_temp];
					}
				}
			}
		}
		else
		{
			if(myucords<0)
			{
				string val = to_string(myucords);
				char temp[10];
				int i_temp=0; //iterator for temp
				int i_dot=-1; //position of dot, set only if you have to work on it
				int len = val.length();
				temp[i_temp++]='-';
				file[i*ls + cords[6*i+g_i]-1]='-';
				int s_dot1=0; // saw dot in the first number? ( already present number )
				int s_dot2=0; // saw dot in the second number? ( number to be placed )
				for(int j=0,k=1; j<=cords[6*i+1+g_i]-cords[6*i+g_i] ; )
				{
					if(val[k]=='.') s_dot2=1;
				
					if(file[i*ls + cords[6*i+g_i]+j]=='.') 
					{
						s_dot1=1;
						if(j!=(k-1))
							i_dot=j;
					}

					if( s_dot1 && !s_dot2 )
					{
						i_dot=j;
						temp[i_temp++]=val[k];
						k++;
						continue;
					}

					else if( s_dot2 && !s_dot1 )
					{
						for(int h=i_temp-1;h>=0;h--)
						{
							temp[h+1]=temp[h];
						}
						temp[0]=' ';
						i_temp++;
						j++;
					}
					else
					{
						if(k>=len)
						{
							file[i*ls + cords[6*i+g_i]+j]=' ';
							continue;
						}
	
						file[i*ls + cords[6*i+g_i]+j]=val[k];
						// Adding chars to the temp array if you have not encountered dot
						if(i_dot<0)
						{
							temp[i_temp++]=val[k];
						}
						// Done adding
						k++;
						j++;
					}
				}
				i_temp--;
				if(i_dot>0)
				{
					for(int j=i_dot-1;i_temp>=0;j--,i_temp--)
					{
						file[i*ls + cords[6*i+g_i]+j]=temp[i_temp];
					}
				}
			}
			else
			{

				string val = to_string(myucords);
				char temp[10];
				int i_temp=0; //iterator for temp
				int i_dot=-1; //position of dot, set only if you have to work on it
				int len = val.length();

				int s_dot1=0; // saw dot in the first number? ( already present number )
				int s_dot2=0; // saw dot in the second number? ( number to be placed )

				for(int j=0,k=0; j<= cords[6*i+1+g_i]-cords[6*i+g_i] ;  )
				{

					if(val[k]=='.') s_dot2=1;
				
					if(file[i*ls + cords[6*i+g_i]+j]=='.') 
					{
						s_dot1=1;
						if(j!=k)
							i_dot=j;
					}

					if( s_dot1 && !s_dot2 )
					{
						i_dot=j;
						temp[i_temp++]=val[k];
						k++;
						continue;
					}

					else if( s_dot2 && !s_dot1 )
					{
						for(int h=i_temp-1;h>=0;h--)
						{
							temp[h+1]=temp[h];
						}
						temp[0]=' ';
						i_temp++;
						j++;
					}

					else
					{
						if(k>=len)
						{
							file[i*ls + cords[6*i+g_i]+j]=' ';
							continue;
						}

						file[i*ls + cords[6*i+g_i]+j]=val[k];
						// Adding chars to the temp array if you have not encountered dot
						if(i_dot<0)
						{
							temp[i_temp++]=val[k];
						}
						// Done adding
						k++;
						j++;
					}
				

				}
				
				i_temp--;
				if(i_dot>0)
				{
					for(int j=i_dot-1;i_temp>=0;j--,i_temp--)
					{
						file[i*ls + cords[6*i+g_i]+j]=temp[i_temp];
					}
				}
			}
		}

	}
}
	ofstream outfile ("/mnt/pspdata/.init/sample-helices-DB/processed/"+filename+"_off0");
	for(int i=0; i<lc*ls;i++)
	{
		outfile<<file[i];
	}
	

}

void setcords( cord3d *mycords, int *cords, string filename) // cords is actually the start and stop offset in line of every xyz coords
{
	ifstream myfile (filename);
	int i=0;
	string line;
	while(getline(myfile, line))
	{
		mycords[i].x = stof(line.substr(cords[6*i],cords[6*i+1]-cords[6*i]+1));
		mycords[i].y = stof(line.substr(cords[6*i+2],cords[6*i+2+1]-cords[6*i+2]+1));
		mycords[i].z = stof(line.substr(cords[6*i+4],cords[6*i+4+1]-cords[6*i+4]+1));
		i++;
	}
}

void fileprop(string filename,int * ls, int * lc, char **file)
{
	
        ifstream myfile (filename);
	*lc = count(std::istreambuf_iterator<char>(myfile),std::istreambuf_iterator<char>(),'\n'); //linecount is number of lines

	myfile.clear();
	myfile.seekg(0, std::ios::beg);
	
	string line;    
        getline (myfile,line);        //Problem - Linesize may vary as we go down the file 
        *ls = line.size()+1;

	myfile.clear();
	myfile.seekg(0, std::ios::beg);

	*file=(char *)(malloc((*lc)*(*ls)*sizeof(char)));
        int it=0;
        char c;
        while (myfile.get(c))   
        {    
                (*file)[it]=c;    
                it++;
        }
}
