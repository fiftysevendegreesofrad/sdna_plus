#include "stdafx.h"
#include "globalwindow.h"

using namespace std;

//these globals are not thread safe but are not easily avoidable:
//(see http://www.newty.de/fpt/callback.html#member)
CSDNAWindow *globalsdnawindow; 

int __cdecl progressor_callback(float progress) 
{
	stringstream ss;
	ss.precision(1);
	ss.setf ( ios::fixed );
	globalsdnawindow->set_to(progress);
	return 0;
}

int __cdecl warning_callback(const char* warning) 
{
	_bstr_t b(warning);
	globalsdnawindow->append_text(b);
	return 0;
}
