import argparse
from topoplot import edf_topoplot

#PARSE
parser = argparse.ArgumentParser()
parser.add_argument('-i','--archive', 
	help='nombre del archivo .edf que se desea utilizar')
parser.add_argument('-o','--figure', 
	help='ingresa la direccion para guardar el topoplot')
parser.add_argument('-c','--config',
	help='nombre del archivo de configuracion. NOTA: el nombre de la variable de las coordenadas debe ser elec y de la variable de las etiquetas labels ')
parser.add_argument('-f','--formatt', 
	help='indica cual es el formato de salida del topoplot,puede ser, image, object, data')
parsedargs = parser.parse_args()
archi = parsedargs.archive
output = parsedargs.figure
config  = parsedargs.config
formatt = parsedargs.formatt
if archi is None:		archi= 'sujeto_base.edf'
if output is None:		output = 'topoplot'
if config is None:		config = 'config'
if formatt is None:		formatt = 'image'

ob = edf_topoplot()

# da lectura al edf
signal,nch,labels = ob.read_edf(archi)

# calculo de la potencia de la senal
power = ob.power(signal)

# prepara las etiquetas y coordenadas del modelo de referencia del archivo config
elec,labels_ref,center,radius = ob.prepare(config)

# calculo de las posiciones de los electrodos de la medida
pos,power,labels= ob.positions(nch,labels,elec,labels_ref,power)

if formatt == 'image':
	# topoplot utilizando biblioteca mne
	fig = ob.plot_topomap(output,power,pos)

if formatt == 'object':
	# interpolacion con los electrodos de referencia
	power_interp = ob.interpolation_object(power,pos,elec)
	# elaboracion del borde circular por medio de nodos 
	elec_circle = ob.circle(elec,center,radius)
	# interpolacion con los nodos del borde
	power_interp = ob.interpolation_object(power_interp,elec,elec_circle)
	# elaboracion de malla y faces
	faces = ob.mesh(elec_circle)
	# jet to RGB
	powerRGB = ob.RGB(power_interp)
	# escritura del archivo .ply
	file = ob.write_ply(output,elec_circle,faces,powerRGB)

if formatt == 'data':
	import numpy as np
	import matplotlib.pyplot as plt
	pos[:,1] = pos[:,1] - center[1]
	center = [0,0]
	x = np.linspace(-0.33,0.33,600)
	y = np.linspace(-0.33,0.33,600)

	power_interp = ob.interpolation_data(power,pos)
	power_interp = ob.turnoff(power_interp,center,radius)
	im = plt.pcolormesh(x,y,power_interp, 
		vmin=np.min(power),vmax=np.max(power),cmap = 'jet')
	plt.scatter(pos[:,0],pos[:,1],c = 'k')
	plt.colorbar(im)
	np.save(output,power_interp)
	plt.show()
