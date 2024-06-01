#include "calculation.h"

class to_union_visitor
    : public boost::static_visitor<SDNAOutputUnion>
{
public:
    SDNAOutputUnion operator()(long const& l) const
    {
		SDNAOutputUnion v;
        v.l=l;
		return v;
    }
	SDNAOutputUnion operator()(float const& f) const
    {
		SDNAOutputUnion v;
        v.f=f;
		return v;
    }
    SDNAOutputUnion operator()(HeapString const& str) const
    {
        SDNAOutputUnion v;
        v.s=str.c_str();
		return v;
    }
};

SDNAOutputUnion variant_to_union(SDNAVariant const &v)
{
	return apply_visitor (to_union_visitor(), v);
}

const char* outfieldtype_to_pythontype(OutputFieldType t)
{
	switch (t)
	{
	case fLONG:
		return "INT";
	case fFLOAT:
		return "FLOAT";
	case fSTRING:
		return "STR";
	}
	assert(false);
	return "";
};

sDNAGeometryCollectionIterator::sDNAGeometryCollectionIterator (sDNAGeometryCollection *gc) 
	: it(gc->items.begin()), gc(gc) 
{
	databuffer.swap(vector<SDNAOutputUnion>(gc->m_datanames.size(),SDNAOutputUnion(0.f)));
}

int sDNAGeometryCollectionIterator::next(long *num_parts,SDNAOutputUnion **data)
{
	if (it!=gc->items.end())
	{
		*num_parts = numeric_cast<long>((*it)->get_num_parts());
		const vector<SDNAVariant>& d = (*it)->get_data();
		assert(d.size()==gc->m_datanames.size());

		size_t index=0;
		BOOST_FOREACH( SDNAVariant const &v , d )
			databuffer[index++] = variant_to_union(v);
		
		if (d.size())
			*data = &databuffer[0];

		it_for_getpart = it;
		++it; 
		return 1;
	}
	else
		return 0;
}

SDNAPolylineDataSourceGeometryCollectionIteratorWrapper::SDNAPolylineDataSourceGeometryCollectionIteratorWrapper(vector<SDNAPolylineDataSource*> ds) 
		: net_it(NetIterator(ds[0]->getNet())), datasources(ds), numoutputs(1)//numoutputs starts with arcid
{
	for (vector<SDNAPolylineDataSource*>::iterator it=datasources.begin();it<datasources.end();it++)
	{
		assert((*it)->getNet()==net_it.getNet()); // all data sources must derive from the same net
		numoutputs += (*it)->get_output_length();
	}
	databuffer.swap(vector<SDNAOutputUnion>(numoutputs,0.f));
	variantbuffer.swap(vector<SDNAVariant>(numoutputs,0.f));
}

size_t SDNAPolylineDataSourceGeometryCollectionWrapper::get_field_metadata(char*** names_c,char*** shortnames_c,char ***pythontypes_c)
{
	*names_c = names.get_string_array();
	*shortnames_c = shortnames.get_string_array();
	*pythontypes_c = pythontypes.get_string_array();
	assert(names.size()==shortnames.size());
	assert(names.size()==pythontypes.size());
	return names.size();
}

int SDNAPolylineDataSourceGeometryCollectionIteratorWrapper::next(long *num_parts,SDNAOutputUnion **data)
{
	float *dummy = 0; //where net data ends up
	long arcid;
	int valid = net_it.next(&arcid,&geom_length,&xs,&ys,&zs,&dummy);
	if (valid)
	{
		*num_parts=1;
		
		//first copy variants to buffer so strings aren't lost
		size_t outpos=0;
		variantbuffer[outpos++] = SDNAVariant(arcid);
		for (vector<SDNAPolylineDataSource*>::iterator datasource=datasources.begin();datasource<datasources.end();datasource++)
		{
			const vector<SDNAVariant> &outs_this_source = (*datasource)->get_outputs(arcid);
			BOOST_FOREACH(SDNAVariant const& v,outs_this_source)
				variantbuffer[outpos++]=v;
		}
		assert(outpos==numoutputs);

		//then copy variant buffer to output buffer
		outpos=0;
		BOOST_FOREACH(SDNAVariant &v,variantbuffer)
			databuffer[outpos++]=variant_to_union(v);
		assert(outpos==numoutputs);

		*data = &databuffer[0];
	}
	return valid;
}

size_t SDNAPolylineDataSourceGeometryCollectionWrapper::get_num_items() { return net->num_items();}

SDNAPolylineDataSourceGeometryCollectionWrapper::SDNAPolylineDataSourceGeometryCollectionWrapper(vector<SDNAPolylineDataSource*> ds) : datasources(ds), net(ds[0]->getNet())
{
	names.add_string("ID");
	shortnames.add_string("ID");
	pythontypes.add_string(outfieldtype_to_pythontype(fLONG));
	for (vector<SDNAPolylineDataSource*>::iterator datasource=datasources.begin();datasource<datasources.end();datasource++)
	{
		assert ((*datasource)->getNet()==net);
		BOOST_FOREACH(FieldMetaData const& fmd , (*datasource)->get_field_metadata())
		{
			names.add_string(fmd.name);
			shortnames.add_string(fmd.shortname);
			pythontypes.add_string(outfieldtype_to_pythontype(fmd.type));
		}
	}
}
