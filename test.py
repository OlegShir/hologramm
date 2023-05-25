import numpy as np
import matplotlib.pyplot as plt

with open("C:/Users/X/Desktop/185900/test.adc", 'rb') as rgg_file:
        new_part_rgg_file = np.frombuffer(rgg_file.read(1000000), dtype='int64')
        # создание копии из буфера для возможности его редактивования

        # plot
        fig, ax = plt.subplots()

        ax.plot(new_part_rgg_file)

        plt.show()