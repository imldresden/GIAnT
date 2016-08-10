#ifndef _Path_H_
#define _Path_H_

#include <api.h>

#include <base/GLMHelper.h>
#include <vector>

std::vector<glm::vec2> simplifyPath(std::vector<glm::vec2>& pts, double epsilon);

#endif



