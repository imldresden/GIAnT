
#ifndef _ScatterPlotNode_H_
#define _ScatterPlotNode_H_

#include <api.h>

#include <base/GLMHelper.h>
#include <base/UTF8String.h>
#include <graphics/Color.h>
#include <player/RasterNode.h>

#include <boost/shared_ptr.hpp>

#include <string>

namespace avg {
    class MCTexture;
    typedef boost::shared_ptr<MCTexture> MCTexturePtr;
}

class ScatterPlotNode: public avg::RasterNode
{
public:
    // libavg plugin methods
    static void registerType();

    ScatterPlotNode(const avg::ArgList& args, const std::string& sPublisherName="Node");
    virtual ~ScatterPlotNode();
    virtual void connectDisplay();
    virtual void disconnect(bool bKill);
    virtual void preRender(const avg::VertexArrayPtr&, bool, float);
    virtual void render(avg::GLContext* pContext, const glm::mat4& transform);

    // node external methods
    void setPosns(const std::vector<glm::vec2>& posns);

private:
    avg::BitmapPtr createPlotBmp();
    glm::vec2 posToBmpPixel(const glm::vec2& pos);

    avg::MCTexturePtr m_pTex;
    avg::Color m_Color;

    glm::vec2 m_ViewportRangeMin;
    glm::vec2 m_ViewportRangeMax;
    glm::vec2 m_ViewportExtent;
    std::vector<glm::vec2> m_Posns;

    bool m_bDataChanged;
};

#endif
