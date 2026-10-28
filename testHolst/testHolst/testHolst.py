import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QToolBar, QAction, QPushButton, QMenu  # 2 коммит добавлен QMenu
from PyQt5.QtGui import QPainter, QPen, QImage, QColor
from PyQt5.QtCore import Qt, QPoint


class Holst(QWidget):

    def __init__(self):
        super().__init__()
        # создаем холст со своими характеристиками
        self.image = QImage(800, 600, QImage.Format_ARGB32)
        self.image.fill(Qt.white)

        self.last_point = QPoint()
        self.drawing_enabled = True

        # 2 коммит: параметры рисования - цвет, толщина, ластик
        self.pen_color = QColor(0, 0, 0)
        self.pen_size = 3
        self.eraser_mode = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    # метод, отслеживающий нажатие ЛКМ
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing_enabled:
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):  # метод, отслеживающий движение мыши
        if (event.buttons() & Qt.LeftButton) and self.drawing_enabled:
            painter = QPainter(self.image)

            # 2 коммит: выбор цвета и толщины в зависимости от режима ластика
            if self.eraser_mode:
                color = QColor(255, 255, 255)
                size = self.pen_size * 5
            else:
                color = self.pen_color
                size = self.pen_size

            pen = QPen(color, size, Qt.SolidLine, Qt.RoundCap,
                       Qt.RoundJoin)  # 2 коммит: color и size
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()

            self.last_point = event.pos()
            self.update()

    # проверка, выбранаа ли кисть на панели инструментов
    def activate_brush(self):
        self.drawing_enabled = True
        print("Кисть активирована")

    # 2 коммитустановка цвета кисти
    def set_color(self, color):
        self.pen_color = color
        self.eraser_mode = False
        print(f"Цвет установлен: {color.name()}")

    # 2 коммит толщина кисти
    def set_size(self, size):
        self.pen_size = size
        print(f"Размер кисти: {size}")

    # 2 коммит режим ластика
    def activate_eraser(self):
        self.eraser_mode = True
        self.drawing_enabled = True
        print("Ластик активирован")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Простой Paint")
        self.setGeometry(100, 100, 800, 600)

        self.canvas = Holst()
        self.setCentralWidget(self.canvas)

        self.create_menu()  # 2 коммит вызов создания меню
        self.create_toolbar()

        # создал кнопкку выхода из приложения
        self.create_exit_button()

    # 2 коммит новый метод вкладка «Арина Путинцева» с кистью, ластиком и палитройиз 4 цветов
    def create_menu(self):
        menu_bar = self.menuBar()
        arina_menu = menu_bar.addMenu("Арина Путинцева")

        #кисть с подменю из 3 размеров
        # lambda короткая безымянная функция
        brush_menu = QMenu("Кисть", self)

        thin = QAction("Тонкая (2 px)", self)
        thin.triggered.connect(lambda: self.canvas.set_size(2))
        brush_menu.addAction(thin)

        medium = QAction("Средняя (5 px)", self)
        medium.triggered.connect(lambda: self.canvas.set_size(5))
        brush_menu.addAction(medium)

        thick = QAction("Толстая (10 px)", self)
        thick.triggered.connect(lambda: self.canvas.set_size(10))
        brush_menu.addAction(thick)

        activate_brush = QAction("Активировать кисть", self)
        activate_brush.triggered.connect(self.canvas.activate_brush)
        brush_menu.addAction(activate_brush)

        arina_menu.addMenu(brush_menu)

        # --- Ластик ---
        eraser = QAction("Ластик", self)
        eraser.triggered.connect(self.canvas.activate_eraser)
        arina_menu.addAction(eraser)

        # --- Палитра из 4 цветов ---
        palette_menu = QMenu("Палитра", self)
        colors = [
            ("Красный", QColor(255, 0, 0)),
            ("Синий", QColor(0, 0, 255)),
            ("Жёлтый", QColor(255, 255, 0)),
            ("Зелёный", QColor(0, 255, 0)),
        ]
        for name, color in colors:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, c=color: self.canvas.set_color(c))
            palette_menu.addAction(action)

        arina_menu.addMenu(palette_menu)

    # функции панели инструментов и кисти
    def create_toolbar(self):
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        # когда будет нажата кнопкаа "кисть" на панели то вызовется этот метод
        brush_action = QAction("Кисть", self)
        brush_action.triggered.connect(self.canvas.activate_brush)
        toolbar.addAction(brush_action)

    # функции и описание кнопки выхода
    def create_exit_button(self):
        exit_btn = QPushButton("Выйти")
        exit_btn.setFixedSize(100, 30)
        exit_btn.clicked.connect(self.close)

        self.statusBar().addPermanentWidget(exit_btn)
        self.statusBar().showMessage("Готово")

        # проверка точки входа


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())