// GIAnT Group Interaction Analysis Toolkit
// Copyright (C) 2017 Interactive Media Lab Dresden
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
