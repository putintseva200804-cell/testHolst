import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QToolBar, QAction, QPushButton
from PyQt5.QtGui import QPainter, QPen, QImage, QColor
from PyQt5.QtCore import Qt, QPoint


class Holst(QWidget):
    
    def __init__(self):
        super().__init__()
        #создаем холст со своими характеристиками
        self.image = QImage(800, 600, QImage.Format_ARGB32)
        self.image.fill(Qt.white)
        
        self.last_point = QPoint()
        self.drawing_enabled = True  

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)
        #метод, отслеживающий нажатие ЛКМ
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing_enabled:
            self.last_point = event.pos()

    def mouseMoveEvent(self, event): #метод, отслеживающий движение мыши
        if (event.buttons() & Qt.LeftButton) and self.drawing_enabled:
            painter = QPainter(self.image)
            pen = QPen(QColor(0, 0, 0), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()
            
            self.last_point = event.pos()
            self.update()
            #проверка, выбранаа ли кисть на панели инструментов
    def activate_brush(self):
        self.drawing_enabled = True
        print("Кисть активирована")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Простой Paint")
        self.setGeometry(100, 100, 800, 600)

        self.canvas = Holst()
        self.setCentralWidget(self.canvas)

        #создал панель инструментов сверху
        self.create_toolbar()

        #создал кнопкку выхода из приложения
        self.create_exit_button()

        #функции панели инструментов и кисти
    def create_toolbar(self):
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        #когда будет нажата кнопкаа "кисть" на панели то вызовется этот метод
        brush_action = QAction("Кисть", self)
        brush_action.triggered.connect(self.canvas.activate_brush)
        toolbar.addAction(brush_action)

        #функции и описание кнопки выхода
    def create_exit_button(self):
        exit_btn = QPushButton("Выйти")
        exit_btn.setFixedSize(100, 30)
        exit_btn.clicked.connect(self.close)
        
        self.statusBar().addPermanentWidget(exit_btn)
        self.statusBar().showMessage("Готово")

        #проверка точки входа
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
     
