from topoplot import edf_topoplot
ob = edf_topoplot()
archi,output,config = ob.argparse()
elec,labels_ref,cz,radius = ob.preparate_ref(config)
signal,nch,channels_labels = ob.read_edf(archi)
pot_signal = ob.calc_power(signal)

pos,pot_signal,channels_labels= ob.calc_positions(nch,channels_labels,elec,labels_ref,pot_signal)

pot_interp = ob.interpolation(pot_signal,pos,elec)

elec_with_circle = ob.circle(elec,cz,radius)
pot_interp_with_circle = ob.interpolation(pot_interp,elec,elec_with_circle)

fig = ob.topoplot(pot_interp,elec,labels_ref)
faces = ob.mesh(elec_with_circle) # malla de los electrodos de la muestra
colorVal = ob.RGB(pot_interp_with_circle)
file = ob.write_ply(output,elec_with_circle,faces,colorVal)



#python main_topo.py -i sujeto_base.edf -o fig3 -c config