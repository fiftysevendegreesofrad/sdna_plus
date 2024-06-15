#include "stdafx.h"
#include "calculation.h"
#include "prepareoperations.h"

Calculation* sDNACalculationFactory(char *name_cstr, const char *config, Net *net,
									  int (__cdecl *set_progressor_callback)(float),
									  int (__cdecl *print_warning_callback)(const char*),
									  vector<boost::shared_ptr<Table<float>>>* tables1d)
{
	string name(name_cstr);
	to_lower(name);
	if (name=="sdnaintegral")
		return new SDNAIntegralCalculation(net,config,
											set_progressor_callback, print_warning_callback, tables1d); 
	else if (name=="sdnaprepare")
	{
		assert(tables1d->size()==0);
		delete tables1d;
		return new PrepareOperation(net,config,
											print_warning_callback); 
	}
	else
		throw BadConfigException("Unknown calculation type: "+string(name));
}