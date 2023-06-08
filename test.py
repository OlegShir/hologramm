import numpy as np
import matplotlib.pyplot as plt
from matplotlib import scale
from scipy import io
import matplotlib.colors as mcolors

file = io.loadmat('rli.mat')
rli = file.get('rli_py')
rli = np.abs(rli)
magnitude_log = rli




plt.figure()
plt.imshow(magnitude_log, cmap = 'gray', aspect='auto', norm=mcolors.PowerNorm(0.3))

plt.title('АРЛИ сформированное по суммарной РГГ')
plt.show()
