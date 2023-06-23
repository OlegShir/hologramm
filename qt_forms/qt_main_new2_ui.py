# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\X\Documents\GitHub\work\hologramm\qt_forms\qt_main_new2.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1065, 710)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("c:\\Users\\X\\Documents\\GitHub\\work\\hologramm\\qt_forms\\resources/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.open_file = QtWidgets.QPushButton(self.centralwidget)
        self.open_file.setGeometry(QtCore.QRect(21, 400, 170, 30))
        self.open_file.setObjectName("open_file")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(200, 0, 171, 30))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.canvas_SAP = QtWidgets.QGraphicsView(self.centralwidget)
        self.canvas_SAP.setGeometry(QtCore.QRect(527, 30, 516, 350))
        self.canvas_SAP.setObjectName("canvas_SAP")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(760, 0, 81, 30))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.get_RLI = QtWidgets.QPushButton(self.centralwidget)
        self.get_RLI.setEnabled(False)
        self.get_RLI.setGeometry(QtCore.QRect(20, 555, 170, 30))
        self.get_RLI.setObjectName("get_RLI")
        self.Type_RSA = QtWidgets.QGroupBox(self.centralwidget)
        self.Type_RSA.setGeometry(QtCore.QRect(20, 440, 171, 101))
        self.Type_RSA.setObjectName("Type_RSA")
        self.change_RSA = QtWidgets.QComboBox(self.Type_RSA)
        self.change_RSA.setEnabled(False)
        self.change_RSA.setGeometry(QtCore.QRect(10, 20, 151, 30))
        self.change_RSA.setEditable(False)
        self.change_RSA.setObjectName("change_RSA")
        self.add_RSA = QtWidgets.QPushButton(self.Type_RSA)
        self.add_RSA.setEnabled(False)
        self.add_RSA.setGeometry(QtCore.QRect(10, 60, 151, 30))
        self.add_RSA.setObjectName("add_RSA")
        self.save_img_RSA = QtWidgets.QPushButton(self.centralwidget)
        self.save_img_RSA.setEnabled(False)
        self.save_img_RSA.setGeometry(QtCore.QRect(20, 600, 170, 30))
        self.save_img_RSA.setObjectName("save_img_RSA")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QtCore.QRect(526, 390, 535, 291))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.create_SAP = QtWidgets.QPushButton(self.tab)
        self.create_SAP.setEnabled(False)
        self.create_SAP.setGeometry(QtCore.QRect(1, 230, 160, 30))
        self.create_SAP.setObjectName("create_SAP")
        self.solve_SAP = QtWidgets.QPushButton(self.tab)
        self.solve_SAP.setEnabled(False)
        self.solve_SAP.setGeometry(QtCore.QRect(171, 230, 160, 30))
        self.solve_SAP.setObjectName("solve_SAP")
        self.save_SAP = QtWidgets.QPushButton(self.tab)
        self.save_SAP.setEnabled(False)
        self.save_SAP.setGeometry(QtCore.QRect(341, 230, 170, 30))
        self.save_SAP.setObjectName("save_SAP")
        self.save_param_SAP = QtWidgets.QPushButton(self.tab)
        self.save_param_SAP.setEnabled(False)
        self.save_param_SAP.setGeometry(QtCore.QRect(343, 6, 170, 25))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("c:\\Users\\X\\Documents\\GitHub\\work\\hologramm\\qt_forms\\resources/save_RCA.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.save_param_SAP.setIcon(icon1)
        self.save_param_SAP.setObjectName("save_param_SAP")
        self.table_SAP = QtWidgets.QTableWidget(self.tab)
        self.table_SAP.setGeometry(QtCore.QRect(1, 33, 525, 190))
        self.table_SAP.setObjectName("table_SAP")
        self.table_SAP.setColumnCount(0)
        self.table_SAP.setRowCount(0)
        self.add_element_SAP = QtWidgets.QPushButton(self.tab)
        self.add_element_SAP.setEnabled(False)
        self.add_element_SAP.setGeometry(QtCore.QRect(1, 6, 160, 25))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("c:\\Users\\X\\Documents\\GitHub\\work\\hologramm\\qt_forms\\resources/add_RCA.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_element_SAP.setIcon(icon2)
        self.add_element_SAP.setObjectName("add_element_SAP")
        self.del_element_SAP = QtWidgets.QPushButton(self.tab)
        self.del_element_SAP.setEnabled(False)
        self.del_element_SAP.setGeometry(QtCore.QRect(172, 6, 160, 25))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("c:\\Users\\X\\Documents\\GitHub\\work\\hologramm\\qt_forms\\resources/del_RCA.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.del_element_SAP.setIcon(icon3)
        self.del_element_SAP.setObjectName("del_element_SAP")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.bt_get_estimation = QtWidgets.QPushButton(self.tab_2)
        self.bt_get_estimation.setEnabled(True)
        self.bt_get_estimation.setGeometry(QtCore.QRect(10, 160, 170, 30))
        self.bt_get_estimation.setObjectName("bt_get_estimation")
        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(10, 12, 85, 21))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("c:\\Users\\X\\Documents\\GitHub\\work\\hologramm\\qt_forms\\resources/PGав.png"))
        self.label.setObjectName("label")
        self.PGav = QtWidgets.QLabel(self.tab_2)
        self.PGav.setGeometry(QtCore.QRect(105, 10, 47, 21))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.PGav.setFont(font)
        self.PGav.setObjectName("PGav")
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(10, 230, 71, 24))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap("c:\\Users\\X\\Documents\\GitHub\\work\\hologramm\\qt_forms\\resources/Ksap.png"))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.tab_2)
        self.label_6.setGeometry(QtCore.QRect(10, 200, 80, 21))
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap("c:\\Users\\X\\Documents\\GitHub\\work\\hologramm\\qt_forms\\resources/PGк.png"))
        self.label_6.setObjectName("label_6")
        self.Type_RSA_KA = QtWidgets.QGroupBox(self.tab_2)
        self.Type_RSA_KA.setEnabled(True)
        self.Type_RSA_KA.setGeometry(QtCore.QRect(10, 50, 171, 101))
        self.Type_RSA_KA.setObjectName("Type_RSA_KA")
        self.change_RSA_KA = QtWidgets.QComboBox(self.Type_RSA_KA)
        self.change_RSA_KA.setEnabled(True)
        self.change_RSA_KA.setGeometry(QtCore.QRect(10, 20, 151, 30))
        self.change_RSA_KA.setEditable(False)
        self.change_RSA_KA.setObjectName("change_RSA_KA")
        self.add_RSA_KA = QtWidgets.QPushButton(self.Type_RSA_KA)
        self.add_RSA_KA.setEnabled(True)
        self.add_RSA_KA.setGeometry(QtCore.QRect(10, 60, 151, 30))
        self.add_RSA_KA.setObjectName("add_RSA_KA")
        self.PGk = QtWidgets.QLabel(self.tab_2)
        self.PGk.setGeometry(QtCore.QRect(94, 198, 47, 21))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.PGk.setFont(font)
        self.PGk.setText("")
        self.PGk.setObjectName("PGk")
        self.Ksab = QtWidgets.QLabel(self.tab_2)
        self.Ksab.setGeometry(QtCore.QRect(62, 228, 47, 21))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Ksab.setFont(font)
        self.Ksab.setText("")
        self.Ksab.setObjectName("Ksab")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1065, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.open_file, self.change_RSA)
        MainWindow.setTabOrder(self.change_RSA, self.add_RSA)
        MainWindow.setTabOrder(self.add_RSA, self.create_SAP)
        MainWindow.setTabOrder(self.create_SAP, self.solve_SAP)
        MainWindow.setTabOrder(self.solve_SAP, self.canvas_SAP)
        MainWindow.setTabOrder(self.canvas_SAP, self.save_SAP)
        MainWindow.setTabOrder(self.save_SAP, self.get_RLI)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Модель САП"))
        self.open_file.setText(_translate("MainWindow", "Открыть фаил"))
        self.label_2.setText(_translate("MainWindow", "Исходное РЛИ"))
        self.label_3.setText(_translate("MainWindow", "РЛИ с САП"))
        self.get_RLI.setText(_translate("MainWindow", "Вывести РЛИ"))
        self.Type_RSA.setTitle(_translate("MainWindow", "Выбор типа авиационного РСА"))
        self.add_RSA.setText(_translate("MainWindow", "Изменение параметров РСА"))
        self.save_img_RSA.setText(_translate("MainWindow", "Сохранить РЛИ "))
        self.create_SAP.setText(_translate("MainWindow", "Создать САП"))
        self.solve_SAP.setText(_translate("MainWindow", "Расчитать САП"))
        self.save_SAP.setText(_translate("MainWindow", "Сохранить РЛИ с САП"))
        self.save_param_SAP.setText(_translate("MainWindow", "Сохранить параметры САП"))
        self.add_element_SAP.setText(_translate("MainWindow", "Добавить элемент САП"))
        self.del_element_SAP.setText(_translate("MainWindow", "Удалить элемент САП"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Параметры САП"))
        self.bt_get_estimation.setText(_translate("MainWindow", "Провести оценку"))
        self.PGav.setText(_translate("MainWindow", "15 Вт"))
        self.Type_RSA_KA.setTitle(_translate("MainWindow", "Выбор типа космического РСА"))
        self.add_RSA_KA.setText(_translate("MainWindow", "Изменение параметров РСА"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Оценка энергетических характеристик"))
import resources_rc
