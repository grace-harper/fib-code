from typing import Dict

import numpy as np
import pymatching as pm
import rustworkx as rx


class DecoderGraph:
    def __init__(
        self,
        matching_graph: rx.PyGraph,
        probe_indices,
        hori_probe_fault_id: int,
        verti_probe_fault_id: int,
        symmetry_stab2node: Dict[int, int],
    ) -> None:
        """_summary_

        Args:
            matching_graph (rx.PyGraph): _description_
            hori_probe_fault_id (int): _description_
            verti_probe_fault_id (int): _description_
            stab2node (Dict[int, int]): _description_
        """

        self.matching_decoder = pm.Matching(matching_graph)
        self.matching_graph = matching_graph
        self.hori_probe_fault_id = hori_probe_fault_id
        self.verti_probe_fault_id = verti_probe_fault_id
        self.symmetry_stab2node = symmetry_stab2node
        self.probe_indices = probe_indices

    def graph_label_attr_fn(self):
        def node_attr(node):
            return {"label": str(node["element"])}

        def edge_attr(edge):
            return {"label ": str(list(edge["fault_ids"])[0])}

        return node_attr, edge_attr

    def decode_prob(self, symmetry_indx_syndrome: np.array):
        # convert syndrome to node
        cur_node_syndrome = [0] * len(symmetry_indx_syndrome)
        for stabindx, value in enumerate(symmetry_indx_syndrome):
            nodeindx = self.symmetry_stab2node[stabindx]
            cur_node_syndrome[nodeindx] = value  # TODO is right?

        res = self.matching_decoder.decode(cur_node_syndrome)

        return [res[indx] for indx in self.probe_indices], res
        return res[self.hori_probe_fault_id], res[self.verti_probe_fault_id], res
