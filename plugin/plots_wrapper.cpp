#include "VWLineNode.h"
#include "ScatterPlotNode.h"

#include <base/GeomHelper.h>

#include <wrapper/raw_constructor.hpp>
#include <wrapper/WrapHelper.h>

#include <string>

using namespace boost::python;
using namespace std;
using namespace avg;

char VWLineNodeName[] = "vwlinenode";
char ScatterPlotNodeName[] = "scatterplotnode";

BOOST_PYTHON_MODULE(plots)
{
    class_<VWLineNode, bases<avg::VectorNode>, boost::noncopyable>("VWLineNode", no_init)
        .def("__init__", raw_constructor(createNode<VWLineNodeName>))
        .def("setValues", &VWLineNode::setValues)
        .def("setHighlights", &VWLineNode::setHighlights)
        ;

    class_<ScatterPlotNode, bases<avg::RasterNode>, boost::noncopyable>("ScatterPlotNode", no_init)
        .def("__init__", raw_constructor(createNode<ScatterPlotNodeName>))
        .def("setPosns", &ScatterPlotNode::setPosns)
        ;
}

AVG_PLUGIN_API PyObject* registerPlugin()
{
    VWLineNode::registerType();
    ScatterPlotNode::registerType();
    initplots();
    PyObject* pyVWLineModule = PyImport_ImportModule("plots");

    return pyVWLineModule;
}
