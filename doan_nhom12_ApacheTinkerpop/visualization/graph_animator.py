# visualization/graph_animator.py
import matplotlib.pyplot as plt
import networkx as nx
import time

class GraphAnimator:
    def __init__(self, G, delay=1.0):
        self.G = G
        self.delay = delay
        self.pos = nx.spring_layout(G, seed=42)  # layout cố định
        self.fig, self.ax = plt.subplots(figsize=(8,6))
        plt.ion()  # bật interactive mode

    def draw(self, visited=None, active=None, mst_edges=None, coloring=None):
        self.ax.clear()
        node_colors = []
        for n in self.G.nodes():
            if coloring and n in coloring:
                # map màu số thành tên màu
                c = coloring[n]
                color_map = ["lightgray","lightblue","orange","yellow","pink","green","purple","cyan","brown","red"]
                node_colors.append(color_map[c % len(color_map)])
            elif active == n:
                node_colors.append("red")
            elif visited and n in visited:
                node_colors.append("lightgreen")
            else:
                node_colors.append("lightgray")

        # vẽ graph
        if isinstance(self.G, nx.DiGraph):
            nx.draw_networkx(
                self.G,
                pos=self.pos,
                ax=self.ax,
                with_labels=True,
                node_color=node_colors,
                arrows=True,
                arrowstyle='-|>',
                arrowsize=15,
                edge_color="black"
            )
        else:
            nx.draw_networkx(
                self.G,
                pos=self.pos,
                ax=self.ax,
                with_labels=True,
                node_color=node_colors,
                edge_color="black"
            )

        # vẽ MST edges nếu có
        if mst_edges:
            nx.draw_networkx_edges(
                self.G,
                self.pos,
                edgelist=mst_edges,
                edge_color="red",
                width=3
            )

        plt.pause(self.delay)

    def animate(self):
        plt.show(block=False)

    def save(self, filename):
        self.fig.savefig(filename)
