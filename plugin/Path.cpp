#include "Path.h"

#include <cmath>

using namespace std;

const std::pair<int, double> findMaximumDistance(const vector<glm::vec2>& pts)
{
    glm::vec2 firstpoint = pts[0];
    glm::vec2 lastpoint = pts[pts.size()-1];
    int index = 0;       // index to be returned
    double maxDist = -1; // the Maximum distance to be returned

    glm::vec2 p = lastpoint - firstpoint;
    for (int i=1; i<pts.size()-1; i++) {
        glm::vec2 pp = pts[i] - firstpoint;
        float dist = std::abs(glm::dot(pp, p)) / glm::length(p);   // point-to-line distance
        if (dist > maxDist) {
            maxDist = dist;
            index = i;
        }
    }
    return std::make_pair(index, maxDist);
}


// Implements Ramer-Douglas-Peucker-Algorithm for path simplication.
// From https://github.com/Yongjiao/Ramer-Douglas-Peucker-Algorithm/blob/master/simplifyPath.cpp
// Possibly faster version at https://www.namekdev.net/2014/06/iterative-version-of-ramer-douglas-peucker-line-simplification-algorithm/
vector<glm::vec2> simplifyPath(vector<glm::vec2>& pts, double epsilon)
{
    if (pts.size()<3) {
        return pts;
    }
    std::pair<int, double> maxDistance = findMaximumDistance(pts);
    if (maxDistance.second >= epsilon) {
        int index = maxDistance.first;
        vector<glm::vec2>::iterator it=pts.begin();
        vector<glm::vec2> path1(pts.begin(), it+index+1); // new path l1 from 0 to index
        vector<glm::vec2> path2(it+index, pts.end());     // new path l2 from index to last

        vector<glm::vec2> r1 = simplifyPath(path1, epsilon);
        vector<glm::vec2> r2 = simplifyPath(path2, epsilon);

        //Concat simplified path1 and path2 together
        vector<glm::vec2> rs(r1);
        rs.pop_back();
        rs.insert(rs.end(), r2.begin(), r2.end());
        return rs;
    }
    else { // base case 2, all points between are to be removed.
        vector<glm::vec2> r(1, pts[0]);
        r.push_back(pts[pts.size()-1]);
        return r;
    }    
}

