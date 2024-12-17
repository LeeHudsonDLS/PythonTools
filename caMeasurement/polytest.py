import numpy as np

x = np.linspace(0,1,1000)
f = 1/4

sine = np.sin(2*np.pi*f*x) + np.random.normal(scale=0.1, size=len(x))

poly = np.polyfit(x, sine, deg=5)
print("Here")