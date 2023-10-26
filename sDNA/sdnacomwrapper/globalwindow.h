#include "stdafx.h"

#include "SDNAWindow.h"

//these globals are not thread safe but are not easily avoidable:
//(see http://www.newty.de/fpt/callback.html#member)
extern CSDNAWindow *globalsdnawindow; 

int __cdecl progressor_callback(float progress) ;
int __cdecl warning_callback(const char* warning); 