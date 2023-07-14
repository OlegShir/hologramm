from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QPointF, QRectF, QLineF
from PyQt5.QtGui import QPainter, QPixmap, QImage, QPen, QFont
from modules.massager import MSGLabel
from PIL import Image, ImageEnhance
import math
Image.MAX_IMAGE_PIXELS = None


class ImageAnalizator(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageAnalizator, self).__init__(parent)

        self.setEnabled(False)
        # Create a scene for displaying images
        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)
        self.setGeometry(580, 30, 516, 350)
        # ограничители масштабирования
        self.min_ratio: float
        self.max_ratio: float
        # размер изображения в px
        self.xsize_RLI_pixmap: int
        self.ysize_RLI_pixmap: int
        # инициализация ссылки обработку изображения
        self.msg: MSGLabel
        # инициализация работы с метками ЧКП
        self.pixmap_item = QGraphicsPixmapItem()
        self.graphics_scene.addItem(self.pixmap_item)
        # инициализация масштаба
        self.scale_factor: float = 1.0
        # инициализация позиция мыши и размера 
        self.initial_pos: QPoint

        # начальные параметры изображения
        self.brightness_value = 1.0
        self.contrast_value = 1.0
        self.exp_value = 1.0

        # переменные для измерения расстояния
        self.point1_item = QGraphicsEllipseItem()
        self.point2_item = QGraphicsEllipseItem()
        self.line_item = QGraphicsLineItem()
        self.distance_text_item = QGraphicsTextItem()
        self.dragging_point_index = 0
        self.point_radius = 5
        self.ruler = False
        self.coef_px_to_meters:float
        self.star_ruler: bool = False

        # Enable zooming
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def set_link(self, table, msg: MSGLabel) -> None:
        self.table = table
        self.msg = msg
    
    def set_coef_px_to_meters(self, coef_px_to_meters: list) -> None:
        # получение коэффициента перевода пикселей в метры
        self.coef_px_to_meters, _ = coef_px_to_meters
    
    def wheelEvent(self, event):
        # Handle mouse wheel event for zooming
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.2
        else:
            self.scale_factor /= 1.2 

        # Ограничение масштабирования
        self.scale_factor = max(min(self.scale_factor, self.max_ratio), self.min_ratio)
     
        # масштабирование РЛИ
        self.resetTransform()
        self.scale(self.scale_factor, self.scale_factor)

        # Обновление размера элементов линейки
        if self.ruler:
            self.update_ruler(update_size=True)

    def mousePressEvent(self, event):
        # Handle mouse press event for moving the image
        self.initial_pos = event.pos()
        item_pos = self.mapToScene(event.pos()).toPoint()

        # проверяет нажатие на точки
        if self.ruler and self.star_ruler:
            if self.cross_cursor(self.point1_item.pos().toPoint(), item_pos, self.point_radius, round(5/self.scale_factor)):
                if event.buttons() == Qt.LeftButton: # type: ignore
                    # Нажатие произошло на первую точку
                    self.dragging_point_index = 1
                else:
                    self.ruler_clear()
            elif self.cross_cursor(self.point2_item.pos().toPoint(), item_pos, self.point_radius, round(5/self.scale_factor)):
                if event.buttons() == Qt.LeftButton: # type: ignore
                    # Нажатие произошло на вторую точку
                    self.dragging_point_index = 2
                else:
                    self.ruler_clear()
            else:
                self.dragging_point_index = 0

        super(ImageAnalizator, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        # Handle mouse move event for moving the image
        if event.buttons() == Qt.LeftButton: # type: ignore 

            if self.dragging_point_index:
                # Отключаем передвижение для картинки и меняем курсор
                self.setDragMode(QGraphicsView.NoDrag)
                self.setCursor(Qt.CrossCursor) # type: ignore
                new_item_pos = self.mapToScene(event.pos()).toPoint()
                # Обновление линии точек
                if self.dragging_point_index == 1:
                    self.point1_item.setPos(new_item_pos)
                elif self.dragging_point_index == 2:
                    self.point2_item.setPos(new_item_pos)
                # Обновление отображаемого расстояния
                self.update_ruler(update_position=True)

                event.accept()
            
            if not self.dragging_point_index:

                delta = event.pos() - self.initial_pos
                target_pos = self.viewport().pos() - delta
                animation = QPropertyAnimation(self.viewport(), b"pos")
                animation.setDuration(200)  # Длительность анимации в миллисекундах
                animation.setStartValue(self.viewport().pos())
                animation.setEndValue(target_pos)
                animation.start()

                event.accept()
        
        super(ImageAnalizator, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        # Включаем передвижение для картинки и возвращаем курсор
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setCursor(Qt.OpenHandCursor) # type: ignore
      
        if event.pos() == self.initial_pos and event.button() == Qt.LeftButton: # type: ignore 
            # получение координат пикселей места нажатия
            item_pos = self.mapToScene(event.pos()).toPoint()
            if self.star_ruler:
                if self.point1_item in self.graphics_scene.items() and not self.ruler:
                    # Если уже есть первая точка, то это будет вторая точка
                    # Отображаем второй точки как красный круг
                    self.graphics_scene.addItem(self.point2_item)
                    self.point2_item.setPos(item_pos)
                    self.point2_item.setBrush(Qt.red) # type: ignore
                    # Добавление остальных элементов на сцену
                    self.graphics_scene.addItem(self.line_item)
                    self.graphics_scene.addItem(self.distance_text_item)
                    self.distance_text_item.setDefaultTextColor(Qt.red) # type: ignore
                    # Обновление элементов
                    self.update_ruler(update_position=True, update_size=True)
                    # устанавливаем что линейка установлена
                    self.ruler = True
                else:
                    if self.ruler:
                        # очистка сцены
                        self.ruler_clear()
                    # Если первая точка еще не установлена, то это будет первая точка
                    # Отображаем первую точку как красный круг
                    self.graphics_scene.addItem(self.point1_item)
                    self.point1_item.setPos(item_pos)
                    self.point1_item.setRect(QRectF(- self.point_radius/self.scale_factor,
                                                    - self.point_radius/self.scale_factor, 
                                                    (self.point_radius*2)/self.scale_factor, 
                                                    (self.point_radius*2)/self.scale_factor))
                    self.point1_item.setBrush(Qt.red) # type: ignore

        elif event.button() == Qt.RightButton: # type: ignore
            # получение координат пикселей места нажатия
            item_pos = self.mapToScene(event.pos())

        super(ImageAnalizator, self).mouseReleaseEvent(event)

    def get_limit_ratio(self) -> tuple:

        x_ratio = self.size().width() / self.image_width
        y_ratio = self.size().height()/ self.image_height

        return max(x_ratio, y_ratio), min(1/x_ratio, 1/y_ratio)
   
    def open_file(self, path_to_img):
        # открытие изображения
        self.image = Image.open(path_to_img)
        # Преобразование изображения в режим "L" (градации серого)
        self.image = self.image.convert("L")
        self.image_width, self.image_height = self.image.size
        self.copy_image = self.image.copy()
        
        self.setEnabled(True)
        # загрузка изображения на просмотр
        self.update_display_image()
        self.min_ratio, self.max_ratio = self.get_limit_ratio()

    def update_display_image(self):
        # Преобразование изображения PIL в QImage
        image_qt = QImage(self.copy_image.tobytes(), self.image_width, self.image_height, self.image_width, QImage.Format_Grayscale8)
        # Создание QPixmap из QImage
        image = QPixmap.fromImage(image_qt)
        # Установка изображения в ImageView
        self.pixmap_item.setPixmap(image)
        

    def adjust_image(self, contrast_value, brightness_value, exp_value):
        
        # Изменение контраста
        contrast_enhancer = ImageEnhance.Contrast(self.image)
        adjusted_image = contrast_enhancer.enhance(contrast_value)

        # Изменение яркости
        brightness_enhancer = ImageEnhance.Brightness(adjusted_image)
        adjusted_image = brightness_enhancer.enhance(brightness_value)

        # Изменение резкости
        sharpness_enhancer = ImageEnhance.Sharpness(adjusted_image)
        self.copy_image = sharpness_enhancer.enhance(exp_value)
        
        self.update_display_image()
 
    # -----------------Функции управления и изменение линейки--------------

    def update_ruler(self, update_size:bool = False, update_position:bool = False) -> None:
        """Функция изменения параметров линейки.
           Объекты точки добавлены на сцену.
           update_size - меняется только размер в соответствии с scale_factor;
           update_position - только позиция."""
        if update_position:
            # Рисуем линию между двумя точками
            self.line_item.setLine(QLineF(self.point1_item.pos(), self.point2_item.pos()))
            # Вычисляем и отображаем расстояние между точками
            distance = self.calculate_distance(self.point1_item.pos(), self.point2_item.pos())
            self.distance_text_item.setPlainText(f"{distance:.2f} м.")
            self.distance_text_item.setPos(self.point2_item.pos())
        if update_size:
            # Установка толщины линии
            pen = QPen(Qt.red) # type: ignore
            pen.setWidth(round(1/self.scale_factor))  # Установка толщины линии в пикселях
            self.line_item.setPen(pen) # type: ignore
            self.distance_text_item.setFont(QFont("Arial", round(14/self.scale_factor)))
            rect = QRectF(- self.point_radius/self.scale_factor,
                          - self.point_radius/self.scale_factor, 
                          (self.point_radius*2)/self.scale_factor, 
                          (self.point_radius*2)/self.scale_factor)
            
            self.point1_item.setRect(rect)
            self.point2_item.setRect(rect)

    def ruler_clear(self)->None:
        # функция очищает сцену от элементов линейки
        stack = [self.point1_item, self.point2_item, self.line_item, self.distance_text_item]
        for item in stack:
            if item in self.graphics_scene.items():
                self.graphics_scene.removeItem(item)
        # self.graphics_scene.removeItem(self.point1_item)
        # self.graphics_scene.removeItem(self.point2_item)
        # self.graphics_scene.removeItem(self.line_item)
        # self.graphics_scene.removeItem(self.distance_text_item)
        self.ruler = False

    def calculate_distance(self, point1: QPoint, point2: QPoint) -> float:
        return math.sqrt((point2.x() - point1.x())**2 + (point2.y() - point1.y())**2)*self.coef_px_to_meters
    
    def cross_cursor(self, widget_position: QPoint, touch_position: QPoint, radius: int, dopusk: int = 0) -> bool:
        '''Определяет пересечение курсора мыши с виджетом (эллипсом).

        Первый аргумент центр виджета, второй позиция курсора, третий - радиус эллипса,
        четвертый является возможным допуском между курсором и эллипсом  '''
        x0, y0 = widget_position.x(), widget_position.y()
        x1, y1 = touch_position.x(), touch_position.y()
        if math.sqrt((x1-x0-radius)**2+(y1-y0-radius)**2) <= radius + dopusk:
            return True
        else:
            return False


