# ui/main_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel,
    QComboBox, QLineEdit
)
import networkx as nx
from visualization.graph_animator import GraphAnimator
from algorithms.gremlin_controller import AlgorithmController  # controller dùng GraphAnimator

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Backend
        self.G = None
        self.visualizer = None
        self.controller = None

        # UI
        self.setWindowTitle("Graph Algorithms Visualizer - NetworkX")
        self.setGeometry(200, 150, 1000, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        left = QVBoxLayout()

        self.vertex_input = QLineEdit()
        self.vertex_input.setPlaceholderText("Nhập đỉnh (VD: A B C)")

        self.edge_input = QTextEdit()
        self.edge_input.setPlaceholderText(
            "Nhập cạnh, mỗi dòng:\nA B\nA B 3 (có trọng số)"
        )

        self.graph_type = QComboBox()
        self.graph_type.addItems([
            "Có hướng", "Vô hướng",
            "Có hướng + trọng số", "Vô hướng + trọng số"
        ])

        self.algorithm = QComboBox()
        self.algorithm.addItems([
            "DFS", "BFS", "Dijkstra", "Bellman-Ford",
            "Prim", "Kruskal", "Graph Coloring"
        ])

        self.run_btn = QPushButton("Chạy thuật toán")
        self.run_btn.clicked.connect(self.run_algorithm)

        self.status = QTextEdit()
        self.status.setReadOnly(True)

        left.addWidget(QLabel("Danh sách đỉnh"))
        left.addWidget(self.vertex_input)
        left.addWidget(QLabel("Danh sách cạnh"))
        left.addWidget(self.edge_input)
        left.addWidget(QLabel("Loại đồ thị"))
        left.addWidget(self.graph_type)
        left.addWidget(QLabel("Thuật toán"))
        left.addWidget(self.algorithm)
        left.addWidget(self.run_btn)
        left.addWidget(QLabel("Log thuật toán"))
        left.addWidget(self.status)

        main_layout.addLayout(left, 2)
        self.setLayout(main_layout)

    def run_algorithm(self):
        self.status.clear()
        vertices = self.vertex_input.text().strip().split()
        if not vertices:
            self.status.append("⚠ Vui lòng nhập ít nhất 1 đỉnh")
            return

        edges = []
        for line in self.edge_input.toPlainText().splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                edges.append(parts)

        directed = "Có hướng" in self.graph_type.currentText()
        weighted = "trọng số" in self.graph_type.currentText()

        # Build graph NetworkX
        if directed:
            self.G = nx.DiGraph()
        else:
            self.G = nx.Graph()

        for v in vertices:
            self.G.add_node(v)

        for e in edges:
            u, v = e[0], e[1]
            w = float(e[2]) if weighted and len(e) == 3 else 1.0
            self.G.add_edge(u, v, weight=w)

        self.status.append("✅ Graph đã được tạo")

        # Build visualizer
        self.visualizer = GraphAnimator(self.G)

        # Build controller
        self.controller = AlgorithmController(self.G, self.status, self.visualizer)

        # Run algorithm
        algo = self.algorithm.currentText()
        start_vertex = vertices[0]  # mặc định đỉnh đầu
        try:
            self.controller.run(algo, start_vertex)
        except Exception as e:
            self.status.append(f"❌ Lỗi chạy thuật toán {algo}: {e}")
