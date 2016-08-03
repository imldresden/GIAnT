#include "ScatterPlotNode.h"

#include <math.h>

#include <base/Exception.h>
#include <base/StringHelper.h>
#include <base/ScopeTimer.h>
#include <graphics/MCTexture.h>
#include <graphics/VertexArray.h>
#include <graphics/FilterFill.h>
#include <graphics/GLContextManager.h>
#include <graphics/Bitmap.h>
#include <player/Arg.h>
#include <player/TypeDefinition.h>
#include <player/TypeRegistry.h>
#include <player/OGLSurface.h>

#include <iostream>
#include <string>

using namespace boost;
using namespace std;
using namespace avg;


void ScatterPlotNode::registerType()
{
    vector<string> cm;
    TypeDefinition def = TypeDefinition("scatterplotnode", "rasternode",  ExportedObject::buildObject<ScatterPlotNode>)
        .addArg(Arg<glm::vec2>("viewportrangemin", glm::vec2(0,0), false, offsetof(ScatterPlotNode, m_ViewportRangeMin)))
        .addArg(Arg<glm::vec2>("viewportrangemax", glm::vec2(0,0), false, offsetof(ScatterPlotNode, m_ViewportRangeMax)))
        .addArg(Arg<Color>("color", Color("FFFFFF"), false, offsetof(ScatterPlotNode, m_Color)))
        ;

    const char* allowedParentNodeNames[] = {"div", "canvas", "avg", 0};
    TypeRegistry::get()->registerType(def, allowedParentNodeNames);
}

ScatterPlotNode::ScatterPlotNode(const ArgList& args, const string& sPublisherName) : RasterNode(sPublisherName)
{
    args.setMembers(this);
    m_ViewportExtent = m_ViewportRangeMax - m_ViewportRangeMin;
}

ScatterPlotNode::~ScatterPlotNode()
{
}

void ScatterPlotNode::connectDisplay()
{
    m_pTex = GLContextManager::get()->createTexture(getSize(), R8G8B8A8, getMipmap());
    getSurface()->create(R8G8B8A8, m_pTex);
    setupFX();
    RasterNode::connectDisplay();
}

void ScatterPlotNode::disconnect(bool bKill)
{
    // TODO: Delete texture.
    RasterNode::disconnect(bKill);
}

static ProfilingZoneID PrerenderProfilingZone("ScatterPlotNode::prerender");

void ScatterPlotNode::preRender(const VertexArrayPtr& pVA, bool bIsParentActive, float parentEffectiveOpacity)
{
    ScopeTimer timer(PrerenderProfilingZone);
    AreaNode::preRender(pVA, bIsParentActive, parentEffectiveOpacity);

    if (m_bDataChanged) {
        BitmapPtr pBmp = createPlotBmp();

        GLContextManager::get()->scheduleTexUpload(m_pTex, pBmp);
        scheduleFXRender();
        m_bDataChanged = false;
    }
    calcVertexArray(pVA);
}

static ProfilingZoneID RenderProfilingZone("ScatterPlotNode::render");

void ScatterPlotNode::render(GLContext* pContext, const glm::mat4& transform)
{
    ScopeTimer Timer(RenderProfilingZone);
    blt32(pContext, transform);
}

void ScatterPlotNode::setPosns(const std::vector<glm::vec2>& posns)
{
    m_Posns = posns;
    m_bDataChanged = true;
}

BitmapPtr ScatterPlotNode::createPlotBmp()
{
    BitmapPtr pBmp(new Bitmap(getSize(), R8G8B8A8));
    FilterFill<Pixel32>(Pixel32(0,0,0,0)).applyInPlace(pBmp);

    for (auto pos: m_Posns) {
        glm::vec2 posInBmp = posToBmpPixel(pos);
        pBmp->setPixel(posInBmp, Pixel32(m_Color));
        pBmp->setPixel(posInBmp + glm::vec2(1,0), Pixel32(m_Color));
        pBmp->setPixel(posInBmp + glm::vec2(0,1), Pixel32(m_Color));
        pBmp->setPixel(posInBmp + glm::vec2(1,1), Pixel32(m_Color));
    }

    return pBmp;
}

glm::vec2 ScatterPlotNode::posToBmpPixel(const glm::vec2& pos)
{
    glm::vec2 normPos = (pos - m_ViewportRangeMin)/ m_ViewportExtent;
    return normPos * getSize();
}
