#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 21:04:55 2023

@author: acomeau
"""



import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model

X=np.array([[0,0],[400,0],[400,80]])
Y=[2,4,10]

ols = linear_model.LinearRegression()
model = ols.fit(X, Y)
r2 = model.score(X, Y)


############################################## Plot ################################################
x_pred = np.linspace(0, 800, 30)      # range of porosity values
y_pred = np.linspace(0, 80, 30)  # range of VR values

plt.style.use('default')

fig = plt.figure(figsize=(12, 4))

ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132, projection='3d')
ax3 = fig.add_subplot(133)

x = X[:, 0]
y = X[:, 1]
z = Y

xx_pred, yy_pred = np.meshgrid(x_pred, 0)
model_viz = np.array([xx_pred.flatten(), yy_pred.flatten()]).T
predicted = model.predict(model_viz)
ax1.plot(x, z, color='k', zorder=15, linestyle='none', marker='o', alpha=0.5)
ax1.scatter(xx_pred.flatten(), predicted, marker='.', facecolor=(0,0,0,0), s=20, edgecolor='#70b3f0')
ax1.set_xlabel('MHz.L (MHz)', fontsize=12)
ax1.set_ylabel('CPU Util (pC)', fontsize=12)
ax1.grid()

xx_pred, yy_pred = np.meshgrid(x_pred, y_pred)
model_viz = np.array([xx_pred.flatten(), yy_pred.flatten()]).T
predicted = model.predict(model_viz)
ax2.plot(x, y, z, color='k', zorder=15, linestyle='none', marker='o', alpha=0.5)
ax2.scatter(xx_pred.flatten(), yy_pred.flatten(), predicted, facecolor=(0,0,0,0), s=20, edgecolor='#70b3f0')
ax2.set_xlabel('MHz.L (MHz)', fontsize=12)
ax2.set_ylabel('CAPS (CAPS)', fontsize=12)
ax2.set_zlabel('CPU Util (pC)', fontsize=12)

xx_pred, yy_pred = np.meshgrid(0, y_pred)
model_viz = np.array([xx_pred.flatten(), yy_pred.flatten()]).T
predicted = model.predict(model_viz)
ax3.plot(y, z, color='k', zorder=15, linestyle='none', marker='o', alpha=0.5)
ax3.scatter(yy_pred.flatten(), predicted, marker='.', facecolor=(0,0,0,0), s=20, edgecolor='#70b3f0')
ax3.set_xlabel('CAPS (CAPS)', fontsize=12)
ax3.set_ylabel('CPU Util (pC)', fontsize=12)
ax3.grid()

ax2.view_init(elev=25, azim=45+180)

fig.suptitle('$R^2 = %.2f$' % r2, fontsize=20)

fig.tight_layout()

