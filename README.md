# Topoplot

Topoplot : Script para el cálculo y visualización del topoplot de un paciente a partir de un archivo .edf

## Parámetros

__i__ : str. Nombre del archivo .edf que desea utilizar. Por defecto -i sujeto_base.edf

__o__ : str. Nombre y dirección para guardar el topoplot. Por defecto -o topoplot

__c__ : str. Nombre del archivo de configuración, éste debe incluir las siguientes dos variables: 

   labels: list de longitud número de electrodos. Incluye el nombre de los electrodos según el modelo que se desea utilizar, por default se utiliza el modelo New York.
   
   elec: numpy.ndarray de forma número de electrodos por ejes, en este caso 2. array con las coordenadas de los electrodos según el modelo que se desea utilizar, por default se utiliza el modelo New York.
   
Por defecto -c config

__f__ : str. tipo de formato de como se desea el topoplot, puede ser: 'image','object' o 'data'
   
## Métodos

### Imagen

Guarda una imagen .png. Por defecto topoplot.png

#### Ejemplo desde la consola

 python main_topo.py -i sujeto_base.edf -f image

### Objeto

guarda un objecto .ply. Por defecto topoplot.ply

#### Ejemplo desde la consola

 python main_topo.py -i sujeto_base.edf -f object

### Data

guarda el array de las potencias en cada nodo en .npy. Por defecto topoplot.npy

#### Ejemplo desde la consola

 python main_topo.py -i sujeto_base.edf -f data
