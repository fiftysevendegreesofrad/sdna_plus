#include "stdafx.h"
#include "calculationbase.h"

Calculation* sDNACalculationFactory(char *name, char *config, Net *net,
									  int (__cdecl *set_progressor_callback)(float),
									  int (__cdecl *print_warning_callback)(const char*),
									  vector<shared_ptr<Table<float>>>* tables1d);