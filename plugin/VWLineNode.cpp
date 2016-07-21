
#include "VWLineNode.h"

#include <base/Exception.h>
#include <base/ScopeTimer.h>
#include <graphics/VertexArray.h>
#include <player/TypeDefinition.h>
#include <player/TypeRegistry.h>

#include <iostream>
#include <string>
#include <math.h>

using namespace avg;
using namespace std;
using namespace boost;


void VWLineNode::registerType()
{
    TypeDefinition def = TypeDefinition("vwlinenode", "vectornode", 
            ExportedObject::buildObject<VWLineNode>);
    const char* allowedParentNodeNames[] = {"div", "canvas", "avg", 0};
    TypeRegistry::get()->registerType(def, allowedParentNodeNames);
}

VWLineNode::VWLineNode(const ArgList& args, const string& sPublisherName)
    : VectorNode(args, sPublisherName)
{
    args.setMembers(this);
}

VWLineNode::~VWLineNode()
{
}

void VWLineNode::setValues(const vector<glm::vec2>& pts, const vector<float>& widths, 
        const vector<float>& opacities)
{
    Pixel32 color = getColor();
    m_VertexCoords.clear();
    m_Colors.clear();
    m_Triangles.clear();

    // First point
    glm::vec2 pt0 = pts[0];
    glm::vec2 offset(0, widths[0]/2);
    glm::vec2 pt0_t = pt0 - offset;
    glm::vec2 pt0_b = pt0 + offset;
    m_VertexCoords.push_back(pt0_t);
    m_VertexCoords.push_back(pt0);
    m_VertexCoords.push_back(pt0_b);
    appendColors(3, color, opacities[0]);

    for (int i=1; i<pts.size()-1; ++i) {
        pt0 = pts[i-1];
        glm::vec2 pt1 = pts[i];
        glm::vec2 pt2 = pts[i+1];
        float w = widths[i]/2;
        int vi = m_VertexCoords.size();

        glm::vec2 delta0 = pt1 - pt0;
        glm::vec2 offset0 = glm::normalize(glm::vec2(-delta0.y, delta0.x)) * w;
        glm::vec2 delta1 = pt2 - pt1;
        glm::vec2 offset1 = glm::normalize(glm::vec2(-delta1.y, delta1.x)) * w;

        float slope1 = (pt1.y-pt0.y)/(pt1.x-pt0.x);
        float slope2 = (pt2.y-pt1.y)/(pt2.x-pt1.x);
        if (fabs(slope1-slope2) < 0.03) {
            // Near-parallel lines
            glm::vec2 pt1_t = pt1 - offset0;
            glm::vec2 pt1_b = pt1 + offset0;
            glm::vec2 pt0_t = pt0 - offset0;
            glm::vec2 pt0_b = pt0 + offset0;
            handleOverlap(pt1_b, pt0_b);
            handleOverlap(pt1_t, pt0_t);

            m_VertexCoords.push_back(pt1_t);
            m_VertexCoords.push_back(pt1);
            m_VertexCoords.push_back(pt1_b);
            appendColors(3, color, opacities[i]);
                
            m_Triangles.push_back(glm::ivec3(vi-3, vi  , vi+1));
            m_Triangles.push_back(glm::ivec3(vi-3, vi+1, vi-2));
            m_Triangles.push_back(glm::ivec3(vi-2, vi+1, vi-1));
            m_Triangles.push_back(glm::ivec3(vi-1, vi+1, vi+2));
        } else if (slope1 < slope2) {
            // Curve to the right: Small triangle at top.
            glm::vec2 pt1_tl = pt1 - offset0;
            glm::vec2 pt1_bl = pt1 + offset0;
            glm::vec2 pt0_b = pt0 + offset0;

            glm::vec2 pt1_tr = pt1 - offset1;
            glm::vec2 pt1_br = pt1 + offset1;
            glm::vec2 pt2_b = pt2 + offset1;

            glm::vec2 pt1_b = intersectLines(pt0_b, pt1_bl, pt1_br, pt2_b);
            handleOverlap(pt1_b, pt0_b);

            m_VertexCoords.push_back(pt1_tl);
            m_VertexCoords.push_back(pt1_tr);
            m_VertexCoords.push_back(pt1);
            m_VertexCoords.push_back(pt1_b);
            appendColors(4, color, opacities[i]);

            m_Triangles.push_back(glm::ivec3(vi-3, vi  , vi+2));
            m_Triangles.push_back(glm::ivec3(vi-3, vi+2, vi-2));
            m_Triangles.push_back(glm::ivec3(vi-2, vi+2, vi-1));
            m_Triangles.push_back(glm::ivec3(vi-1, vi+2, vi+3));
            m_Triangles.push_back(glm::ivec3(vi,   vi+1, vi+2));
        } else {
            // Curve to the left: Small triangle at bottom
            glm::vec2 pt1_bl = pt1 + offset0;
            glm::vec2 pt1_tl = pt1 - offset0;
            glm::vec2 pt0_t = pt0 - offset0;

            glm::vec2 pt1_br = pt1 + offset1;
            glm::vec2 pt1_tr = pt1 - offset1;
            glm::vec2 pt2_t = pt2 - offset1;

            glm::vec2 pt1_t = intersectLines(pt0_t, pt1_tl, pt1_tr, pt2_t);
            handleOverlap(pt1_t, pt0_t);

            m_VertexCoords.push_back(pt1_bl);
            m_VertexCoords.push_back(pt1_t);
            m_VertexCoords.push_back(pt1);
            m_VertexCoords.push_back(pt1_br);
            appendColors(4, color, opacities[i]);

            m_Triangles.push_back(glm::ivec3(vi-3, vi+1, vi+2));
            m_Triangles.push_back(glm::ivec3(vi-3, vi+2, vi-2));
            m_Triangles.push_back(glm::ivec3(vi-2, vi+2, vi-1));
            m_Triangles.push_back(glm::ivec3(vi-1, vi+2, vi  ));
            m_Triangles.push_back(glm::ivec3(vi,   vi+2, vi+3));
        }
    }
    // Last point
    int i = pts.size()-1;
    int vi = m_VertexCoords.size();
    glm::vec2 pt1 = pts[i];
    offset = glm::vec2(0, widths[i]/2);
    glm::vec2 pt1_t = pt1 - offset;
    glm::vec2 pt1_b = pt1 + offset;
    m_VertexCoords.push_back(pt1_t);
    m_VertexCoords.push_back(pt1);
    m_VertexCoords.push_back(pt1_b);
    appendColors(3, color, opacities[i]);

    m_Triangles.push_back(glm::ivec3(vi-3, vi  , vi+1));
    m_Triangles.push_back(glm::ivec3(vi-3, vi+1, vi-2));
    m_Triangles.push_back(glm::ivec3(vi-2, vi+1, vi-1));
    m_Triangles.push_back(glm::ivec3(vi-1, vi+1, vi+2));

    setDrawNeeded();
}

void VWLineNode::calcVertexes(const VertexDataPtr& pVertexData, Pixel32 color)
{
    for (unsigned int i = 0; i < m_VertexCoords.size(); i++) {
        pVertexData->appendPos(m_VertexCoords[i], glm::vec2(0,0), m_Colors[i]);
    }

    for (unsigned int i = 0; i < m_Triangles.size(); i++) {
        pVertexData->appendTriIndexes(m_Triangles[i].x, m_Triangles[i].y, 
                m_Triangles[i].z);
    }
}

glm::vec2 VWLineNode::intersectLines(const glm::vec2& pt00, const glm::vec2& pt01,
        const glm::vec2& pt10, const glm::vec2& pt11)
{
    // Returns intersection of two lines given two points on each line.
    // Line0 is (pt00, pt01), line1 is (pt10, pt11)
    // See https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    float denom = (pt00.x-pt01.x) * (pt10.y-pt11.y) - (pt00.y-pt01.y) * (pt10.x-pt11.x);
    float x = ((pt00.x*pt01.y - pt00.y*pt01.x) * (pt10.x-pt11.x)
             - (pt00.x-pt01.x) * (pt10.x*pt11.y - pt10.y*pt11.x))
            /denom;
    float y = ((pt00.x*pt01.y - pt00.y*pt01.x) * (pt10.y-pt11.y)
             - (pt00.y-pt01.y) * (pt10.x*pt11.y - pt10.y*pt11.x))
            /denom;
    return glm::vec2(x,y);    
}
        
void VWLineNode::appendColors(int numEntries, avg::Pixel32 color, float opacity)
{
    color.setA(opacity*255);
    for (int i=0; i < numEntries; i++) {
        m_Colors.push_back(color);
    }
}

void VWLineNode::handleOverlap(glm::vec2& pt1, const glm::vec2& pt0)
{
    if (pt1.x < pt0.x) {
        pt1 = pt0;
    }
}
