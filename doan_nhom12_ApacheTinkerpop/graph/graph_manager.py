
import time
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.anonymous_traversal import traversal

class GraphManager:
    def __init__(self):
        # Kết nối tới Gremlin Server
        self.connection = DriverRemoteConnection("ws://localhost:8182/gremlin", "g")
        self.g = traversal().withRemote(self.connection)
        self.graph_prefix = f"graph_{int(time.time())}"

    def reset(self):
        """Xóa toàn bộ graph hiện tại (có phân biệt prefix)"""
        self.g.V().drop().iterate()

    def close(self):
        """Đóng kết nối"""
        self.connection.close()

    def build(self, vertices, edges, directed=False, weighted=False):
        """
        vertices: list of vertex names (strings)
        edges: list of [u, v] hoặc [u, v, weight]
        directed: bool
        weighted: bool
        """
        self.reset()

        # Thêm các đỉnh với property graph để phân biệt nhiều graph
        for v in vertices:
            self.g.addV("vertex")\
                  .property("id", str(v))\
                  .property("graph", self.graph_prefix)\
                  .next()

        # Thêm các cạnh
        for e in edges:
            u, v = str(e[0]), str(e[1])
            w = float(e[2]) if weighted and len(e) == 3 else 1.0

            # Add edge từ u -> v
            self.g.addE("edge")\
                  .from_(__.V().has("id", u).has("graph", self.graph_prefix))\
                  .to(__.V().has("id", v).has("graph", self.graph_prefix))\
                  .property("weight", w)\
                  .next()

            # Nếu vô hướng, thêm cạnh ngược
            if not directed:
                self.g.addE("edge")\
                      .from_(__.V().has("id", v).has("graph", self.graph_prefix))\
                      .to(__.V().has("id", u).has("graph", self.graph_prefix))\
                      .property("weight", w)\
                      .next()

    def show_vertices_edges(self):
        """Debug: in ra vertex và edge"""
        vertices = self.g.V().has("graph", self.graph_prefix).valueMap(True).toList()
        edges = self.g.E().has("graph", self.graph_prefix).valueMap(True).toList()
        print("Vertices:", vertices)
        print("Edges:", edges)
