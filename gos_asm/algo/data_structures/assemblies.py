# -*- coding: utf-8 -*-
from bg.utils import get_from_dict_with_path


class AssemblyPoint(object):
    __slots__ = ["vertex1", "vertex2", "target_multicolor",
                 "fragment1", "fragment2",
                 "fragment1_sign", "fragment2_sign", "info", "id", "cc_id"]
    id_cnt = 0

    def __init__(self, vertex1=None, vertex2=None,
                 fragment1=None, fragment2=None,
                 sign1=None, sign2=None,
                 additional_information=None, cc_id=None):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.target_multicolor = None if additional_information is None else additional_information.target_multicolor
        self.info = additional_information
        self.fragment1 = None if additional_information is None else get_from_dict_with_path(additional_information.iedge1.data, key="name", path=["fragment"])
        self.fragment2 = None if additional_information is None else get_from_dict_with_path(additional_information.iedge2.data, key="name", path=["fragment"])
        self.fragment1_sign = sign1
        self.fragment2_sign = sign2
        self.id = AssemblyPoint.id_cnt
        self.cc_id = cc_id
        AssemblyPoint.id_cnt += 1

    def get_for_csv_format(self):
        if self.fragment2 is None or self.fragment1 < self.fragment2:
            return [self.fragment1, self.fragment1_sign, self.fragment2, self.fragment2_sign, self.vertex1, self.vertex2, self.info]
        else:
            return [self.fragment2, self.fragment2_sign, self.fragment1, self.fragment1_sign, self.vertex2, self.vertex1, self.info]

    def __str__(self):
        return "{vertex1:^7} | {vertex2:^7} |" \
               " {repeat1:^10} |" \
               " {repeat2:^10} |" \
               " {s_edge_existed:^5} |" \
               "".format(vertex1=self.vertex1.name, vertex2=self.vertex2.name,
                         repeat1=self.info.repeat_info["repeat_name_1"] + "(" + self.info.repeat_info["repeat_dir_1"] + ")",
                         repeat2=self.info.repeat_info["repeat_name_2"] + "(" + self.info.repeat_info["repeat_dir_2"] + ")",
                         s_edge_existed=str(self.info.support_edge is not None)
                         )

    def as_logger_entry(self):
        return "{ap_id:^4} | {vertex1:>7} - {vertex2:<7} | {fragment1:>7} - {fragment2:<7} |" \
               " {repeat1:>10} -" \
               " {repeat2:<10} |" \
               " {cc_id:^5} |" \
               " {s_edge_existed:^5} |" \
               "".format(vertex1=self.vertex1.name, vertex2=self.vertex2.name,
                         fragment1=self.fragment1, fragment2=self.fragment2,
                         cc_id=self.cc_id,
                         repeat1=self.info.repeat_info["repeat_name_1"] + "(" + self.info.repeat_info["repeat_dir_1"] + ")",
                         repeat2=self.info.repeat_info["repeat_name_2"] + "(" + self.info.repeat_info["repeat_dir_2"] + ")",
                         s_edge_existed=str(self.info.support_edge is not None),
                         ap_id=self.id)
    
    def as_assembly_points_file_string(self):
        return self.as_logger_entry()


class AssemblyPointInfo(object):
    __slots__ = ["support_edge",
                 "repeat_info",
                 "evolutionary_scenarios",
                 "allowed",
                 "iedge1", "iedge2",
                 "target_multicolor"]

    def __init__(self, support_edge=None,
                 iedge1=None, iedge2=None,
                 evolutionary_scenarios=None,
                 allowed=None,
                 repeat_info=None,
                 target_multicolor=None):
        self.support_edge = support_edge
        self.iedge1 = iedge1
        self.iedge2 = iedge2
        self.repeat_info = {} if repeat_info is None else repeat_info
        self.evolutionary_scenarios = evolutionary_scenarios
        self.allowed = allowed
        self.target_multicolor = target_multicolor
