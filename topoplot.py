import numpy as np
import argparse
import pyedflib
import scipy.io
from scipy.spatial import Delaunay
from scipy.interpolate import griddata
from scipy import interpolate
import matplotlib.pyplot as plt
from mne.viz import plot_topomap

class edf_topoplot(object):

	def __init__(self,):
		super(edf_topoplot, self).__init__()

	def argparse(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('-i','--archivo', help='nombre del archivo .edf que desea utilizar',type = str)
		parser.add_argument('-o','--figure', help='ingresa la direccion para guardar el topoplot')
		parser.add_argument('-c','--config', help='nombre del archivo de configuracion. NOTA: el nombre de la variable debe ser elec')
		parsedargs = parser.parse_args()
		arc = parsedargs.archivo
		output = parsedargs.figure
		config  = parsedargs.config
		return arc, output, config

	#lee el archivo .edf y extrae la informacion principal
	def read_edf(self,arc):

		edf = pyedflib.EdfReader(arc)#archivo edf
		channels_labels = edf.getSignalLabels() #etiquetas de los canales	
		nsig = edf.getNSamples()[0] #longitud de la toma		
		nch  = edf.signals_in_file #numero de canales		
		signal = np.zeros((nch,nsig))
		for x in range(nch):
			signal[x,:] = edf.readSignal(x)	
		return signal,nch,channels_labels

	#calcula la potencia y las posiciones de los electrodos
	def calc_power(self,signal):
		magnitud = signal**2	#magnitud
		pot_signal = np.mean(magnitud,axis=1) #potencia de la senal
		# print('vector de potencias')
		# print(pot_signal)
		return pot_signal

	def calc_positions(self,config,channels_labels,nch,pot_signal):
		config_file = __import__(config)
		elec = config_file.elec 		#coordenadas de los electrodos de referencia
		lab_ref_list = config_file.labels	#lista etiquetas de referencia
		label_ref_list = []

		# #organiza la lista de etiquetas de referencia para ser comparada
		for lab_ref in lab_ref_list:
			label_ref = lab_ref.upper()
			label_ref_list.append(label_ref)
		count = 0
		counter = -1
		pos = np.zeros(shape=(nch,2))

		#organiza la lista de etiquetas de la medicion para ser comparada
		for lab in channels_labels:
			labe = lab.upper()
			label1 = labe.find('-')
			label = labe[0:label1]
			exist = label in label_ref_list

			#crea un np.ndarray con las coordenadas de los electrodos existentes en la medida
			if exist is True:
				point = label_ref_list.index(label)
				coord = elec[point]
				pos[count,:] = coord
				# coord = np.asarray(coord)
			count += 1
		
		#elimina los electrodos que no fueron encontrados en la lista de referencia	
		for coord in pos:
			counter += 1
			check = np.array_equal(coord,[0.,0.])
			if check is True:
				pos = np.delete(pos,counter,0)
				pot_signal = np.delete(pot_signal,counter,0)
				counter += -1
		# print('posicion de los nodos')
		# print(pos)
		return pos,pot_signal,elec

	#elabora el topoplot
	def topoplot(self,pot_signal,pos):

		plt.title('topomap')
		fig = plot_topomap(pot_signal, pos, cmap='jet', sensors='k.', names=channels_labels, show_names=False,
				contours=0, image_interp='spline36' ,show = False)
		# plt.savefig(output)
		plt.show(fig)
		return fig

	def mesh(self,pos,elec):
		# malla de los electrodos de la muestra
		tri = Delaunay(pos)
		plt.triplot(pos[:,0], pos[:,1], tri.simplices)
		plt.plot(pos[:,0], pos[:,1], 'o')
		plt.show()

		# malla de los electrodos de New York Head Model
		tri = Delaunay(elec)
		plt.triplot(elec[:,0], elec[:,1], tri.simplices)
		plt.plot(elec[:,0], elec[:,1], 'o')
		plt.show()

if __name__ == '__main__':
	ob = edf_topoplot()
	arc,output,config = ob.argparse()
	signal,nch,channels_labels = ob.read_edf(arc)
	pot_signal = ob.calc_power(signal)
	pos, pot_signal, elec= ob.calc_positions(config,channels_labels,nch,pot_signal)
	fig = ob.topoplot(pot_signal,pos)
	_ = ob.mesh(pos,elec)
