from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel,
    QComboBox, QLineEdit,
    QGroupBox, QRadioButton
)
import os
import json
import networkx as nx
from visualization.graph_animator import GraphAnimator
from algorithms.gremlin_controller import AlgorithmController

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.G = None
        self.visualizer = None
        self.controller = None
        self.graph_loaded = False
        self.updating_ui = False  # ⭐ chống signal lồng nhau

        self.setWindowTitle("Graph Algorithms Visualizer")
        self.setGeometry(200, 150, 1000, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        left = QVBoxLayout()

        self.vertex_input = QLineEdit()
        self.vertex_input.setPlaceholderText("Nhập đỉnh (VD: A B C)")

        self.edge_input = QTextEdit()
        self.edge_input.setPlaceholderText("Nhập cạnh, mỗi dòng:\nA B\nA B 3")

        # ===== Data source =====
        source_box = QGroupBox("Nguồn dữ liệu đồ thị")
        source_layout = QVBoxLayout()

        self.radio_manual = QRadioButton("Nhập tay")
        self.radio_data = QRadioButton("Dữ liệu mẫu (data/)")
        self.radio_manual.setChecked(True)

        self.radio_manual.toggled.connect(self.update_data_source_ui)
        self.radio_data.toggled.connect(self.update_data_source_ui)

        self.data_combo = QComboBox()
        self.load_data_files()

        self.load_btn = QPushButton("Load graph mẫu")
        self.load_btn.clicked.connect(self.load_graph_from_file)

        source_layout.addWidget(self.radio_manual)
        source_layout.addWidget(self.radio_data)
        source_layout.addWidget(self.data_combo)
        source_layout.addWidget(self.load_btn)
        source_box.setLayout(source_layout)

        self.graph_type = QComboBox()
        self.graph_type.addItems([
            "Vô hướng",
            "Có hướng",
            "Vô hướng + trọng số",
            "Có hướng + trọng số"
        ])

        self.algorithm = QComboBox()
        self.algorithm.addItems([
            "DFS", "BFS",
            "Dijkstra", "Bellman-Ford",
            "Prim", "Kruskal",
            "Graph Coloring"
        ])

        self.run_btn = QPushButton("Chạy thuật toán")
        self.run_btn.clicked.connect(self.run_algorithm)
        self.run_btn.setEnabled(False)

        self.status = QTextEdit()
        self.status.setReadOnly(True)

        left.addWidget(source_box)
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

        main_layout.addLayout(left)
        self.setLayout(main_layout)

        self.update_data_source_ui()

    # ================= DATA =================
    def load_data_files(self):
        self.data_combo.clear()
        os.makedirs(DATA_DIR, exist_ok=True)
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
        self.data_combo.addItems(files)

    def update_data_source_ui(self):
        use_data = self.radio_data.isChecked()

        self.data_combo.setEnabled(use_data)
        self.load_btn.setEnabled(use_data)

        # khóa / mở input
        self.vertex_input.setEnabled(not use_data)
        self.edge_input.setEnabled(not use_data)

        if use_data:
            self.load_data_files()   # ⭐ reload file mỗi lần chọn
            self.graph_loaded = False
            self.run_btn.setEnabled(False)
            self.status.append("ℹ Đã chọn nguồn: Dữ liệu mẫu")
        else:
            self.graph_loaded = True
            self.run_btn.setEnabled(True)
            self.status.append("ℹ Đã chọn nguồn: Nhập tay")

    def load_graph_from_file(self):
        if self.updating_ui:
            return

        filename = self.data_combo.currentText()
        if not filename:
            self.status.append("⚠ Không có file dữ liệu")
            return

        path = os.path.join(DATA_DIR, filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.updating_ui = True
            self.blockSignals(True)

            self.vertex_input.setText(" ".join(data.get("vertices", [])))
            self.edge_input.clear()
            for e in data.get("edges", []):
                self.edge_input.append(" ".join(map(str, e)))

            directed = data.get("directed", False)
            weighted = data.get("weighted", False)

            if directed and weighted:
                self.graph_type.setCurrentIndex(3)
            elif directed:
                self.graph_type.setCurrentIndex(1)
            elif weighted:
                self.graph_type.setCurrentIndex(2)
            else:
                self.graph_type.setCurrentIndex(0)

            self.blockSignals(False)
            self.updating_ui = False

            self.graph_loaded = True
            self.run_btn.setEnabled(True)

            self.status.append("✅ Đã load dữ liệu đồ thị mẫu")
            self.status.append(f"📄 File: {data.get('name', filename)}")
            self.status.append("👉 Chọn thuật toán và bấm 'Chạy thuật toán'")

        except Exception as e:
            self.blockSignals(False)
            self.updating_ui = False
            self.status.append(f"❌ Lỗi load dữ liệu: {e}")

    # ================= RUN =================
    def run_algorithm(self):
        if not self.graph_loaded:
            self.status.append("⚠ Vui lòng load đồ thị trước")
            return

        vertices = self.vertex_input.text().split()
        edges = []

        for line in self.edge_input.toPlainText().splitlines():
            p = line.split()
            if len(p) >= 2:
                edges.append(p)

        directed = "Có hướng" in self.graph_type.currentText()
        weighted = "trọng số" in self.graph_type.currentText()

        self.G = nx.DiGraph() if directed else nx.Graph()

        for v in vertices:
            self.G.add_node(v)

        for e in edges:
            u, v = e[0], e[1]
            w = float(e[2]) if weighted and len(e) == 3 else 1.0
            self.G.add_edge(u, v, weight=w)

        self.visualizer = GraphAnimator(self.G)
        self.controller = AlgorithmController(self.G, self.status, self.visualizer)

        self.controller.run(self.algorithm.currentText(), vertices[0])
