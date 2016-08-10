
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

