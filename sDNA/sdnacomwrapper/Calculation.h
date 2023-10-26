// Calculation.h : Declaration of the CCalculation

#pragma once
#include "resource.h"       // main symbols

#include "sdnacomwrapper_i.h"
#include <iostream>
using namespace std;

#if defined(_WIN32_WCE) && !defined(_CE_DCOM) && !defined(_CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA)
#error "Single-threaded COM objects are not properly supported on Windows CE platform, such as the Windows Mobile platforms that do not include full DCOM support. Define _CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA to force ATL to support creating single-thread COM object's and allow use of it's single-threaded COM object implementations. The threading model in your rgs file was set to 'Free' as that is the only threading model supported in non DCOM Windows CE platforms."
#endif

// CCalculation

class ATL_NO_VTABLE CCalculation :
	public CComObjectRootEx<CComSingleThreadModel>,
	public CComCoClass<CCalculation, &CLSID_Calculation>,
	public IDispatchImpl<ICalculation, &IID_ICalculation, &LIBID_sdnacomwrapperLib, /*wMajor =*/ 1, /*wMinor =*/ 0>
{
	SDNAIntegralCalculation *calc;
	Net *net;
	float *output_buffer;
	long output_length;
public:
	CCalculation():net(NULL),calc(NULL),output_buffer(NULL),output_length(0)
	{
	}
	~CCalculation() {
		calc_destroy((Calculation*)calc);
		delete[] output_buffer;
	}

DECLARE_REGISTRY_RESOURCEID(IDR_CALCULATION)


BEGIN_COM_MAP(CCalculation)
	COM_INTERFACE_ENTRY(ICalculation)
	COM_INTERFACE_ENTRY(IDispatch)
END_COM_MAP()



	DECLARE_PROTECT_FINAL_CONSTRUCT()

	HRESULT FinalConstruct()
	{
		return S_OK;
	}

	void FinalRelease()
	{
	}

public:

	STDMETHOD(configure)(VARIANT config_bs, IUnknown* in_net,IUnknown* sdnawindow);
	STDMETHOD(run)();
	STDMETHOD(get_output_shortnames)(VARIANT* names);
	STDMETHOD(get_output_names)(VARIANT* names);
	STDMETHOD(get_all_outputs)(LONG id, VARIANT* outputs);
};

OBJECT_ENTRY_AUTO(__uuidof(Calculation), CCalculation)
