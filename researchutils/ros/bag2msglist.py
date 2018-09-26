#!/usr/bin/env python
import os
import sys
import math
import rosbag
import rospy
import numpy as np
# PyQt Libraries
from SimplePyQtGUIKit   import SimplePyQtGUIKit
from PyQt4              import QtGui


class Bagfile2MsgList:
    def __init__(self, selected_topics_=None, save_dir_=None, files_=None):
        self.app = QtGui.QApplication(sys.argv)
        self.selected_topics = selected_topics_
        self.save_dir = save_dir_
        self.files = files_

    def get_bagfile(self):
        files=SimplePyQtGUIKit.GetFilePath(isApp=True,caption="Select bag file",filefilter="*bag")
        if len(files)<1:
            print("Error:Please select a bag file")
            sys.exit()

        return files


    @staticmethod
    def get_topic_list(path):
        bag = rosbag.Bag(path)
        topics = bag.get_type_and_topic_info()[1].keys()
        types=[]
        for i in range(0,len(bag.get_type_and_topic_info()[1].values())):
            types.append(bag.get_type_and_topic_info()[1].values()[i][0])

        results=[]
        for to,ty in zip(topics,types):
            results.append(to)

        return results


    def select_topics(self, topics):
        selected=SimplePyQtGUIKit.GetCheckButtonSelect(topics, app=self.app, msg="Select topics")
        topic_names=[]
        for k,v in selected.items():
            if v:
               topic_names.append(k)
        if len(topic_names)==0:
            print("Error:Please select topics")
            sys.exit()

        return topic_names

    def msg_to_nested_dict(self, msg, y_data):
        try:
            for s in type(msg).__slots__:
                val = msg.__getattribute__(s)
                if s not in y_data.keys():
                    if isinstance(val,int) or isinstance(val,float):
                        y_data[s] = []
                    else:
                        y_data[s] = {}
                self.msg_to_nested_dict(val, y_data[s])
        except:
            if isinstance(msg,int) or isinstance(msg,float):
                y_data.append(msg)


    def bag_to_dict(self, filename, topic_names):
        # Start Loading Bag File
        x_dict = dict()
        y_dict = dict()
        try:
            bag = rosbag.Bag(filename)
            for i in range(len(topic_names)):
                x_data = []
                y_data = {}
                first_time = True
                for (topic, msg, t) in bag.read_messages(topics=topic_names[i]):
                    if first_time==True:
                        start = t.to_sec()
                        first_time=False
                    x_data.append(t.to_sec()-start)
                    self.msg_to_nested_dict(msg, y_data)
                x_dict[topic_names[i]] = x_data
                y_dict[topic_names[i]] = y_data
                end = t.to_sec()
                print("Topic: {},       Data Length: {}".format(topic_names[i], len(x_data)))
        except Exception as e:
            rospy.logfatal('failed to load bag files: %s', e)
            exit(1)

        return x_dict, y_dict

    def convert(self):
        """
        convert from rosbag to nested dictionary/list

        Parameters
        -------
        selected_topics : list
            List of Topics. ex) ['/tiwst', '/joystick']

        save_dir : string
            Where to save the output data

        files : list
            Files to read from

        Returns
        -------
        times : list
            List of times for each topic. It starts from 0.

        msgs : dictionary/list
            Topic messages that can be accessed via mutli-dimension dictionary

        files : list
            List of file names
        """
        # Get Saving Path
        if self.save_dir is None:
            save_dir = SimplePyQtGUIKit.GetFolderPath(isApp=True,caption="Select Saving Directory")
        # Get Files that want to be converted
        if self.files is None:
            files = self.get_bagfile()

        times, msgs = {}, {}
        for file in files:
            topic_list = self.get_topic_list(file)
            if self.selected_topics is None:
               self. selected_topics = self.select_topics(topic_list)

            # Convert Bagfile to Dictionary
            time, msg = self.bag_to_dict(file, self.selected_topics)

            times[file] = time
            msgs[file] = msg

        return times, msgs, files
