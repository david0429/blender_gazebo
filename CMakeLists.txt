cmake_minimum_required(VERSION 2.8.3)
project(blender_gazebo)

find_package(catkin REQUIRED COMPONENTS)

catkin_package()
include_directories(
  ${catkin_INCLUDE_DIRS}
)


install(DIRECTORY blender_gazebo worlds
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
install(DIRECTORY scripts
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
