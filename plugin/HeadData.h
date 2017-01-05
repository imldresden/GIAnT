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


#ifndef _HeadData_H_
#define _HeadData_H_

#include <api.h>

#include <base/GLMHelper.h>

class HeadData
{
public:
    HeadData(int userid, const glm::vec3& pos, const glm::vec3& rot, double time);
    virtual ~HeadData();

    int getUserID() const;
    const glm::vec3& getPos() const;
    const glm::vec3& getRot() const;
    double getTime() const;
    const glm::vec2& getWallViewpoint() const;
    void setWallViewpoint(const glm::vec2& pt);
    const glm::vec3& getPosPrefixSum() const;
    void setPosPrefixSum(const glm::vec3& sum);

private:
    int m_UserID;
    glm::vec3 m_Pos;
    glm::vec3 m_Rot;
    double m_Time;
    glm::vec2 m_WallViewpoint;
    glm::vec3 m_PosPrefixSum;
};

#endif

