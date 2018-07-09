class edf_topoplot(object):

	def __init__(self):
		super(edf_topoplot, self).__init__()

	#lee el archivo .edf y extrae la informacion principal
	def read_edf(self,archi):
		import numpy as np
		import pyedflib
		from pyedflib import EdfWriter
		edf = pyedflib.EdfReader(archi)
		channels_labels = edf.getSignalLabels()	
		nsig = edf.getNSamples()[0]
		nch  = edf.signals_in_file			
		signal = np.zeros((nch,nsig))
		for i in range(nch):
			signal[i,:] = edf.readSignal(i)
		return signal,nch,channels_labels

	#calcula la potencia y las posiciones de los electrodos
	def power(self,signal):
		import numpy as np
		power = signal**2
		power = np.mean(power,axis=1) #potencia de la senal
		return power

	#lee el archivo config, y elabora lista de etiquetas y de coordenadas de electrodos
	def prepare(self,config):
		import numpy as np
		import scipy.spatial.distance as sp
		config_file = __import__(config)
		# organiza la lista de etiquetas de referencia para ser comparada		
		lab_ref_list = config_file.labels
		label_ref_list = []
		for lab_ref in lab_ref_list:
			label_ref = lab_ref.upper()
			label_ref_list.append(label_ref)

		# organiza las coordenadas de los electrodos que serán referencia
		elec = config_file.elec
		cz = label_ref_list.index('CZ')
		iz = label_ref_list.index('IZ')
		cz = elec[cz]
		iz = elec[iz]
		cz_iz = np.vstack((cz,iz))
		radius = sp.pdist(cz_iz)
		new_elec = np.zeros(shape=(0,2))
		new_labels_ref = []
		for lab_ref in label_ref_list:
			m = label_ref_list.index(lab_ref)
			coord = elec[m]
			YY = np.vstack((cz,coord))
			dist = sp.pdist(YY)
			if dist < radius:
				new_labels_ref.append(lab_ref)
				new_elec = np.vstack((new_elec,coord))

		return new_elec,new_labels_ref,cz,radius


	def positions(self,nch,channels_labels,elec,label_ref_list,pot_signal):
		import numpy as np
		count = 0
		pos = np.zeros(shape=(nch,2))

		# organiza la lista de etiquetas de la medicion para ser comparada
		for lab in channels_labels:
			labe = lab.upper()
			label1 = labe.find('-')
			label = labe[0:label1]
			if label == 'T1':	label = 'FT9'
			if label == 'T2':	label = 'FT10'
			if label == 'T3':	label = 'T7'
			if label == 'T4':	label = 'T8'
			if label == 'T5':	label = 'P7'
			if label == 'T6':	label = 'P8'

			exist = label in label_ref_list

			#crea un np.ndarray con las coordenadas de los electrodos existentes en la medida
			if exist is True:
				coord = elec[label_ref_list.index(label)]
				pos[count,:] = coord
			count += 1
		count = 0

		#elimina la informacion de los electrodos que no fueron encontrados en la lista de referencia	
		for coord in pos:			
			check = np.array_equal(coord,[0.,0.])
			if check is True:
				pos = np.delete(pos,count,0)
				pot_signal = np.delete(pot_signal,count,0)
				channels_labels = np.delete(channels_labels,count,0)
				count += -1
			count += 1
		return pos,pot_signal,channels_labels
	
	#elabora el topoplot
	def plot_topomap(self,output,pot_signal,pos):
		from mne.viz import plot_topomap
		import matplotlib.pyplot as plt
		minn = min(pot_signal)
		maxx = max(pot_signal)
		plt.title('topomap')
		fig = plot_topomap(pot_signal, pos, cmap='jet', sensors='k.',contours=0, 
			image_interp='spline36' ,show = False,vmin = minn, vmax = maxx)
		plt.savefig(output)
		plt.show(fig)
		return fig

	def interpolation_object(self,pot_signal,pos,elec):
		import matplotlib.pyplot as plt
		from scipy.interpolate import griddata
		pot_interp = griddata(pos, pot_signal,elec, method='cubic',fill_value =0)
		return pot_interp

	def circle(self,pos,cz,radius):
		import numpy as np
		import math as mt
		for theta in range(100):
			arc = 2*mt.pi/100*theta
			x = cz[0] + radius*mt.cos(arc)
			y = cz[1] + radius*mt.sin(arc)
			coord = np.asarray([x,y])
			coord = coord.T
			pos = np.vstack((pos,coord))
		pos_interp = np.copy(pos)
		return pos_interp

	def mesh(self,pos):		
		from scipy.spatial import Delaunay
		import matplotlib.pyplot as plt
		tri = Delaunay(pos)
		faces = tri.simplices
		return faces

	def RGB(self,pot_signal):
		import matplotlib.pyplot as plt
		import matplotlib.colors as colors
		import matplotlib.cm as cmx
		import numpy as np
		jet = cm = plt.get_cmap('jet')
		cNorm  = colors.Normalize(vmin=min(pot_signal), vmax=max(pot_signal))
		scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
		colorVal = scalarMap.to_rgba(pot_signal)
		colorVAl = np.around(255*colorVal)
		return colorVAl

	def write_ply(self,ply_file,vertex,faces,colorVal):
		import numpy as np
		vertex_colorVal = np.hstack((vertex,colorVal))
		file = open(ply_file+".ply","w")
		file.write('''ply
			format ascii 1.0
			element vertex %d
			property float x
			property float y
			property float z
			property uchar red
			property uchar green
			property uchar blue
			element face %d
			property list uchar int vertex_index
			end_header\n'''
		%(len(vertex),len(faces)))
		for row in vertex_colorVal:
			file.write('%f %f %f %i %i %i \n' %(row[0],row[1], 0,row[2],row[3],row[4]))
		for row in faces:
			file.write('3 %i %i %i \n' %(row[0],row[1],row[2]))
		file.close()
		return file

	def interpolation_data(self,power,pos):
		import numpy as np
		import matplotlib.pyplot as plt
		from scipy.interpolate import interp2d
		x = np.linspace(-0.33,0.33,600)
		y = np.linspace(-0.33,0.33,600)

		power = interp2d(pos[:,0], pos[:,1], power,kind = 'linear')
		power = power(x,y)
		return power

	def turnoff(self,power,cz,radius):
		import numpy as np
		import scipy.spatial.distance as sp
		x = np.linspace(-0.36,0.36,600)
		y = np.linspace(-0.36,0.36,600)
		for m in range(len(x)):
			for n in range(len(y)):
				YY = np.vstack((cz,[x[m],y[n]]))
				dist = sp.pdist(YY)
				if dist >= radius:
					c = (m,n)
					power[c] = float('nan')
		return power
