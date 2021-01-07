#include <string>
#include <fstream>
#include<iostream>
//#include <filesystem>
#include<algorithm>
#include<vector>
using namespace std;
int frag_size=19;
string filename = "1RSZ_A_138.pdb";

__global__ void check_prot(char* line, int len, int * ca_p_d) 
{
        char last_c='0'; //The last character seen
	char last_sc='0'; //The last second character seen
	bool found = false;
      	for(int i=((blockIdx.x)*len); i<((blockIdx.x)*len)+len; i++)
        {
                if(last_sc=='G' && last_c=='L' && line[i]=='Y')
                {
                        ca_p_d[blockIdx.x]=blockIdx.x;
			found = true;
                        break;
                }
		last_sc=last_c;
                last_c=line[i];
        }
	if(!found)
		ca_p_d[blockIdx.x]=-1;
}


int main()
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

	check_prot<<<lc,1>>>(lines_d, ls, ca_p_d);
	cudaMemcpy(ca_p, ca_p_d, lc*sizeof(int),cudaMemcpyDeviceToHost);
	myfile.close();
	
	vector<int> arr_ca;
	for(int i=0; i<lc; i++)
	{
		if(ca_p[i]!=-1)
			arr_ca.push_back(ca_p[i]);
	}	

	int mod3=0;//Is actually 4
	ofstream outfile ("GLY_"+filename);

	for(int i=0;i<arr_ca.size();i++)
	{
		if(mod3==0)
			outfile << "\n";

		for(int k=(arr_ca[i]*ls); k<(arr_ca[i]*ls)+ls; k++)
		{      
			outfile << whole_file[k];
		}
		mod3=(mod3+1)%4;
	}
	outfile.close();

return 0;
}
