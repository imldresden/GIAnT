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

#include "User.h"

#include "Path.h"

using namespace std;

Touch::Touch(int userid, const glm::vec2& pos, float time, float duration)
    : m_UserID(userid),
      m_Pos(pos),
      m_Time(time),
      m_Duration(duration)
{
}

const glm::vec2& Touch::getPos() const
{
    return m_Pos;
}

float Touch::getTime() const
{
    return m_Time;
}

float Touch::getDuration() const
{
    return m_Duration;
}


User::User(int userid, float duration)
    : m_UserID(userid),
      m_Duration(duration)
{
}

User::~User()
{
}

void User::addHeadData(const HeadData& head)
{
    m_HeadData.push_back(head);
}

void User::addTouch(const Touch& touch)
{
    m_Touches.push_back(touch);
}

int User::getUserID() const
{
    return m_UserID;
}

const glm::vec3& User::getHeadPos(float time) const
{
    int i = timeToIndex(time);
    return m_HeadData[i].getPos();
}

const glm::vec2& User::getWallViewpoint(float time) const
{
    int i = timeToIndex(time);
    return m_HeadData[i].getWallViewpoint();
}

const glm::vec3& User::getHeadRot(float time) const
{
    int i = timeToIndex(time);
    return m_HeadData[i].getRot();
}

glm::vec3 User::getHeadPosAvg(float time, int smoothness) const
{
    int i = timeToIndex(time);
    glm::vec3 startSum = m_HeadData[fmax(0, i - smoothness/2)].getPosPrefixSum();
    glm::vec3 endSum = m_HeadData[fmin(m_HeadData.size()-1, i + int((smoothness+1)/2))].getPosPrefixSum();
    glm::vec3 headPos = glm::vec3(
            (endSum.x - startSum.x) / smoothness,
            (endSum.y - startSum.y) / smoothness,
            (endSum.z - startSum.z) / smoothness);
    return headPos;
}

float User::getDistTravelled(float startTime, float endTime) const
{
    int start_i = timeToIndex(startTime);
    int end_i = timeToIndex(endTime);
    vector<glm::vec2> posns;
    for (int i=start_i; i<end_i; ++i) {
        const HeadData& head = m_HeadData[i];
        posns.push_back(glm::vec2(head.getPos().x, head.getPos().z));
    }
//    vector<glm::vec2> posns = simplifyPath(origPosns, 0.1f);

    float dist = 0.0f;
    glm::vec2 pos = posns[0];
    glm::vec2 oldPos;
    for (int i=1; i<posns.size(); ++i) {
        oldPos = pos;
        pos = posns[i];
        dist += glm::distance(pos, oldPos);
    }
    return dist;
}

float User::getAvgDistFromWall(float startTime, float endTime) const
{
    int start_i = timeToIndex(startTime);
    int end_i = timeToIndex(endTime);
    float sum = 0;
    for (int i=start_i; i<end_i; ++i) {
        sum += m_HeadData[i].getPos().z;
    }
    return sum/(end_i-start_i);
}



vector<Touch> User::getTouches(float startTime, float endTime) const
{
    vector<Touch> touches;
    for (auto touch: m_Touches) {
        if (startTime <= touch.getTime() && touch.getTime() <= endTime) {
            touches.push_back(touch);
        }
    }
    return touches;
}

vector<glm::vec2> User::getHeadXZPosns(float startTime, float endTime) const
{
    vector<glm::vec2> posns;
    int start_i = timeToIndex(startTime);
    int end_i = timeToIndex(endTime);
    for (int i=start_i; i<end_i; ++i) {
        const glm::vec3 pos = m_HeadData[i].getPos();
        posns.push_back(glm::vec2(pos.x, pos.z));
    }
    return posns;
}

vector<glm::vec2> User::getHeadViewpoints(float startTime, float endTime) const
{
    vector<glm::vec2> viewpts;
    int start_i = timeToIndex(startTime);
    int end_i = timeToIndex(endTime);
    for (int i=start_i; i<end_i; ++i) {
        viewpts.push_back(m_HeadData[i].getWallViewpoint());
    }
    return viewpts;

}

int User::timeToIndex(float time) const
{
    return int(time * m_HeadData.size() / m_Duration);
}
