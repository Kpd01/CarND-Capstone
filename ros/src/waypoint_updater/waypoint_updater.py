#!/usr/bin/env python
import numpy as np
import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from scipy.spatial import KDTree
import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

****Completed by Krishna Priya*******
Partial Waypoint Updater completed. 
Subscribes: /base_waypoints,/current_pose
Publishes: /final_waypoints

Next Steps: Need to complete Waypoint Updater(Full)-> Once Traffic light detection is working.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number


class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below


        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below
        self.pose = None
        self.base_Waypts = None
        self.Waypts_2D = None
        self.wayPts_tree = None
        self.loop()

    def loop(self):
        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            if self.pose and self.base_Waypts and self.wayPts_tree:
                rospy.logwarn('about to publish waypoints')
                self.publish_waypoints(self.get_closest_wayPt_index())
            rate.sleep()
    def pose_cb(self, msg):
        self.pose = msg

    def get_closest_wayPt_index(self):
        x = self.pose.pose.position.x
        y = self.pose.pose.position.y
        closest_index = self.wayPts_tree.query([x, y], 1)[1]
        closest_coord = self.Waypts_2D[closest_index]
        prev_coord = self.Waypts_2D[closest_index -1]        
        cl_vect = np.array(closest_coord)
        prev_vect = np.array(prev_coord)
        pos_vect = np.array([x, y])        
        val = np.dot(cl_vect - prev_vect, pos_vect - cl_vect)
        if val > 0:
          closest_index = (closest_index + 1) % len(self.Waypts_2D)
        return closest_index
    def publish_waypoints(self, closest_index):	
        lane = Lane()
        lane.header = self.base_Waypts.header
        lane.waypoints = self.base_Waypts.waypoints[closest_index: closest_index + LOOKAHEAD_WPS]
        self.final_waypoints_pub.publish(lane)
        

    def waypoints_cb(self, waypoints):
        self.base_Waypts = waypoints
        if not self.Waypts_2D:
            self.Waypts_2D = [[waypoint.pose.pose.position.x, waypoint.pose.pose.position.y] for waypoint in waypoints.waypoints]
            self.wayPts_tree = KDTree(self.Waypts_2D)

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        pass

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
