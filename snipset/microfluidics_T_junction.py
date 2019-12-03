import numpy as np
import matplotlib.pyplot as plt

Pa_mBar = 10
Pb_mBar = 5
Pc_mBar = 0


Pa_mBar = np.linspace(0,10,100)

Ra = 0.1
Rb = 0.1
Rc = 0.2

V = (Pa_mBar/Ra + Pb_mBar/Rb + Pc_mBar/Rc)/(1/Ra + 1/Rb + 1/Rc)

ia = (Pa_mBar - V) / Ra
ib = (Pb_mBar - V) / Rb
ic = (V - Pc_mBar) / Rc


fig, ax1 = plt.subplots()


ax1.set_xlabel('Pa en mBar')
ax1.set_ylabel('Flux Puce en microL/min')
ax1.plot(Pa_mBar, ia, label="iA")
ax1.plot(Pa_mBar, ib, label="iB")
plt.legend()

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis


ax2.set_ylabel('Flux Puce en microL/min')  # we already handled the x-label with ax1
ax2.plot(Pa_mBar, ic, "r--", label='I_puce',  linewidth=5)


plt.legend()
fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
