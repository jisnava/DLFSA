#include<string>
#include<fstream>
#include<iostream>
#include<algorithm>
#include<vector>
#include<thread>
#include<mutex>
#include<condition_variable>
#include<queue>
#include<functional>
#include<chrono>
#include<pthread.h>
using namespace std;
int frag_size=5;
void process(string);

//--------------------------------------------------------------------------My threads
class ThreadPool
{
    public:

    ThreadPool (int threads) : shutdown_ (false)
    {
        // Create the specified number of threads
        threads_.reserve (threads);
        for (int i = 0; i < threads; ++i)
            threads_.emplace_back (std::bind (&ThreadPool::threadEntry, this, i));
    }

    ~ThreadPool ()
    {
        {
            // Unblock any threads and tell them to stop
            std::unique_lock <std::mutex> l (lock_);

            shutdown_ = true;
            condVar_.notify_all();
        }

        // Wait for all threads to stop
        // std::cerr << "Joining threads" << std::endl;
        for (auto& thread : threads_)
            thread.join();
    }

    void doJob (std::function <void (void)> func)
    {
        // Place a job on the queu and unblock a thread
        std::unique_lock <std::mutex> l (lock_);

        jobs_.emplace (std::move (func));
        condVar_.notify_one();
    }

    protected:

    void threadEntry (int i)
    {
        std::function <void (void)> job;

        while (1)
        {
            {
                std::unique_lock <std::mutex> l (lock_);

                while (! shutdown_ && jobs_.empty())
                    condVar_.wait (l);

                if (jobs_.empty ())
                {
                    // No jobs to do and we are shutting down
                    // std::cerr << "Thread " << i << " terminates" << std::endl;
                    return;
                 }

                // std::cerr << "Thread " << i << " does a job" << std::endl;
                job = std::move (jobs_.front ());
                jobs_.pop();
            }

            // Do the job without holding any locks
            job ();
        }

    }

    std::mutex lock_;
    std::condition_variable condVar_;
    bool shutdown_;
    std::queue <std::function <void (void)>> jobs_;
    std::vector <std::thread> threads_;
};
//--------------------------------------------------------------------------Threads end



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
	ThreadPool p (100);
	// The list in which the file to be processed is present
	ifstream list ("/mnt/pspdata/.init/helices-DB-list");
	while(getline(list, filename))
	{
		//cout<<filename;
		p.doJob (std::bind (process, filename));
		// process(filename);
	}


return 0;
}

void process(string filename)
{
        ifstream myfile ("/mnt/pspdata/.init/helices-DB/"+filename);
        ifstream myfilec ("/mnt/pspdata/.init/helices-DB/"+filename); //copy of that iterator
		ifstream myfiled ("/mnt/pspdata/.init/helices-DB/"+filename);

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
		if((i+frag_size)<arr_ca.size())
		{
			ofstream outfile ("/mnt/pspdata/.init/profile/helices-DB-threads-100/"+to_string(frag_size)+"_"+to_string(i+1)+"_"+filename);
			int start=arr_ca[i]-1;
			int end=arr_ca[i+frag_size]-2;
			for(int j=start;j<=end;j++)
			{
				for(int k=(j*ls); k<(j*ls)+ls; k++)
				{      
					outfile << whole_file[k];
				}
			}
			outfile.close();
		}
		// if equal to the arr_ca.size() then we will do it differently
		else if((i+frag_size)==arr_ca.size())
		{
			
			ofstream outfile ("/mnt/pspdata/.init/profile/helices-DB-threads-100/"+to_string(frag_size)+"_"+to_string(i+1)+"_"+filename);
			int start=arr_ca[i]-1;
			int end=lc-1;
			for(int j=start;j<=end;j++)
			{
				for(int k=(j*ls); k<(j*ls)+ls; k++)
				{      
					outfile << whole_file[k];
				}
			}
			outfile.close();
		}
	}
}
