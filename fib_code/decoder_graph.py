from typing import Dict

import numpy as np
import pymatching as pm
import rustworkx as rx


class DecoderGraph:
    def __init__(
        self,
        matching_graph: rx.PyGraph,
        hori_probe_fault_id: int,
        verti_probe_fault_id: int,
        stab2node: Dict[int, int],
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
        self.stab2node = stab2node

    def graph_label_attr_fn(self):
        def node_attr(node):
            return {"label": str(node["element"])}

        def edge_attr(edge):
            return {"label ": str(list(edge["fault_ids"])[0])}

        return node_attr, edge_attr

    def decode_prob(self, syndrome: np.array):
        """[summary]
        Args:
            syndrome (np.array): _description_

        Returns:
            _type_: _description_
        """
        res = self.matching_decoder.decode(syndrome)
        return res[self.hori_probe_fault_id], res[self.verti_probe_fault_id], res
