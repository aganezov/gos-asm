# -*- coding: utf-8 -*-

def log_bg_stats(bg, logger):
    rnodes_cnt = len(list(node for node in bg.nodes() if node.is_regular_vertex))
    inodes_cnt = len(list(node for node in bg.nodes() if node.is_irregular_vertex))
    logger.debug("Nodes :: regular = {rnodes:^6} | irregular = {inodes:^6}"
                 "".format(rnodes=rnodes_cnt, inodes=inodes_cnt))
    redges_cnt = len(list(edge for edge in bg.edges() if not edge.is_irregular_edge))
    iedges_cnt = len(list(edge for edge in bg.edges() if edge.is_irregular_edge))
    logger.debug("Edges :: regular = {redges:^6} | irregular = {iedges:^6}"
                 "".format(redges=redges_cnt, iedges=iedges_cnt))