
//string class that uses only one pointer internally for space saving in variant
class HeapString
{
private:
	char *p;
	void fillstring(const char *other)
	{
		p = new char[strlen(other)+1];
		strcpy(p,other);
	}
	HeapString()
	{
		fillstring("");
	}
public:
	HeapString (const string s)
	{
		fillstring(s.c_str());
	}
	HeapString (HeapString const& other)
	{
		fillstring(other.p);
	}
	HeapString& operator=(HeapString const& other)
	{
		delete[] p;
		fillstring(other.p);
		return *this;
	}
	const char* c_str() const {return p;}
	~HeapString()
	{
		delete[] p;
	}
};
typedef variant<long,float,HeapString> SDNAVariant;

class Net;
struct FieldMetaData;

class SDNAPolylineDataSource
{
public:
	virtual size_t get_output_length()=0;
	virtual vector<FieldMetaData> get_field_metadata()=0;
	virtual vector<SDNAVariant> get_outputs(long arcid)=0;
	virtual Net* getNet()=0;
};