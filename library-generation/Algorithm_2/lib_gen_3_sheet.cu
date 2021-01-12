#include<string>
#include<fstream>
#include<iostream>
#include<algorithm>
#include<vector>
using namespace std;
void process(string,string);
int frag_size=3;

__global__ void check_ca(char* line, int len, int * ca_p_d) 
{
        char last_c='0'; //The last character seen
	bool found = false;
      	for(int i=((blockIdx.x)*len); i<((blockIdx.x)*len)+len; i++)
        {
                if(last_c=='C' && line[i]=='A')
                {
                        ca_p_d[blockIdx.x]=blockIdx.x;
			found = true;
                        break;
                }
                last_c=line[i];
        }
	if(!found)
		ca_p_d[blockIdx.x]=-1;
}


int main()
{
	string filename;
	ifstream list ("/mnt/pspdata/.init/sheet-DB-list");

	double progress = 0;

	while(getline(list, filename))
	{
		//Code for showing the progress bar
		int barWidth = 100;
		cout << "[";
		int pos = barWidth * progress;
		for (int i = 0; i < barWidth; ++i) 
		{
        		if (i < pos) cout << "=";
	        	else if (i == pos) cout << ">";
		        else cout << " ";
		}
		cout << "] " << double(progress * 100.0) <<" "<<filename <<"\t %\r";
		cout.flush();

		progress += 1.0/6959.0;
		cout.flush();
		//Progress bar code ends
		process("/mnt/pspdata/.init/sheet-DB/" + filename,filename);
	}

std::cout << std::endl;
return 0;
}

void process(string filename, string succintfname)
{
        ifstream myfile (filename);
        ifstream myfilec (filename); //copy of that iterator
	ifstream myfiled (filename);

	int lc = count(std::istreambuf_iterator<char>(myfile),std::istreambuf_iterator<char>(),'\n'); //linecount ie number of lines
	
	string line;    
        getline (myfilec,line);         //linesize
        int ls = line.size()+1;
       
	char whole_file[lc*ls + lc];
        int it=0;
        char c;
        while (myfiled.get(c))          // loop getting single characters
        {    
                whole_file[it]=c;    
                it++;
        }

   
        int ca_p[lc];  // Position of ca, that is line number in which ca is present
	for(int i=0;i<lc;i++)
	{
		ca_p[i]=-1;
	}

	char* lines_d;
	int* ca_p_d;
	cudaMalloc((void**)&ca_p_d, lc * sizeof(int)); 
	cudaMalloc((void**)&lines_d, (lc*ls+lc)*sizeof(char));
	
	cudaMemcpy(lines_d, whole_file , lc*ls*sizeof(char),cudaMemcpyHostToDevice);

	check_ca<<<lc,1>>>(lines_d, ls, ca_p_d);
	cudaMemcpy(ca_p, ca_p_d, lc*sizeof(int),cudaMemcpyDeviceToHost);
	myfile.close();
	
	vector<int> arr_ca;
	for(int i=0; i<lc; i++)
	{
		if(ca_p[i]!=-1)
			arr_ca.push_back(ca_p[i]);
	}

	for(int i=0;i<arr_ca.size();i++)
	{
		if((i+frag_size)<=arr_ca.size())
		{
			ofstream outfile ("/mnt/pspdata/.init/frag-sheet/3frag/frag"+to_string(frag_size)+"_"+to_string(i+1)+"_"+succintfname);
			for(int j=i;j<i+frag_size;j++)
			{
				for(int k=(arr_ca[j]*ls); k<(arr_ca[j]*ls)+ls; k++)
				{      
					outfile << whole_file[k];
				}
			}
			outfile.close();
		}
	}
}
