#include "random.h"

//will have to move random number generator to stack of calculation::run_internal
//if we want to have deterministic rng
//many threads and processes can access this, only the mutex keeps it safe
boost::random::mt19937 random_number_generator;
boost::mutex random_mutex;

float randuni(float lower,float upper)
{
	boost::random::uniform_real_distribution<float> dist(lower,upper);
	boost::lock_guard<boost::mutex> lock(random_mutex);
	return dist(random_number_generator);
}

float randnorm(float mean,float sigma)
{
	boost::random::normal_distribution<float> dist(mean,sigma);
	boost::lock_guard<boost::mutex> lock(random_mutex);
	return dist(random_number_generator);
}

