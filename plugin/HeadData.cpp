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

#include "HeadData.h"

#include <iomanip>

using namespace std;

HeadData::HeadData(int userid, const glm::vec3& pos, const glm::vec3& rot, double time)
    : m_UserID(userid),
      m_Pos(pos),
      m_Rot(rot),
      m_Time(time)
{
}

HeadData::~HeadData()
{
}

int HeadData::getUserID() const
{
    return m_UserID;
}

const glm::vec3& HeadData::getPos() const
{
    return m_Pos;
}

const glm::vec3& HeadData::getRot() const
{
    return m_Rot;
}

double HeadData::getTime() const
{
    return m_Time;
}

const glm::vec2& HeadData::getWallViewpoint() const
{
    return m_WallViewpoint;
}

void HeadData::setWallViewpoint(const glm::vec2& pt)
{
    m_WallViewpoint = pt;
}

const glm::vec3& HeadData::getPosPrefixSum() const
{
    return m_PosPrefixSum;
}

void HeadData::setPosPrefixSum(const glm::vec3& sum)
{
    m_PosPrefixSum = sum;
}

