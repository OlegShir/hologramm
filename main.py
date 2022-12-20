import sys
from PyQt5 import QtWidgets, uic


class MainForm(QtWidgets.QMainWindow):
    """Класс основного окна программы"""

    def __init__(self):
        super(MainForm, self).__init__()
        self.file_path: str = ''
        self.file_name: str = ''

        # загрузка файла интерфейса основного окна
        uic.loadUi('qt_forms/qt_main.ui', self)
        # нажатие открыть голограмму
        self.open_file.clicked.connect(self.get_file_path)
        self.show()

    def get_file_path(self) -> None:
        """Метод загрузки расположения файла голограммы."""
        self.collection_param_RLS()
        file_path, a = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите голограмму", "", "Hologramm (*.rgg)")
        # если фаил выбран -> сохраняем его путь и имя
        if file_path:
            self.file_path = file_path
            print(self.file_path)
            self.file_name = file_path.split("/")[-1]
            self.label_file_name.setText(self.file_name)
            
        

    def collection_param_RLS(self) -> list:
        """Метод сбора параметров РЛС."""
        number_complex_readings = self.number_complex_readings.text()
        number_registered_impulses = self.number_registered_impulses.text()
        sampling_frequency = self.sampling_frequency.text()
        wavelength = self.wavelength.text()
        pulse_period = self.pulse_period.text()
        signal_spectrum_width = self.signal_spectrum_width.text()
        pulse_duration = self.pulse_duration.text()

        string_array = [number_complex_readings, number_registered_impulses,
                        sampling_frequency, wavelength, pulse_period, signal_spectrum_width, pulse_duration]

        float_array = [float(x) for x in string_array]

        return float_array

    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainForm()
    app.exec_()
