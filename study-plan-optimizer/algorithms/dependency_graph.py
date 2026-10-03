"""
Topic Dependency Graph & Topological Sorting.

Data Structure & Algorithms:
----------------------------
Represents prerequisites as a Directed Acyclic Graph (DAG):
- Nodes: Academic Topics
- Directed Edges: Prerequisite (U) -> Dependent Topic (V)  [U must be learned before V]

Algorithms Implemented:
1. Cycle Detection (3-Color DFS or Kahn's in-degree)
2. Topological Sort (Kahn's Algorithm using BFS queue)
3. Dependency Validation & Missing Prerequisite Alerts
4. Transitive Dependency Closure (Auto-inclusion of upstream prerequisites)
"""
from typing import List, Dict, Set, Tuple, Any
from collections import deque
from models.topic import Topic


class DependencyGraph:
    """
    DAG of topic prerequisites with topological sorting and validation.
    """
    def __init__(self, topics: List[Topic]):
        self.topics_map: Dict[str, Topic] = {t.id: t for t in topics}
        # adj[u] = list of topics that depend on u (u is prerequisite of v)
        self.adj: Dict[str, List[str]] = {t.id: [] for t in topics}
        # prereqs[v] = list of prerequisites for topic v
        self.prereqs: Dict[str, List[str]] = {t.id: list(t.prerequisites) for t in topics}
        self.in_degree: Dict[str, int] = {t.id: 0 for t in topics}

        self._build_graph()

    def _build_graph(self) -> None:
        """Constructs adjacency list and calculates in-degrees."""
        for topic_id, prereq_list in self.prereqs.items():
            for p_id in prereq_list:
                if p_id in self.adj:
                    self.adj[p_id].append(topic_id)
                    self.in_degree[topic_id] += 1

    def detect_cycle(self) -> Tuple[bool, List[str]]:
        """
        Detects if there is any circular dependency cycle using Kahn's algorithm.
        Returns (has_cycle, cycle_description).
        """
        temp_in_degree = dict(self.in_degree)
        queue = deque([node for node, deg in temp_in_degree.items() if deg == 0])
        visited_count = 0

        while queue:
            node = queue.popleft()
            visited_count += 1
            for neighbor in self.adj.get(node, []):
                temp_in_degree[neighbor] -= 1
                if temp_in_degree[neighbor] == 0:
                    queue.append(neighbor)

        has_cycle = (visited_count != len(self.topics_map))
        if has_cycle:
            cyclic_nodes = [node for node, deg in temp_in_degree.items() if deg > 0]
            cycle_names = [self.topics_map[cid].name for cid in cyclic_nodes if cid in self.topics_map]
            return True, cycle_names
        return False, []

    def topological_sort(self, topic_ids: List[str] = None) -> List[Topic]:
        """
        Returns topics ordered topologically (prerequisites first) using Kahn's algorithm.
        If topic_ids is provided, restricts ordering to that subset.
        """
        target_ids = set(topic_ids) if topic_ids is not None else set(self.topics_map.keys())

        # Subgraph in-degrees
        sub_in_degree: Dict[str, int] = {tid: 0 for tid in target_ids}
        sub_adj: Dict[str, List[str]] = {tid: [] for tid in target_ids}

        for tid in target_ids:
            for p_id in self.prereqs.get(tid, []):
                if p_id in target_ids:
                    sub_adj[p_id].append(tid)
                    sub_in_degree[tid] += 1

        queue = deque([node for node, deg in sub_in_degree.items() if deg == 0])
        ordered_ids: List[str] = []

        while queue:
            node = queue.popleft()
            ordered_ids.append(node)
            for neighbor in sub_adj.get(node, []):
                sub_in_degree[neighbor] -= 1
                if sub_in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # In case of disconnected or cyclic components, append remaining nodes
        for tid in target_ids:
            if tid not in ordered_ids:
                ordered_ids.append(tid)

        return [self.topics_map[tid] for tid in ordered_ids if tid in self.topics_map]

    def validate_prerequisites_for_selected(
        self,
        selected_topics: List[Topic],
        prep_threshold: float = 60.0
    ) -> List[Dict[str, Any]]:
        """
        Validates whether prerequisites of selected topics are either:
        1. Also selected in the study plan, OR
        2. Already well-prepared (current_prep >= prep_threshold).

        Returns list of warning advisories.
        """
        selected_ids = {t.id for t in selected_topics}
        warnings = []

        for t in selected_topics:
            for prereq_id in t.prerequisites:
                prereq_topic = self.topics_map.get(prereq_id)
                if not prereq_topic:
                    continue

                is_selected = prereq_id in selected_ids
                is_prepared = prereq_topic.current_prep >= prep_threshold

                if not is_selected and not is_prepared:
                    warnings.append({
                        "topic_name": t.name,
                        "prereq_id": prereq_id,
                        "prereq_name": prereq_topic.name,
                        "prereq_prep": prereq_topic.current_prep,
                        "message": (
                            f"Topic '{t.name}' requires '{prereq_topic.name}', "
                            f"which is neither in your study plan nor adequately prepared "
                            f"({prereq_topic.current_prep:.0f}% < {prep_threshold:.0f}%)."
                        )
                    })

        return warnings

    def get_prerequisite_closure(self, topic_id: str) -> Set[str]:
        """
        Finds all recursive upstream prerequisites for a given topic using DFS.
        """
        closure = set()
        stack = list(self.prereqs.get(topic_id, []))

        while stack:
            curr = stack.pop()
            if curr not in closure:
                closure.add(curr)
                stack.extend(self.prereqs.get(curr, []))

        return closure
