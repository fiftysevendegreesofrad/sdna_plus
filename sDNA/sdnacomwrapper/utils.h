#include "comutil.h"

void string_array_to_bstr_safearray_variant(long arraylength,char ** in_array,VARIANT *out_variant);
void float_array_to_double_safearray_variant(long arraylength,float *in_array,VARIANT *out_variant);
void double_array_to_double_safearray_variant(long arraylength,double *in_array,VARIANT *out_variant);
void long_array_to_long_safearray_variant(long arraylength,long *in_array,VARIANT *out_variant);