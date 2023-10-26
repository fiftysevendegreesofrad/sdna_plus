#include "stdafx.h"
#include "utils.h"

void string_array_to_bstr_safearray_variant(long arraylength,char ** in_array,VARIANT *out_variant)
{
	CComSafeArray<BSTR> out_array;
	ATLENSURE_SUCCEEDED(out_array.Create(arraylength));
	for (int i=0;i<arraylength;i++)
		ATLENSURE_SUCCEEDED(out_array.SetAt(i,CComBSTR(in_array[i])));
	CComVariant ccv(out_array.Detach());
	HRESULT hr = ccv.Detach(out_variant);
	ATLENSURE_SUCCEEDED(hr);
}

void float_array_to_double_safearray_variant(long arraylength,float *in_array,VARIANT *out_variant)
{
	CComSafeArray<double> out_array;
	out_array.Create(arraylength);
	for (int i=0;i<arraylength;i++)
		out_array.SetAt(i,in_array[i]);
	CComVariant(out_array.Detach()).Detach(out_variant);
}

void double_array_to_double_safearray_variant(long arraylength,double *in_array,VARIANT *out_variant)
{
	CComSafeArray<double> out_array;
	out_array.Create(arraylength);
	for (int i=0;i<arraylength;i++)
		out_array.SetAt(i,in_array[i]);
	CComVariant(out_array.Detach()).Detach(out_variant);
}

void long_array_to_long_safearray_variant(long arraylength,long *in_array,VARIANT *out_variant)
{
	CComSafeArray<long> out_array;
	out_array.Create(arraylength);
	for (int i=0;i<arraylength;i++)
		out_array.SetAt(i,in_array[i]);
	CComVariant(out_array.Detach()).Detach(out_variant);
}