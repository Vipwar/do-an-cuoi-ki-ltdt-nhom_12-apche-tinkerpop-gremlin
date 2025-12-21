# gremlin_connection.py
from gremlin_python.driver import client, serializer

class GremlinManager:
    def get_vertices(self):
        # trả về danh sách tên đỉnh từ Gremlin
        return ["A","B","C","D"]

    def get_edges(self):
        # trả về danh sách cạnh (u,v,w) từ Gremlin
        return [("A","B",1), ("B","C",2), ("C","D",3), ("D","A",4), ("A","C",2)]

class GremlinManager:
    def __init__(self, url="ws://localhost:8182/gremlin", graph_name="g"):
        self.url = url
        self.client = client.Client(
            self.url, 'g',
            message_serializer=serializer.GraphSONSerializersV2d0()
        )
        self.graph_name = graph_name

    # ================== Vertex ==================
    def add_vertex(self, v_id):
        script = f"g.V('{v_id}').fold().coalesce(unfold(), addV('{v_id}'))"
        self.client.submit(script).all().result()

    def get_vertices(self):
        script = "g.V().id()"
        result = self.client.submit(script).all().result()
        return list(result)
    

    # ================== Edge ==================
    def add_edge(self, u, v, weight=1.0):
        script = (
            f"g.V('{u}').as('a').V('{v}').as('b')"
            f".coalesce(__.outE().where(__.inV().is(b)), __.addE('edge').from('a').to('b').property('weight',{weight}))"
        )
        self.client.submit(script).all().result()

    def get_edges(self):
        # Lấy tất cả các cạnh dưới dạng (u, v, weight)
        script = "g.E().project('u','v','w').by(outV().id()).by(inV().id()).by('weight')"
        result = self.client.submit(script).all().result()
        edges = []
        for r in result:
            u = r['u']
            v = r['v']
            w = r.get('w', 1.0)
            edges.append((u, v, w))
        return edges

    # ================== Clear Graph ==================
    def clear_graph(self):
        self.client.submit("g.V().drop()").all().result()

    # ================== Close connection ==================
    def close(self):
        self.client.close()
