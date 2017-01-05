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
                const std::vector<float>& dists);
        void setHighlights(std::vector<float> xPosns, std::vector<float> widths);
        
        virtual void calcVertexes(const avg::VertexDataPtr& pVertexData,
                avg::Pixel32 color);

    private:
        void appendColors(int numEntries, avg::Pixel32 color, float opacity);
        float calcWidth(float dist);
        float calcVertWidth(float width, float angle);
        float getLineAngle(const glm::vec2& pt1, const glm::vec2& pt2);
        float calcOpacity(float dist);
        glm::vec2 posOnLine(float x) const;

        std::vector<glm::vec2> m_Pts;
        std::vector<glm::vec2> m_VertexCoords;
        std::vector<avg::Pixel32> m_Colors;
        std::vector<glm::ivec3> m_Triangles;

        float m_MaxWidth;
        bool m_bUseOpacity;
};

typedef boost::shared_ptr<VWLineNode> VWLineNodePtr;

#endif

