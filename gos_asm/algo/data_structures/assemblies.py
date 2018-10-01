# -*- coding: utf-8 -*-
from bg.genome import BGGenome
from bg.multicolor import Multicolor
from bg.utils import get_from_dict_with_path


class AssemblyPoint(object):
    __slots__ = ["vertex1", "vertex2", "target_multicolor",
                 "fragment1", "fragment2",
                 "fragment1_sign", "fragment2_sign", "info", "id", "cc_id"]
    id_cnt = 0

    logger_entry_string = "{ap_id:^4} | {genome:^10} | {vertex1:>7} - {vertex2:<7} | {fragment1:>9} - {fragment2:<9} |" \
                          " {repeat1:>10} -" \
                          " {repeat2:<10} |" \
                          " {cc_id:^7} |" \
                          " {s_edge_existed:^6} |" \
                          " {repeat_guidance} |" \
                          ""
    assembly_point_file_entry = "{ap_id:^4} | {genome:^10} | {vertex1:>7} - {vertex2:<7} | {fragment1:>9} - {fragment2:<9} |" \
                                " {repeat1:>10} -" \
                                " {repeat2:<10} |" \
                                " {cc_id:^7} |" \
                                " {s_edge_existed:^6} |" \
                                " {repeat_guidance} |" \
                                " {target_multicolor} "

    def __init__(self, vertex1=None, vertex2=None,
                 fragment1=None, fragment2=None,
                 sign1=None, sign2=None,
                 additional_information=None, cc_id=None):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.target_multicolor = None if additional_information is None else additional_information.target_multicolor
        self.info = additional_information
        self.fragment1 = None if additional_information is None else get_from_dict_with_path(additional_information.iedge1.data, key="name",
                                                                                             path=["fragment"])
        self.fragment2 = None if additional_information is None else get_from_dict_with_path(additional_information.iedge2.data, key="name",
                                                                                             path=["fragment"])
        fr1_fo = None if additional_information is None else get_from_dict_with_path(additional_information.iedge1.data,
                                                                                     key="forward_orientation", path=["fragment"])
        self.fragment1_sign = None if fr1_fo is None else ("+" if vertex1 == fr1_fo[0] else "-")
        fr2_fo = None if additional_information is None else get_from_dict_with_path(additional_information.iedge2.data,
                                                                                     key="forward_orientation", path=["fragment"])
        self.fragment2_sign = None if fr2_fo is None else ("+" if vertex2 == fr2_fo[1] else "-")
        self.id = AssemblyPoint.id_cnt
        self.cc_id = cc_id
        AssemblyPoint.id_cnt += 1

    def get_for_csv_format(self):
        if self.fragment2 is None or self.fragment1 < self.fragment2:
            return [self.fragment1, self.fragment1_sign, self.fragment2, self.fragment2_sign, self.vertex1, self.vertex2, self.info]
        else:
            return [self.fragment2, self.fragment2_sign, self.fragment1, self.fragment1_sign, self.vertex2, self.vertex1, self.info]

    def __str__(self):
        repeat1 = str(self.info.repeat_info["repeat_name_1"]) + ("" if self.info.repeat_info[
                                                   "repeat_dir_1"] is None else ("(" + str(self.info.repeat_info[
                                                   "repeat_dir_1"]) + ")"))
        repeat2 = str(self.info.repeat_info["repeat_name_2"]) + ("" if self.info.repeat_info[
                                                   "repeat_dir_2"] is None else ("(" + str(self.info.repeat_info[
                                                   "repeat_dir_2"]) + ")"))
        return self.logger_entry_string.format(vertex1=self.vertex1.name, vertex2=self.vertex2.name,
                                               repeat1=repeat1,
                                               repeat2=repeat2,
                                               s_edge_existed=str(self.info.support_edge is not None)
                                               )

    def as_logger_entry(self):
        repeat1 = str(self.info.repeat_info["repeat_name_1"]) + ("" if self.info.repeat_info[
                                                   "repeat_dir_1"] is None else ("(" + str(self.info.repeat_info[
                                                   "repeat_dir_1"]) + ")"))
        repeat2 = str(self.info.repeat_info["repeat_name_2"]) + ("" if self.info.repeat_info[
                                                   "repeat_dir_2"] is None else ("(" + str(self.info.repeat_info[
                                                   "repeat_dir_2"]) + ")"))
        return self.logger_entry_string.format(vertex1=self.vertex1.name, vertex2=self.vertex2.name,
                                               fragment1=("" if self.fragment1_sign == "+" else "-") + self.fragment1,
                                               fragment2=("" if self.fragment2_sign == "+" else "-") + self.fragment2,
                                               cc_id=self.cc_id,
                                               repeat1=repeat1,
                                               repeat2=repeat2,
                                               s_edge_existed=str(self.info.support_edge is not None),
                                               ap_id=self.id,
                                               repeat_guidance=str(self.info.repeat_info["repeat_guidance"]),
                                               genome=self.info.target_color.colors.pop().name)

    def as_assembly_points_file_entry_string(self):
        repeat1 = str(self.info.repeat_info["repeat_name_1"]) + ("" if self.info.repeat_info[
                                                   "repeat_dir_1"] is None else ("(" + str(self.info.repeat_info[
                                                   "repeat_dir_1"]) + ")"))
        repeat2 = str(self.info.repeat_info["repeat_name_2"]) + ("" if self.info.repeat_info[
                                                   "repeat_dir_2"] is None else ("(" + str(self.info.repeat_info[
                                                   "repeat_dir_2"]) + ")"))
        return self.assembly_point_file_entry.format(vertex1=self.vertex1.name, vertex2=self.vertex2.name,
                                                     fragment1=("" if self.fragment1_sign == "+" else "-") + self.fragment1,
                                                     fragment2=("" if self.fragment2_sign == "+" else "-") + self.fragment2,
                                                     cc_id=self.cc_id,
                                                     repeat1=repeat1,
                                                     repeat2=repeat2,
                                                     s_edge_existed=str(self.info.support_edge is not None),
                                                     ap_id=self.id,
                                                     repeat_guidance=", ".join(self.info.repeat_info["repeat_guidance"]),
                                                     genome=self.info.target_color.colors.pop().name,
                                                     target_multicolor=", ".join(
                                                         sorted(color.name for color in self.target_multicolor.colors)))

    @classmethod
    def assembly_file_header_string(cls):
        return cls.assembly_point_file_entry.format(ap_id="id", genome="genome", vertex1="v1", vertex2="v2", fragment1="fragment1",
                                                    fragment2="fragment2",
                                                    repeat1="repeat1", repeat2="repeat2", cc_id="cc_id", s_edge_existed="s_edge",
                                                    repeat_guidance="repeat_guidance", target_multicolor="MC")

    @classmethod
    def logger_file_header_string(cls):
        return cls.logger_entry_string.format(ap_id="id", genome="genome", vertex1="v1", vertex2="v2", fragment1="fragment1",
                                              fragment2="fragment2",
                                              repeat1="repeat1", repeat2="repeat2", cc_id="cc_id", s_edge_existed="s_edge",
                                              repeat_guidance="repeat_guidance", target_multicolor="MC")

    @classmethod
    def from_assembly_points_file(cls, separated_values):
        info = AssemblyPointInfo()
        info.target_color = Multicolor(BGGenome(separated_values["genome"].strip()))
        repeats = separated_values["repeat1 - repeat2"].strip()
        repeat1, repeat2 = repeats.split(" - ")
        repeat_info = {
            "repeat_name_1": repeat1[:-3],
            "repeat_dir_1": repeat1[-2],
            "repeat_name_2": repeat2[:-3],
            "repeat_dir_2": repeat2[-2]
        }
        support_edge_existed = separated_values["s_edge"]
        info.support_edge = support_edge_existed
        repeat_guidance = separated_values["repeat_guidance"].strip()
        repeat_guidance = repeat_guidance.split(", ")
        repeat_info["repeat_guidance"] = repeat_guidance
        info.repeat_info = repeat_info
        target_multicolor = Multicolor(*list(map(lambda entry: BGGenome(entry), separated_values["MC"].strip().split(", "))))
        info.target_multicolor = target_multicolor

        result = cls()
        result.id = separated_values["id"].strip()
        result.cc_id = separated_values.get("cc_id", None).strip()
        vertices = separated_values["v1 - v2"]
        vertex1, vertex2 = vertices.split(" - ")
        vertex1, vertex2 = vertex1.strip(), vertex2.strip()
        result.vertex1 = vertex1
        result.vertex2 = vertex2
        fragments = separated_values["fragment1 - fragment2"].strip()
        fragment1, fragment2 = fragments.split(" - ")
        fragment1, fragment2 = fragment1.strip(), fragment2.strip()
        result.fragment1 = fragment1
        result.fragment2 = fragment2
        result.fragment1_sign = "-" if result.fragment1.startswith("-") else "+"
        result.fragment2_sign = "-" if result.fragment2.startswith("-") else "+"
        if result.fragment1.startswith("-"):
            result.fragment1 = result.fragment1[1:]
        if result.fragment2.startswith("-"):
            result.fragment2 = result.fragment2[1:]
        result.info = info
        return result


class AssemblyPointInfo(object):
    __slots__ = ["support_edge",
                 "target_color",
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
                 target_multicolor=None,
                 target_color=None):
        self.support_edge = support_edge
        self.iedge1 = iedge1
        self.iedge2 = iedge2
        self.repeat_info = {} if repeat_info is None else repeat_info
        self.evolutionary_scenarios = evolutionary_scenarios
        self.allowed = allowed
        self.target_multicolor = target_multicolor
        self.target_color = target_color
