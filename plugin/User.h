
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


