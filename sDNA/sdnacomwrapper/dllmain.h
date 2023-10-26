// dllmain.h : Declaration of module class.

class CsdnacomwrapperModule : public CAtlDllModuleT< CsdnacomwrapperModule >
{
public :
	DECLARE_LIBID(LIBID_sdnacomwrapperLib)
	DECLARE_REGISTRY_APPID_RESOURCEID(IDR_SDNACOMWRAPPER, "{C34461CD-AA35-44B4-B6DF-5416C2A77B1D}")
};

extern class CsdnacomwrapperModule _AtlModule;
