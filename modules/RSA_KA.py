""""Данный класс создает экземпляр космической РСА.
    Пока входными данными является:
    [Импульсная мощность ПРД КРСА,
    КНД антенны КРСА,
    Дальность PЛ наблюдения,
    Размер антенны РСА продольный,
    Размер антенны РСА поперечный,
    Эффективная площадь антенны РСА,
    Мгновенно засвечиваемый ДН антенны участок вдоль линии пути,
    Длительность зондирующего импульса]"""
import numpy as np

# константы
BF_grass_dB = -12

def convert_Db_to_times(var):
    return 10**(var/10)

BF_grass_times = convert_Db_to_times(BF_grass_dB)



class RSAKA():
    def __init__(self, RSA_KA_Param) -> None:
        self.RSA_KA_Param: list = RSA_KA_Param
        self.get_init_param()

    def get_init_param(self) -> None:
        pulse_power, KND_antenna, observation_range, size_antenna_long, size_antenna_trans, \
        effective_area_antenna, illuminated_section, pulse_duration = self.RSA_KA_Param

        self.pulse_power = pulse_power
        self.KND_antenna = convert_Db_to_times(KND_antenna)
        self.observation_range = observation_range
        self.size_antenna_long = size_antenna_long
        self.size_antenna_trans = size_antenna_trans
        self.effective_area_antenna = effective_area_antenna
        self.illuminated_section = illuminated_section
        self.pulse_duration = pulse_duration

    def get_Pf(self):
        Pf = (self.pulse_power*self.KND_antenna*BF_grass_times*3e8*self.pulse_duration*self.illuminated_section)/(8*np.pi*(self.observation_range**2))

        return Pf
    
    def get_PG(self, Kp, size_x_ChKP, size_y_ChKP):
        
        PG = (Kp*self.get_Pf()*4*np.pi*(self.observation_range**2)*2*size_x_ChKP*size_y_ChKP)/(self.effective_area_antenna*3e8*self.pulse_duration*self.illuminated_section)

        return PG