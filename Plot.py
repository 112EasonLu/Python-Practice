from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import numpy as np

def Data():
	#X=['RP0','RP6','RP12','RP18']
	X=[0,6,12,18]
	compress=[174.64, 168.59, 182.38, 184.6]
	void=[17.35, 16.58, 14.19, 11.36]
	K=[0.4, 0.39, 0.352, 0.32]
	data_matrix=[X,compress,void,K]
	return data_matrix

if __name__ == '__main__':
	data=Data()
	print(data)
	fig = plt.figure(1) #定義figure，（1）中的1是什么
	ax_cof = HostAxes(fig, [0.1, 0.08, 0.71, 0.85])  #用[left, bottom, weight, height]的方式定義axes，0 <= l,b,w,h <= 1
#改字型
	plt.rcParams['font.sans-serif'] = ['Times New Roman']
	plt.rcParams['axes.unicode_minus'] = False 
	plt.rcParams['axes.labelsize'] = 14
	plt.rcParams['axes.titlesize'] = 14
	plt.rcParams['axes.labelsize'] = 14
	plt.rcParams['xtick.labelsize'] = 14
	plt.rcParams['ytick.labelsize'] = 14

#parasite addtional axes, share x
	ax_temp = ParasiteAxes(ax_cof, sharex=ax_cof)
	ax_load = ParasiteAxes(ax_cof, sharex=ax_cof)
	#ax_cp = ParasiteAxes(ax_cof, sharex=ax_cof)
	#ax_wear = ParasiteAxes(ax_cof, sharex=ax_cof)

#append axes
	ax_cof.parasites.append(ax_temp)
	ax_cof.parasites.append(ax_load)
	#ax_cof.parasites.append(ax_cp)
	#ax_cof.parasites.append(ax_wear)

#invisible right axis of ax_cof
	ax_cof.axis['right'].set_visible(False)
	ax_cof.axis['top'].set_visible(True)
	ax_temp.axis['right'].set_visible(True)
	ax_temp.axis['right'].major_ticklabels.set_visible(True)
	ax_temp.axis['right'].label.set_visible(True)

#set label for axis
	ax_cof.set_ylabel('Compress Strength (Kgf/$\mathregular{m^2}$)', fontsize=20)
	ax_cof.set_xlabel('Addition of Waste Tire Rubber Powder (g)')
	ax_temp.set_ylabel('Porosity (%)', fontsize=20)
	ax_load.set_ylabel('Coef. of Permeability (cm/s)', fontsize=20)
	#ax_cp.set_ylabel('CP')
	#ax_wear.set_ylabel('Wear')

	load_axisline = ax_load.get_grid_helper().new_fixed_axis
	#cp_axisline = ax_cp.get_grid_helper().new_fixed_axis
	#wear_axisline = ax_wear.get_grid_helper().new_fixed_axis

	ax_load.axis['right2'] = load_axisline(loc='right', axes=ax_load, offset=(70,0))
	#ax_cp.axis['right3'] = cp_axisline(loc='right', axes=ax_cp, offset=(80,0))
	#ax_wear.axis['right4'] = wear_axisline(loc='right', axes=ax_wear, offset=(120,0))

	fig.add_axes(ax_cof)

	#set limit of x, y
	ax_cof.set_xlim(-3,21)
	ax_cof.set_ylim(0,200)


	curve_cof = ax_cof.plot(data[0], data[1], 's-',label="Compress Strength",color='black')
	# markerfacecolor='none 標記變成中空
	curve_temp = ax_temp.plot(data[0], data[2],'o-.', label='Porosity', color='red')
	curve_load = ax_load.plot(data[0], data[3],'^-', label="Coef. of Permeability", color='green')
	#curve_cp = ax_cp.plot(data[0], data[4], label="CP", color='pink')
	#curve_wear = ax_wear.plot(data[0], data[5], label="Wear", color='blue')

	ax_temp.set_ylim(0,20)
	ax_load.set_ylim(0,1)
	#ax_cp.set_ylim(0,0.5)
	#ax_wear.set_ylim(0,0.5)

	ax_cof.legend()

#軸名稱，刻度值的顏色
#ax_cof.axis['left'].label.set_color(ax_cof.get_color())
	ax_temp.axis['right'].label.set_color('red')
	ax_load.axis['right2'].label.set_color('green')
	#ax_cp.axis['right3'].label.set_color('pink')
	#ax_wear.axis['right4'].label.set_color('blue')

	ax_temp.axis['right'].major_ticks.set_color('red')
	ax_load.axis['right2'].major_ticks.set_color('green')
	#ax_cp.axis['right3'].major_ticks.set_color('pink')
	#ax_wear.axis['right4'].major_ticks.set_color('blue')

	ax_temp.axis['right'].major_ticklabels.set_color('red')
	ax_load.axis['right2'].major_ticklabels.set_color('green')
	#ax_cp.axis['right3'].major_ticklabels.set_color('pink')
	#ax_wear.axis['right4'].major_ticklabels.set_color('blue')

	ax_temp.axis['right'].line.set_color('red')
	ax_load.axis['right2'].line.set_color('green')
	#ax_cp.axis['right3'].line.set_color('pink')
	#ax_wear.axis['right4'].line.set_color('blue')

	#plt.yticks(fontproperties = 'Times New Roman', size = 14)
	plt.xticks([0,6,12,18],fontproperties='Times')
	font2 = {'size' : 14}
	#plt.ylabel('Compress Strength(Kgf/$\mathregular{m^2}$)', fontproperties="Times New Roman")
	#plt.xticks(fontdict={'family' : 'Times New Roman', 'size'  : 14})
	plt.xlabel('Addition of Waste Tire Rubber Powder (g)', fontsize=12)
	plt.legend(prop={'family' : 'Times New Roman', 'size'  : 12})

	plt.show()