from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from modules.helper import help

import resources

class Blocker(QLabel):
    def __init__(self, parent_widget):
        super(Blocker, self).__init__(parent_widget,)

        self.parent_widget = parent_widget

        self.setFixedSize(40, 40)
        self.move(537, 30)


        # Устанавливаем изображение
        self.pixmap_open = QPixmap(':/ico/qt_forms/resources/block_open.png').scaled(self.size())    
        self.pixmap_close = QPixmap(':/ico/qt_forms/resources/block_close.png').scaled(self.size())
       
    def blocked(self) -> None:
        self.setPixmap(self.pixmap_close)
        self.setToolTip(help.get('blocker_close', ''))
        self.status = False
        self.setEnabled(True)
        # блокирование родительских виджетов
        self.parent_widget.fon_param.blocked()
        self.parent_widget.table_Chkp_2.slider.setEnabled(False)
        self.parent_widget.table_Chkp_2.table.setEnabled(False)


    def unblocked(self) -> None:
        self.setPixmap(self.pixmap_open)
        self.status = True
        self.setEnabled(False)
        # разблокирование родительских виджетов
        self.parent_widget.table_Chkp_2.slider.setEnabled(True)
        self.parent_widget.table_Chkp_2.table.setEnabled(True)

    
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton: # type: ignore 
            if not self.status:
                self.unblocked()
            else:
                self.blocked()

    def set_init(self) -> None:
              
        self.unblocked()
        
      

        
        