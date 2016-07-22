
#ifndef _VWLineNode_H_
#define _VWLineNode_H_

#include <api.h>

#include <base/GLMHelper.h>
#include <base/UTF8String.h>
#include <player/VectorNode.h>

#include <boost/shared_ptr.hpp>
#include <vector>

class VWLineNode: public avg::VectorNode
{
    public:
        static void registerType();
        
        VWLineNode(const avg::ArgList& args, const std::string& sPublisherName="Node");
        virtual ~VWLineNode();

        void setValues(const std::vector<glm::vec2>& pts,
                const std::vector<float>& widths,
                const std::vector<float>& opacities);
        
        virtual void calcVertexes(const avg::VertexDataPtr& pVertexData,
                avg::Pixel32 color);

    private:
        void appendColors(int numEntries, avg::Pixel32 color, float opacity);

        std::vector<glm::vec2> m_VertexCoords;
        std::vector<avg::Pixel32> m_Colors;
        std::vector<glm::ivec3> m_Triangles;
};

typedef boost::shared_ptr<VWLineNode> VWLineNodePtr;

#endif

