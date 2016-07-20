#ifndef _vwline_wrapper_H_
#define _vwline_wrapper_H_

#include <base/GeomHelper.h>

#include <wrapper/raw_constructor.hpp>
#include <wrapper/WrapHelper.h>

#include <string>

using namespace boost::python;
using namespace std;
using namespace avg;

BOOST_PYTHON_MODULE(vwline)
{

}

AVG_PLUGIN_API PyObject* registerPlugin()
{
#if PY_MAJOR_VERSION < 3
    initvwline();
    PyObject* VWLineModule = PyImport_ImportModule("vwline");
#else
    PyObject* VWLineModule = PyInit_vwline();
#endif

    return VWLineModule;

}

#endif
