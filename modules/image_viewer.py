from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem, QLabel
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QFont
from modules.ChKP_table import ChkpTable
from modules.massager import MSGLabel
from PyQt5.QtCore import QPropertyAnimation, QPoint


class ImageView(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)

        self.setEnabled(False)
        # Create a scene for displaying images
        self.graphics_scene = QGraphicsScene(self)
        #  поле для хранения ссылки на метку текста масштаба
        self.scale_label: QLabel 
        self.create_scale_label()
        
        self.setScene(self.graphics_scene)
        self.setGeometry(5, 30, 516, 350)
        
        # ограничители масштабирования
        self.min_ratio: float
        self.max_ratio: float
        # размер изображения в px
        self.xsize_RLI_pixmap: int
        self.ysize_RLI_pixmap: int
        # инициализация ссылки на таблицу с ЧКП
        self.table: ChkpTable
        # инициализация ссылки на мессенджер
        self.msg: MSGLabel
        # инициализация работы с метками ЧКП
        self.pixmap_item = QGraphicsPixmapItem()
        self.graphics_scene.addItem(self.pixmap_item)
        self.Chkp_pixmap = QPixmap("icon.png")
        self.xsize_Chkp_pixmap:int = self.Chkp_pixmap.width()
        self.ysize_Chkp_pixmap: int = self.Chkp_pixmap.height()
        
        # инициализация масштаба
        self.scale_factor: float = 1.0
        # инициализация позиция мыши и размера 
        self.initial_pos: QPoint

        # Enable zooming
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # резервирование места для коэффициентов перерасчета 
        self.coef_px_to_count: list
        self.coef_px_to_meters: list

    def set_link(self, table, msg):
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
        self.scale_factor = max(min(self.scale_factor, self.max_ratio), self.min_ratio)
     
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
        # Handle mouse move event for moving the image
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
        if self.table.rowCount() and self.table.currentRow() != -1:
            # Handle mouse release event
            if event.pos() == self.initial_pos and event.button() == Qt.LeftButton: # type: ignore 
                # получение координат пикселей места нажатия
                pixmap_pos = self.mapToScene(event.pos())
                # получаем элемент на который нажали - это либо само РЛИ, либо уже существующая ЧКП
                pixmap_item = self.graphics_scene.itemAt(pixmap_pos, self.transform())
                # если не нажали ЧКП
                if pixmap_item == self.pixmap_item:
                    # получаем ссылку на метку для текущей строки
                    pixmap_current_row = self.table.Chkp_index_list[self.table.currentRow()]
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
                    self.table.Chkp_index_list[self.table.currentRow()] = label
                    # перезаписываем координаты
                    self.table.update_coord_ChKP(self.table.currentRow(), pixmap_pos)
                    

            elif event.button() == Qt.RightButton: # type: ignore
                # получение координат пикселей места нажатия
                item_pos = self.mapToScene(event.pos())
                # получаем элемент на который нажали
                item = self.graphics_scene.itemAt(item_pos, self.transform())
                # если это ЧКП
                if item in self.labels:
                    # поиск и удаление
                    self.graphics_scene.removeItem(item)
                    self.table.Chkp_index_list.remove(item)

        super(ImageView, self).mouseReleaseEvent(event)

    def get_limit_ratio(self, image) -> tuple:
        # Получение размера изображения
        self.xsize_RLI_pixmap = image.size().width()
        self.ysize_RLI_pixmap = image.size().height()
        xratio = self.size().width() / image.size().width() 
        yratio = self.size().height()/ image.size().height()

        return min(xratio, yratio), max(1/xratio, 1/yratio)
   
    def open_file(self, path_to_img):
        # Загрузка изображения с помощью QPixmap
        image = QPixmap(path_to_img)
        # Установка изображения в ImageView
        self.pixmap_item.setPixmap(image)

        self.min_ratio, self.max_ratio = self.get_limit_ratio(image)

        self.setEnabled(True)


        # отображение метки масштаба
        self.scale_label.show()  # Покажите метку текста после открытия файла
        self.update_scale_label_text()
        


    def get_visible_pixels(self):
        """получение размеров изображения в пикселях и 
           получение области видимости ROI_px вида [x0, y0, wight, height] в отсчетах"""
        # Получение видимой области QGraphicsView в координатах сцены
        visible_rect = self.mapToScene(self.viewport().rect())

        # Определение видимой области в пикселях
        rect = visible_rect.boundingRect()

        # формирование области
        ROI_px = [rect.left(), rect.top(), rect.right()-rect.left(), rect.bottom()-rect.top()]

        return ROI_px
    
    def set_scale_factor_px_count_and_meters(self, coef_px_to_count, coef_px_to_meters) -> None:
        self.coef_px_to_count = coef_px_to_count
        self.coef_px_to_meters = coef_px_to_meters

    def create_scale_label(self):
        # Добавление метки текста для отображения масштаба
        self.scale_label = QLabel(self)
        self.scale_label.setText("1111")
        self.scale_label.setFont(QFont("Arial", 12))
        self.scale_label.setStyleSheet("color: red")  # Установите красный цвет текста


    def update_scale_label_text(self):
        _, _, wight_px, height_px = self.get_visible_pixels()
        meters_x = round(wight_px * self.coef_px_to_meters[0])
        self.scale_label.setText('{meters_x} м.')
        print(meters_x)
        # Расчет размера метки текста в пикселях
        scale_label_position_x = (self.size().width() - self.scale_label.sizeHint().width()) / 2
        scale_label_position_y = self.size().height() - self.scale_label.sizeHint().height()
        # позиция метки текста
        self.scale_label.move(round(scale_label_position_x), scale_label_position_y)

        # Помещение метки на верхний слой
        self.scale_label.raise_()


            
        
       
