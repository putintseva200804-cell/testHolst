import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QToolBar, QAction, QPushButton, QMenu, QFileDialog, QToolButton
from PyQt5.QtGui import QPainter, QPen, QImage, QColor, QLinearGradient
from PyQt5.QtCore import Qt, QPoint, QRect

class Holst(QWidget):
    def __init__(self):
        super().__init__()

        # Создаём холст
        self.image = QImage(800, 600, QImage.Format_ARGB32)
        self.image.fill(Qt.white)

        self.last_point = QPoint()
        self.start_point = QPoint()
        self.current_point = QPoint()
        self.drawing_enabled = True

        # Настройки кисти
        self.pen_color = QColor(0, 0, 0)
        self.pen_size = 3
        self.eraser_mode = False

        # Настройки фигур
        self.current_tool = "brush"
        self.current_shape = "rectangle"
        self.shape_in_progress = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

        # Показываем предварительный контур фигуры во время растягивания
        if self.shape_in_progress:
            pen = QPen(self.pen_color, self.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            self._draw_shape(painter, self.start_point, self.current_point, self.current_shape)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing_enabled:
            self.start_point = event.pos()
            self.last_point = event.pos()
            self.current_point = event.pos()
            if self.current_tool == "fill":
                self.fill_area(event.pos())
                return
            if self.current_tool == "shape":
                self.shape_in_progress = True
                self.update()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or not self.drawing_enabled:
            return

        if self.current_tool == "shape" and self.shape_in_progress:
            self.current_point = event.pos()
            self.update()
            return

        if self.current_tool == "brush":
            painter = QPainter(self.image)
            if self.eraser_mode:
                color = QColor(255, 255, 255)
                size = self.pen_size * 5
            else:
                color = self.pen_color
                size = self.pen_size

            pen = QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()

            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton or not self.drawing_enabled:
            return

        if self.current_tool == "shape" and self.shape_in_progress:
            self.current_point = event.pos()
            painter = QPainter(self.image)
            pen = QPen(self.pen_color, self.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            self._draw_shape(painter, self.start_point, self.current_point, self.current_shape)
            painter.end()

            self.shape_in_progress = False
            self.update()

    def _draw_shape(self, painter, start, end, shape):
        """Рисует выбранную фигуру только контуром."""
        rect = QRect(start, end).normalized()

        if shape == "line":
            painter.drawLine(start, end)
        elif shape == "rectangle":
            painter.drawRect(rect)
        elif shape == "square":
            side = max(abs(end.x() - start.x()), abs(end.y() - start.y()))
            x_direction = 1 if end.x() >= start.x() else -1
            y_direction = 1 if end.y() >= start.y() else -1
            square_rect = QRect(
                start.x(),
                start.y(),
                side * x_direction,
                side * y_direction
            ).normalized()
            painter.drawRect(square_rect)
        elif shape == "ellipse":
            painter.drawEllipse(rect)
        elif shape == "circle":
            diameter = max(abs(end.x() - start.x()), abs(end.y() - start.y()))
            x_direction = 1 if end.x() >= start.x() else -1
            y_direction = 1 if end.y() >= start.y() else -1
            circle_rect = QRect(
                start.x(),
                start.y(),
                diameter * x_direction,
                diameter * y_direction
            ).normalized()
            painter.drawEllipse(circle_rect)

    def activate_brush(self):
        self.current_tool = "brush"
        self.shape_in_progress = False
        self.drawing_enabled = True
        print("Кисть активирована")

    def set_color(self, color):
        self.pen_color = color
        self.eraser_mode = False
        print(f"Цвет установлен: {color.name()}")

    def set_size(self, size):
        self.pen_size = size
        print(f"Размер кисти: {size}")

    def activate_eraser(self):
        self.current_tool = "brush"
        self.eraser_mode = True
        self.drawing_enabled = True
        self.shape_in_progress = False
        print("Ластик активирован")

    def activate_shape(self, shape):
        self.current_tool = "shape"
        self.current_shape = shape
        self.eraser_mode = False
        self.drawing_enabled = True
        self.shape_in_progress = False
        print(f"Выбрана фигура: {shape}")

    def activate_fill(self):
        self.current_tool = "fill"
        self.eraser_mode = False
        self.drawing_enabled = True
        self.shape_in_progress = False
        print("Заливка активирована")

    def fill_area(self, point):
        x, y = point.x(), point.y()
        if not (0 <= x < self.image.width() and
                0 <= y < self.image.height()):
            return
        target_color = self.image.pixelColor(x, y)
        if target_color == self.pen_color:
            return
        width = self.image.width()
        height = self.image.height()
        stack = [(x, y)]
        while stack:
            px, py = stack.pop()
            if not (0 <= px < width and 0 <= py < height):
                continue
            if self.image.pixelColor(px, py) != target_color:
                continue
            self.image.setPixelColor(px, py, self.pen_color)
            stack.append((px + 1, py))
            stack.append((px - 1, py))
            stack.append((px, py + 1))
            stack.append((px, py - 1))
        self.update()

    def clear_canvas(self):
        self.image.fill(Qt.white)
        self.shape_in_progress = False
        self.update()
        print("Холст очищен")

    def save_image(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Сохранить рисунок",
            "Мой рисунок.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if not file_name:
            return

        # Добавление расширения
        if "." not in file_name.split("/")[-1] and "." not in file_name.split("\\")[-1]:
            if "JPEG" in selected_filter:
                file_name += ".jpg"
            else:
                file_name += ".png"

        if self.image.save(file_name):
            print("Рисунок успешно сохранён!")
        else:
            print("Не удалось сохранить рисунок.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Простой Paint")
        self.setGeometry(100, 100, 800, 600)

        self.canvas = Holst()
        self.setCentralWidget(self.canvas)

        self.create_menu()
        self.create_toolbar()
        self.create_exit_button()
        self.set_theme("light")

    
    def set_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #29262B;
                }

                QMenuBar {
                    background-color: #383139;
                    color: #F8EAF0;
                    padding: 6px;
                    border-bottom: 1px solid #51434E;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 7px 12px;
                    border-radius: 6px;
                }
                QMenuBar::item:selected {
                    background-color: #594652;
                }
                QMenu {
                    background-color: #383139;
                    color: #F8EAF0;
                    border: 1px solid #594652;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 7px 24px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #594652;
                }
                QToolBar {
                    background-color: #383139;
                    border: none;
                    border-bottom: 1px solid #51434E;
                    spacing: 8px;
                    padding: 8px;
                }
                QToolButton {
                    background-color: #493D47;
                    color: #F8EAF0;
                    border: 1px solid #695461;
                    border-radius: 8px;
                    padding: 8px 12px;
                }
                QToolButton:hover {
                    background-color: #634B5B;
                }
                QPushButton {
                    background-color: #B77E9A;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 7px 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #CA91AD;
                }
                QStatusBar {
                    background-color: #383139;
                    color: #F8EAF0;
                    border-top: 1px solid #51434E;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #FFF8FA;
                }
                QMenuBar {
                    background-color: #F9E2E9;
                    color: #593D48;
                    padding: 6px;
                    border-bottom: 1px solid #EBCAD5;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 7px 12px;
                    border-radius: 6px;
                }
                QMenuBar::item:selected {
                    background-color: #F0C5D3;
                }
                QMenu {
                    background-color: #FFFAFC;
                    color: #593D48;
                    border: 1px solid #EBCAD5;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 7px 24px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #F9E2E9;
                }
                QToolBar {
                    background-color: #FCECF1;
                    border: none;
                    border-bottom: 1px solid #EBCAD5;
                    spacing: 8px;
                    padding: 8px;
                }
                QToolButton {
                    background-color: #FFF8FA;
                    color: #593D48;
                    border: 1px solid #EBCAD5;
                    border-radius: 8px;
                    padding: 8px 12px;
                }
                QToolButton:hover {
                    background-color: #F6D6E1;
                }
                QPushButton {
                    background-color: #EBC1D0;
                    color: #593D48;
                    border: none;
                    border-radius: 8px;
                    padding: 7px 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E2A9BE;
                }
                QStatusBar {
                    background-color: #F9E2E9;
                    color: #593D48;
                    border-top: 1px solid #EBCAD5;
                }
            """)


    def create_menu(self):
        menu_bar = self.menuBar()

        # Вкладка «Арина Путинцева» — исходные инструменты
        arina_menu = menu_bar.addMenu("Арина Путинцева")

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

        eraser = QAction("Ластик", self)
        eraser.triggered.connect(self.canvas.activate_eraser)
        arina_menu.addAction(eraser)

        palette_menu = QMenu("Палитра", self)
        original_colors = [
            ("Красный", QColor(255, 0, 0)),
            ("Синий", QColor(0, 0, 255)),
            ("Жёлтый", QColor(255, 255, 0)),
            ("Зелёный", QColor(0, 255, 0)),
        ]
        self._add_color_actions(palette_menu, original_colors)
        arina_menu.addMenu(palette_menu)

        # Новая вкладка «Саша Корнеич»
        sasha_menu = menu_bar.addMenu("Саша Корнеич")

        sasha_brush_menu = QMenu("Кисть", self)
        for title, size in [
            ("Тонкая (2 px)", 2),
            ("Средняя (5 px)", 5),
            ("Толстая (10 px)", 10),
        ]:
            action = QAction(title, self)
            action.triggered.connect(lambda checked=False, s=size: self.canvas.set_size(s))
            sasha_brush_menu.addAction(action)

        activate_sasha_brush = QAction("Активировать кисть", self)
        activate_sasha_brush.triggered.connect(self.canvas.activate_brush)
        sasha_brush_menu.addAction(activate_sasha_brush)
        sasha_menu.addMenu(sasha_brush_menu)

        sasha_eraser = QAction("Ластик", self)
        sasha_eraser.triggered.connect(self.canvas.activate_eraser)
        sasha_menu.addAction(sasha_eraser)


        # Цвета новой палитры не совпадают с четырьмя цветами первой вкладки
        sasha_palette_menu = QMenu("Палитра", self)
        sasha_colors = [
            ("Фиолетовый", QColor(148, 0, 211)),
            ("Оранжевый", QColor(255, 140, 0)),
            ("Розовый", QColor(255, 105, 180)),
            ("Коричневый", QColor(139, 69, 19)),
            ("Бирюзовый", QColor(0, 180, 180)),
            ("Серый", QColor(128, 128, 128)),
        ]
        self._add_color_actions(sasha_palette_menu, sasha_colors)
        sasha_menu.addMenu(sasha_palette_menu)

        # Выбор фигуры для рисования растягиванием мышью
        shapes_menu = QMenu("Фигуры", self)
        shapes = [
            ("Линия", "line"),
            ("Прямоугольник", "rectangle"),
            ("Квадрат", "square"),
            ("Эллипс", "ellipse"),
            ("Круг", "circle"),
        ]
        for title, shape_key in shapes:
            action = QAction(title, self)
            action.triggered.connect(
                lambda checked=False, shape=shape_key: self.canvas.activate_shape(shape)
            )
            shapes_menu.addAction(action)
        sasha_menu.addMenu(shapes_menu)

        # Новая вкладка «Обухова Настя»
        nastya_menu = menu_bar.addMenu("Обухова Настя")
        # Заливка цветом
        fill_action = QAction("Заливка цветом", self)
        fill_action.triggered.connect(self.canvas.activate_fill)
        nastya_menu.addAction(fill_action)
        # Очистка холста
        clear_action = QAction("Очистить холст", self)
        clear_action.triggered.connect(self.canvas.clear_canvas)
        nastya_menu.addAction(clear_action)
        # Выбор темы приложения
        theme_menu = QMenu("Выбрать тему приложения", self)
        light_theme = QAction("Светлая", self)
        light_theme.triggered.connect(
            lambda: self.set_theme("light")
        )
        theme_menu.addAction(light_theme)
        dark_theme = QAction("Темная", self)
        dark_theme.triggered.connect(
            lambda: self.set_theme("dark")
        )
        theme_menu.addAction(dark_theme)
        nastya_menu.addMenu(theme_menu)



    def _add_color_actions(self, menu, colors):
        for name, color in colors:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, selected_color=color: self.canvas.set_color(selected_color)
            )
            menu.addAction(action)

    def create_toolbar(self):
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        brush_action = QAction("Кисть", self)
        brush_action.triggered.connect(self.canvas.activate_brush)
        toolbar.addAction(brush_action)

        eraser_action = QAction("Ластик", self)
        eraser_action.triggered.connect(self.canvas.activate_eraser)
        toolbar.addAction(eraser_action)

        clear_action = QAction("Очистить холст", self)
        clear_action.triggered.connect(self.canvas.clear_canvas)
        toolbar.addAction(clear_action)

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.canvas.save_image)
        toolbar.addAction(save_action)


    def create_exit_button(self):
        exit_btn = QPushButton("Выйти")
        exit_btn.setFixedSize(100, 30)
        exit_btn.clicked.connect(self.close)

        self.statusBar().addPermanentWidget(exit_btn)
        self.statusBar().showMessage("Готово")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

