# algorithms/controller_animator.py
import heapq
from collections import deque


class AlgorithmController:
    def __init__(self, G, status_widget, visualizer=None):
        self.G = G
        self.status = status_widget   # QTextEdit
        self.vis = visualizer


    # ================== DFS ==================
    def dfs(self, start):
        visited = set()
        self.status.append("=== DFS ===")
        def _dfs(v):
            if v in visited:
                return
            visited.add(v)
            self.status.append(f"DFS thăm: {v}")
            if self.vis:
                self.vis.draw(visited=visited, active=v)
            for n in self.G.neighbors(v):
                _dfs(n)
        _dfs(start)
        if self.vis:
            self.vis.draw(visited=visited)


    # ================== BFS ==================
    def bfs(self, start):
        visited = {start}
        queue = deque([start])
        self.status.append("=== BFS ===")
        while queue:
            v = queue.popleft()
            self.status.append(f"BFS thăm: {v}")
            if self.vis:
                self.vis.draw(visited=visited, active=v)
            for n in self.G.neighbors(v):
                if n not in visited:
                    visited.add(n)
                    queue.append(n)
        if self.vis:
            self.vis.draw(visited=visited)


    # ================== Dijkstra ==================
    def dijkstra(self, start):
        dist = {v: float("inf") for v in self.G.nodes()}
        dist[start] = 0
        pq = [(0, start)]
        self.status.append("=== Dijkstra ===")
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            self.status.append(f"Chọn đỉnh {u}, khoảng cách = {dist[u]}")
            if self.vis:
                self.vis.draw(visited=set(dist.keys()), active=u)
            for v in self.G.neighbors(u):
                w = self.G[u][v].get("weight", 1.0)
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    heapq.heappush(pq, (dist[v], v))
        self.status.append("=== Dijkstra kết thúc ===")
        if self.vis:
            self.vis.draw()


    # ================== Bellman-Ford ==================
    def bellman_ford(self, start):
        vertices = list(self.G.nodes())
        dist = {v: float("inf") for v in vertices}
        dist[start] = 0
        edges = [(u, v, self.G[u][v].get("weight",1.0)) for u,v in self.G.edges()]
        self.status.append("=== Bellman-Ford ===")
        for i in range(len(vertices)-1):
            self.status.append(f"Vòng lặp {i+1}")
            updated = False
            for u,v,w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    updated = True
                    self.status.append(f"  Relax {u}->{v}, dist={dist[v]}")
                    if self.vis:
                        self.vis.draw(active=v)
            if not updated:
                break
        for u,v,w in edges:
            if dist[u] + w < dist[v]:
                self.status.append("⚠ Phát hiện chu trình âm")
                return
        self.status.append("=== Bellman-Ford kết thúc ===")
        if self.vis:
            self.vis.draw()


    # ================== Prim ==================
    def prim(self, start):
        visited = {start}
        pq = []
        mst_edges = []
        self.status.append("=== Prim (MST) ===")
        self.status.append(f"Bắt đầu từ đỉnh {start}")


        def push_edges(u):
            for v in self.G.neighbors(u):
                if v not in visited:
                    w = self.G[u][v].get("weight",1.0)
                    heapq.heappush(pq, (w,u,v))
        push_edges(start)
        while pq:
            w,u,v = heapq.heappop(pq)
            if v in visited:
                continue
            visited.add(v)
            mst_edges.append((u,v))
            self.status.append(f"Chọn cạnh {u}-{v} (w={w})")
            if self.vis:
                self.vis.draw(mst_edges=mst_edges)
            push_edges(v)
        total = sum(self.G[u][v].get("weight",1.0) for u,v in mst_edges)
        self.status.append(f"Tổng trọng số MST = {total}")
        if self.vis:
            self.vis.draw(mst_edges=mst_edges)


    # ================== Kruskal ==================
    def kruskal(self):
        parent = {}
        def find(x):
            if parent[x]!=x:
                parent[x]=find(parent[x])
            return parent[x]
        def union(a,b):
            ra,rb=find(a),find(b)
            if ra!=rb:
                parent[rb]=ra
                return True
            return False
        vertices = list(self.G.nodes())
        for v in vertices:
            parent[v]=v
        edges = [(u,v,self.G[u][v].get("weight",1.0)) for u,v in self.G.edges()]
        edges.sort(key=lambda x:x[2])
        mst=[]
        self.status.append("=== Kruskal (MST) ===")
        for u,v,w in edges:
            if union(u,v):
                mst.append((u,v))
                self.status.append(f"Chọn cạnh {u}-{v} (w={w})")
                if self.vis:
                    self.vis.draw(mst_edges=mst)
        total = sum(self.G[u][v].get("weight",1.0) for u,v in mst)
        self.status.append(f"Tổng trọng số MST = {total}")
        if self.vis:
            self.vis.draw(mst_edges=mst)


    # ================== Graph Coloring ==================
    def graph_coloring(self):
        colors = {}
        self.status.append("=== Graph Coloring ===")
        for v in self.G.nodes():
            used = {colors[n] for n in self.G.neighbors(v) if n in colors}
            c = 1
            while c in used:
                c += 1
            colors[v] = c
            self.status.append(f"Đỉnh {v} → màu {c}")
            if self.vis:
                self.vis.draw(coloring=colors)
        self.status.append(f"Số màu sử dụng: {len(set(colors.values()))}")
        if self.vis:
            self.vis.draw(coloring=colors)


    # ================== Run general ==================
    def run(self, algo_name, start_vertex=None):
        if algo_name=="DFS":
            if not start_vertex: return self.status.append("DFS cần đỉnh bắt đầu")
            self.dfs(start_vertex)
        elif algo_name=="BFS":
            if not start_vertex: return self.status.append("BFS cần đỉnh bắt đầu")
            self.bfs(start_vertex)
        elif algo_name=="Dijkstra":
            if not start_vertex: return self.status.append("Dijkstra cần đỉnh bắt đầu")
            self.dijkstra(start_vertex)
        elif algo_name=="Bellman-Ford":
            if not start_vertex: return self.status.append("Bellman-Ford cần đỉnh bắt đầu")
            self.bellman_ford(start_vertex)
        elif algo_name=="Prim":
            if not start_vertex: return self.status.append("Prim cần đỉnh bắt đầu")
            self.prim(start_vertex)
        elif algo_name=="Kruskal":
            self.kruskal()
        elif algo_name=="Graph Coloring":
            self.graph_coloring()
        else:
            self.status.append("Thuật toán chưa được triển khai")



