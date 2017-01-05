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

#ifndef _User_H_
#define _User_H_

#include <api.h>

#include <base/GLMHelper.h>

#include "HeadData.h"

class Touch
{
public:
    Touch(int userid, const glm::vec2& pos, float time, float duration);

    const glm::vec2& getPos() const;
    float getTime() const;
    float getDuration() const;

private:
    int m_UserID;
    glm::vec2 m_Pos;
    float m_Time;
    float m_Duration;
};

class User
{
public:
    User(int userid, float duration);
    virtual ~User();

    void addHeadData(const HeadData& head);
    void addTouch(const Touch& touch);

    int getUserID() const;
    const glm::vec3& getHeadPos(float time) const;
    const glm::vec2& getWallViewpoint(float time) const;
    const glm::vec3& getHeadRot(float time) const;

    glm::vec3 getHeadPosAvg(float time, int smoothness) const;
    float getDistTravelled(float startTime, float endTime) const;
    float getAvgDistFromWall(float startTime, float endTime) const;

    std::vector<Touch> getTouches(float startTime, float endTime) const;
    std::vector<glm::vec2> getHeadXZPosns(float startTime, float endTime) const;
    std::vector<glm::vec2> getHeadViewpoints(float startTime, float endTime) const;

private:
    int timeToIndex(float time) const;

    int m_UserID;
    float m_Duration;

    std::vector<HeadData> m_HeadData;
    std::vector<Touch> m_Touches;
};

#endif


