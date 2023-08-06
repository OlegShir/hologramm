from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QLabel, QGraphicsRectItem
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QBrush
from modules.ChKP_table_2 import ChkpTable_2
from modules.massager import MSGLabel
from PyQt5.QtCore import QPropertyAnimation, QPoint


class ImageView(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)

        self.parent_widget = parent

        self.graphics_scene = QGraphicsScene(self)

        self.setScene(self.graphics_scene)
        self.setGeometry(5, 30, 516, 350)
        
        # ограничители масштабирования
        self.min_ratio: float
        self.max_ratio: float
        # инициализация ссылки на таблицу с ЧКП
        self.table: ChkpTable_2
        # инициализация ссылки на мессенджер
        self.msg: MSGLabel
        # инициализация работы с метками ЧКП
        self.Chkp_pixmap = QPixmap(":/ico/qt_forms/resources/icon.png")
        self.xsize_Chkp_pixmap:int = self.Chkp_pixmap.width()
        self.ysize_Chkp_pixmap: int = self.Chkp_pixmap.height()

        # Enable zooming
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # резервирование места для коэффициентов перерасчета 
        self.coef_px_to_count: list
        self.coef_px_to_meters: list

        self.label_x: QLabel
        self.label_y: QLabel


    def set_init(self) -> None:
        self.resetTransform()        
        self.setEnabled(False)
        # Инициализация работы с измерением фона
        self.star_fon_select:bool = False
        
        # инициализация масштаба
        self.scale_factor: float = 1.0
        # инициализация позиция мыши и размера 
        self.initial_pos: QPoint
        # Если есть метки -> удаляем
        if len(self.graphics_scene.items()):
            for item in self.graphics_scene.items():
                self.graphics_scene.removeItem(item)
        self.pixmap_item = QGraphicsPixmapItem()
        self.graphics_scene.addItem(self.pixmap_item)
        if hasattr(self, 'fon_rect'):
            if self.fon_rect in self.graphics_scene.items():
                self.graphics_scene.removeItem(self.fon_rect)

    def add_fon_rect(self, size_fon_rect):
        if hasattr(self, 'fon_rect'):
            if self.fon_rect in self.graphics_scene.items():
                self.graphics_scene.removeItem(self.fon_rect)
        # переменные для формирования квадрата для области фона
        self.fon_rect = QGraphicsRectItem()
        self.fon_rect_size = size_fon_rect
        self.fon_rect.setRect(0,0,self.fon_rect_size, self.fon_rect_size)
        # Настройка стиля квадрата (зеленая граница, без заливки)
        pen = self.fon_rect.pen()
        pen.setColor(Qt.green) # type: ignore
        pen.setWidth(2)
        self.fon_rect.setPen(pen)
        self.fon_rect.setBrush(QBrush()) # type: ignore




    def set_link(self, table, msg, label_x, label_y):
        self.label_x = label_x
        self.label_y = label_y
        self.table = table
        self.msg = msg
    
    def wheelEvent(self, event):
        # Handle mouse wheel event for zooming
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.2
        else:
            self.scale_factor /= 1.2 

        # Ограничение масштабирования
        self.scale_factor = max(min(self.scale_factor, 1), self.min_ratio)
     
        # масштабирование РЛИ
        self.resetTransform()
        self.scale(self.scale_factor, self.scale_factor)

        # # Масштабирование меток ЧКП
        for label in self.table.Chkp_index_list:
            if label and self.scale_factor <=1 :
                # Получение текущего положения метки
                label_pos = label.pos()
                # Получение текущего размера метки
                old_size = label.boundingRect().width()
                # Масштабирование пиксельного изображения c использованием оригинального изображения метки
                new_size = int(self.xsize_Chkp_pixmap / self.scale_factor)
                scaled_pixmap = self.Chkp_pixmap.scaledToWidth(new_size)
                # Установка масштабированного изображения метки
                label.setPixmap(scaled_pixmap)
                # Пересчет позиции с учетом изменения масштаба
                new_pos = label_pos + QPointF((old_size - new_size) / 2, (old_size - new_size) / 2)
                # Установка новой позиции метки
                label.setPos(new_pos)
        
        self.update_scale_label_text()


     

    def mousePressEvent(self, event):
        # Handle mouse press event for moving the image
        self.initial_pos = event.pos()
        super(ImageView, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):        
        
        if event.buttons() == Qt.LeftButton: # type: ignore 
            
            delta = event.pos() - self.initial_pos
            target_pos = self.viewport().pos() - delta

            animation = QPropertyAnimation(self.viewport(), b"pos")
            animation.setDuration(200)  # Длительность анимации в миллисекундах
            animation.setStartValue(self.viewport().pos())
            animation.setEndValue(target_pos)
            animation.start()

            event.accept()
    
        super(ImageView, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self.star_fon_select:
            if event.pos() == self.initial_pos and event.button() == Qt.LeftButton: # type: ignore 
                # Удаляем область если она уже нарисована
                if self.fon_rect in self.graphics_scene.items():
                    self.graphics_scene.removeItem(self.fon_rect)
                # получение координат пикселей места нажатия
                pixmap_pos = self.mapToScene(event.pos())
                self.fon_rect.setPos(QPointF(pixmap_pos.x()-self.fon_rect_size/2, pixmap_pos.y()-self.fon_rect_size/2))
                self.graphics_scene.addItem(self.fon_rect)


        else:
            if self.table.table.rowCount() and self.table.table.currentRow() != -1:
                # Handle mouse release event
                if event.pos() == self.initial_pos and event.button() == Qt.LeftButton: # type: ignore 
                    # получение координат пикселей места нажатия
                    pixmap_pos = self.mapToScene(event.pos())
                    # получаем элемент на который нажали - это либо само РЛИ, либо уже существующая ЧКП
                    pixmap_item = self.graphics_scene.itemAt(pixmap_pos, self.transform())
                    # если не нажали ЧКП
                    if pixmap_item == self.pixmap_item:
                        # получаем ссылку на метку для текущей строки
                        pixmap_current_row = self.table.Chkp_index_list[self.table.table.currentRow()]
                        # если есть метра, то удаляем ее
                        if pixmap_current_row:
                            self.graphics_scene.removeItem(pixmap_current_row)
                        # учитываем масштаб
                        scaled_width = round(self.Chkp_pixmap.width() / self.scale_factor)
                        scaled_height = round(self.Chkp_pixmap.height() / self.scale_factor)
                        # добавляем изображение ЧКП в сцену
                        label = self.graphics_scene.addPixmap(self.Chkp_pixmap.scaled(scaled_width, scaled_height))
                        # установка позиции ЧКП
                        label_pos = pixmap_pos - QPointF(scaled_width/2, scaled_width/2)
                        label.setPos(label_pos)
                        # добавление в список
                        self.table.Chkp_index_list[self.table.table.currentRow()] = label
                        # перезаписываем координаты
                        self.table.update_coord_ChKP(self.table.table.currentRow(), pixmap_pos)
                        

                elif event.button() == Qt.RightButton: # type: ignore
                    # получение координат пикселей места нажатия
                    item_pos = self.mapToScene(event.pos())
                    # получаем элемент на который нажали
                    item = self.graphics_scene.itemAt(item_pos, self.transform())
                    # если это ЧКП
                    if item in self.table.Chkp_index_list:
                        # поиск и удаление
                        self.graphics_scene.removeItem(item)
                        row = self.table.Chkp_index_list.index(item)
                        self.table.table.removeRow(row)
                        self.table.Chkp_index_list.remove(item)

        super(ImageView, self).mouseReleaseEvent(event)

    def get_limit_ratio(self, image) -> tuple:
        # Определение видимой области в пикселях
        vertical = self.verticalScrollBar().width()
        horizontal = self.horizontalScrollBar().height()

        x_ratio = (self.size().width()-vertical) / image.size().width() 
        y_ratio = (self.size().height()-horizontal)/ image.size().height()

        return max(x_ratio, y_ratio), min(1/x_ratio, 1/y_ratio)
   
    def open_file(self, path_to_img):
        # Загрузка изображения с помощью QPixmap
        image = QPixmap(path_to_img)
        # Установка изображения в ImageView
        self.pixmap_item.setPixmap(image)

        self.min_ratio, self.max_ratio = self.get_limit_ratio(image)

        self.setEnabled(True)

        self.label_x.setHidden(False)
        self.label_y.setHidden(False)

        # отображение метки масштаба
        self.update_scale_label_text()

        # Создание пользовательского курсора в виде квадрата 100x100 пикселей
        # self.square_cursor = QCursor(QPixmap(100, 100))
        # self.square_cursor_painter = QPainter(self.square_cursor.pixmap())
        # self.square_cursor_painter.fillRect(self.square_cursor.pixmap().rect(), Qt.green) # type: ignore
 
        

    def get_visible_pixels(self):
        """получение размеров изображения в пикселях и 
           получение области видимости ROI_px вида [x0, y0, wight, height] в отсчетах"""
        # Получение видимой области QGraphicsView в координатах сцены
        visible_rect = self.mapToScene(self.viewport().rect()) # type: ignore

        # Определение видимой области в пикселях
        rect = visible_rect.boundingRect()

        # формирование области
        ROI_px = [rect.left(), rect.top(), rect.right()-rect.left(), rect.bottom()-rect.top()]

        return ROI_px
    
    def get_ROI_RLI_in_count(self):

        ROI_RLI_in_count = self.get_ROI_in_count(self.get_visible_pixels())

        return ROI_RLI_in_count
    
    def get_ROI_fon_in_count(self, count_resize):

        fon_rect_pos = [self.fon_rect.pos().x(),
                         self.fon_rect.pos().y(),
                         self.fon_rect.rect().width(), # Чтобы можно было свернуть
                         self.fon_rect.rect().height(),]
        
        ROI_fon_in_count = self.get_ROI_in_count(fon_rect_pos)

        return ROI_fon_in_count

    
    def get_ROI_in_count(self, ROI):
        x0_px, y0_px, wight_px, height_px = ROI

        ROI_in_count = [x0_px*self.coef_px_to_count[0],
                        y0_px*self.coef_px_to_count[1],
                        wight_px*self.coef_px_to_count[0],
                        height_px*self.coef_px_to_count[1]]
        
        ROI_in_count = [round(x) for x in ROI_in_count]

        return ROI_in_count

    
    def set_scale_factor_px_to_count_and_meters(self, coef_px_to_count, coef_px_to_meters) -> None:
        self.coef_px_to_count = coef_px_to_count
        self.coef_px_to_meters = coef_px_to_meters

    def update_scale_label_text(self):
        _, _, wight_px, height_px = self.get_visible_pixels()
        meters_x = round(wight_px * self.coef_px_to_meters[0])
        meters_y = round(height_px * self.coef_px_to_meters[1])
        self.label_x.setText(f'{meters_x} м.')
        self.label_y.setText(f'{meters_y} м.')

    def save_image(self) -> None:
        """Метод позволяет сохранять видимое в левом окне изображение"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)")

        if file_path:
            visible_rect = self.viewport().rect()
            pixmap = self.viewport().grab(visible_rect)
            pixmap.save(file_path)


       
