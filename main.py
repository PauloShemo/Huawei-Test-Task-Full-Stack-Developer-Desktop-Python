import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QGraphicsView,
    QGraphicsScene, QWidget, QInputDialog, QGraphicsEllipseItem, QGraphicsTextItem, QMessageBox, QGraphicsLineItem
)
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt, QPointF


class NoteGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Note Graph App")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Graphics scene and view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)  # Enable panning with right click
        self.layout.addWidget(self.view)

        # Toolbar buttons
        self.button_add_node = QPushButton("Add Node")
        self.button_add_edge = QPushButton("Add Edge")
        self.button_delete = QPushButton("Delete Item")
        self.button_save = QPushButton("Save Graph")
        self.button_load = QPushButton("Load Graph")
        self.layout.addWidget(self.button_add_node)
        self.layout.addWidget(self.button_add_edge)
        self.layout.addWidget(self.button_delete)
        self.layout.addWidget(self.button_save)
        self.layout.addWidget(self.button_load)

        # Button actions
        self.button_add_node.clicked.connect(self.add_node)
        self.button_add_edge.clicked.connect(self.add_edge)
        self.button_delete.clicked.connect(self.delete_item)
        self.button_save.clicked.connect(self.save_graph)
        self.button_load.clicked.connect(self.load_graph)

        # Data structures for nodes and edges
        self.nodes = []
        self.edges = []

    def add_node(self):
        text, ok = QInputDialog.getText(self, "Add Note", "Enter note text (max 128 characters):")
        if ok and text.strip():
            if len(text) > 128:
                QMessageBox.warning(self, "Warning", "Text exceeds 128 characters!")
                return

            # Calculate size of node based on text length
            text_width = max(60, len(text) * 7)
            node = QGraphicsEllipseItem(-text_width // 2, -30, text_width, 60)
            node.setBrush(QBrush(Qt.yellow))
            node.setFlag(QGraphicsEllipseItem.ItemIsMovable)
            node.setFlag(QGraphicsEllipseItem.ItemIsSelectable)

            text_item = QGraphicsTextItem(text, node)
            text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
            text_item.setDefaultTextColor(Qt.black)

            self.scene.addItem(node)
            self.nodes.append(node)

    def add_edge(self):
        selected_items = [item for item in self.scene.selectedItems() if isinstance(item, QGraphicsEllipseItem)]
        if len(selected_items) != 2:
            QMessageBox.warning(self, "Warning", "Select exactly two nodes to connect!")
            return

        # Create a line between two selected nodes
        pos1 = selected_items[0].scenePos()
        pos2 = selected_items[1].scenePos()

        line = self.scene.addLine(pos1.x(), pos1.y(), pos2.x(), pos2.y(), QPen(Qt.black))
        line.setFlag(line.ItemIsSelectable)  # Allow the edge to be selectable
        self.edges.append(line)

    def delete_item(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)
            if isinstance(item, QGraphicsEllipseItem) and item in self.nodes:
                self.nodes.remove(item)
            elif isinstance(item, QGraphicsLineItem) and item in self.edges:
                self.edges.remove(item)

    def save_graph(self):
        data = {"nodes": [], "edges": []}

        # Save nodes
        for node in self.nodes:
            pos = node.scenePos()
            text_item = node.childItems()[0]
            data["nodes"].append({
                "x": pos.x(),
                "y": pos.y(),
                "text": text_item.toPlainText()
            })

        # Save edges
        for edge in self.edges:
            source_node, target_node = None, None
            for node in self.nodes:
                if edge.line().p1() == node.scenePos():
                    source_node = node
                if edge.line().p2() == node.scenePos():
                    target_node = node
            if source_node and target_node:
                source_index = self.nodes.index(source_node)
                target_index = self.nodes.index(target_node)
                data["edges"].append((source_index, target_index))

        with open("graph.json", "w") as file:
            json.dump(data, file)
        QMessageBox.information(self, "Info", "Graph saved successfully!")

    def load_graph(self):
        try:
            with open("graph.json", "r") as file:
                data = json.load(file)

            self.scene.clear()
            self.nodes = []
            self.edges = []

            # Load nodes
            for node_data in data["nodes"]:
                self.add_node_at_position(node_data["x"], node_data["y"], node_data["text"])

            # Load edges
            for source_index, target_index in data["edges"]:
                source = self.nodes[source_index]
                target = self.nodes[target_index]
                self.add_edge_between_nodes(source, target)

        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", "No saved graph found!")

    def add_node_at_position(self, x, y, text):
        text_width = max(60, len(text) * 7)
        node = QGraphicsEllipseItem(-text_width // 8, -30, text_width, 80)
        node.setBrush(QBrush(Qt.yellow))
        node.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        node.setFlag(QGraphicsEllipseItem.ItemIsSelectable)

        text_item = QGraphicsTextItem(text, node)
        text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        text_item.setDefaultTextColor(Qt.black)

        node.setPos(x, y)
        self.scene.addItem(node)
        self.nodes.append(node)

    def add_edge_between_nodes(self, source, target):
        pos1 = source.scenePos()
        pos2 = target.scenePos()
        line = self.scene.addLine(pos1.x(), pos1.y(), pos2.x(), pos2.y(), QPen(Qt.black))
        line.setFlag(line.ItemIsSelectable)
        self.edges.append(line)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteGraphApp()
    window.show()
    sys.exit(app.exec_())
