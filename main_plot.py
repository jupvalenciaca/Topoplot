import pyedflib
import numpy as np
import matplotlib.pyplot as plt
from mne.viz import plot_topomap
import scipy.io
from scipy.interpolate import griddata
from config import elec

archivo = 'sujeto_base.edf'

class edf_topoplot(object):

	def __init__(self,):
		super(edf_topoplot, self).__init__()

	#lee el archivo .edf y extrae la informacion principal
	def read_edf(self,archivo):

		edf = pyedflib.EdfReader(archivo) #archivo edf
		channels_labels = edf.getSignalLabels() #etiquetas de los canales	
		nsig = edf.getNSamples()[0] #longitud de la toma		
		nch  = edf.signals_in_file #numero de canales		
		signal = np.zeros((nch,nsig))
		for x in range(nch):
			signal[x,:] = edf.readSignal(x)	
		return nch,edf,channels_labels, signal

	#calcula la potencia y las posiciones de los electrodos
	def cal_topoplot(self,nch,elec,channels_labels,signal):

		magnitud = signal**2	#magnitud
		pot_signal = np.mean(magnitud,axis=1) #potencia de la senal

		lab_ref_list = elec.keys()	#lista etiquetas de referencia
		pos = np.zeros(shape=(nch,2))
		label_ref_list = []

		#organiza la lista de etiquetas de referencia para ser comparada
		for lab_ref in lab_ref_list:	
			label_ref = lab_ref.upper()
			label_ref_list.append(label_ref)


		count =-1
		#organiza la lista de etiquetas de la medicion para ser comparada
		for lab in channels_labels:

			labe = lab.upper()
			label1 = labe.find('-')
			label = labe[0:label1]
			exist = label in label_ref_list
			count += 1
			#crea un np.ndarray con las coordenadas de los electrodos existentes en la medida
			if exist is True:				
				coord = elec[label]
				pos[count,:] = coord				
				coord = np.asarray(coord)
		counter = -1
		#elimina los electrodos que no fueron encontrados en la lista de referencia	
		for coord in pos:
			counter += 1
			check = np.array_equal(coord,[0.,0.])
			if check == True:
				print(counter)
				
				pos = np.delete(pos,counter,0)
				pot_signal = np.delete(pot_signal,counter,0)
				counter += -1
		print('vector de potencias')
		print(pot_signal)
		print('posicion de los nodos')
		print(pos)
		return pot_signal, pos
	#elabora el topoplot
	def topoplot(self,rel,pos):

		plt.title('topomap')
		fig3 = plot_topomap(pot_signal, pos, cmap='jet', sensors='k.', names=channels_labels, show_names=False,
				contours=0, image_interp='spline36')
		return fig3

ob = edf_topoplot()
nch, edf,channels_labels, signal = ob.read_edf(archivo)
pot_signal, pos = ob.cal_topoplot(nch,elec,channels_labels, signal)
fig3 = ob.topoplot(pot_signal,pos)