
from fileinput import filename
import os
import shutil
import hardpotato as hp
import numpy as np
import pandas as pd
from numpy import savetxt
import scipy
from scipy import stats
import matplotlib.pyplot as plt



##define path where all current folders are located
parent_path = 'C:/Users/mapence2/Desktop/data/2023_05_24/expt5'

num_folders = 9
num_experiments = 1

###this defines the order of concentrations by importing "shuffed_order.txt"
with open(f'{parent_path}/shuffled_order.txt') as file:
    mix_to_conc = [float(line.rstrip()) for line in file]


##make output path
subfolders = os.listdir(parent_path)
if 'output' in subfolders:
    print('Output exists already, not creating')
    output = f'{parent_path}/output'
else:
    directory = 'output'
    path = os.path.join(parent_path, directory)
    os.mkdir(path)
    print("Directory '% s' created" % directory)
    output = f'{path}'

folder_name = 'mix'
### outer loop 'i' identifies all folders for defined naming scheme, and list files
for i in range(num_folders):
#### inner loop 'j' goes through listed files and copies them to output path, removing any none txt files, and not copying over new ones if they exist
    for j in os.listdir(f'{parent_path}/{folder_name}_{i+1}'):
        if f'{parent_path}/{folder_name}_{i+1}/{j}'.endswith('.txt'):
            if not f'{i+1}_{j}' in os.listdir(output):
                shutil.copy2(f'{parent_path}/{folder_name}_{i+1}/{j}', output)
                os.rename(f'{output}/{j}',f'{output}/{i+1}_{j}')

###setup pstat
model = 'chi760e'
path = 'C:/Users/mapence2/Desktop/pstats/chi760e/chi760e.exe'
folder = output
hp.potentiostat.Setup(model=model, path=path, folder=folder)

###conc function, part= experiment in cycle, total = total cycles
def conc_fxn(conc_a, conc_b, part, total):
    conc_value = (conc_b*((total)-part)+conc_a*(part))/(total)
    return conc_value

######################## CVs ################
data_frame_CV = []
data_frame_IT = []

for x in range(num_folders):
    for y in range(num_experiments):
        #CVs to dataframe
        #print(conc_fxn(1,500,x,num_folders))
        filename_CV = f'{x+1}_CV_{y+1}.txt'
        data_CV = hp.load_data.CV(filename_CV,folder,model)
        potential_CV = data_CV.E
        current_CV = data_CV.i[:,0].transpose()
        df_CV = pd.DataFrame(data = {'Filename' : filename_CV, 'Concentration / mM' : conc_fxn(1,500,mix_to_conc[x],1500),
                                    'Potential Data' : [potential_CV], 'Current Data' : [current_CV], 'Min Current / A' : np.amin(data_CV.i),
                                    'Max Current / A' : np.amax(data_CV.i), 'Run' : y+1})
        data_frame_CV.append(df_CV)
        ###IT to dataframe
        filename_IT = f'{x+1}_IT_{y+1}.txt'
        data_IT = hp.load_data.CA(filename_IT,folder,model)
        time_IT = data_IT.t
        current_IT = data_IT.i
        df_IT = pd.DataFrame(data = {'Filename' : filename_IT, 'Concentration / mM' : conc_fxn(1,500,mix_to_conc[x],1500),
                                    'Time Data' : [time_IT], 'Current Data' : [current_IT], 'Steady State' : np.mean(data_IT.i[-10:-1]), 'Run' : y+1})
        data_frame_IT.append(df_IT)

fulldata_CV = pd.concat(data_frame_CV, ignore_index=True)
fulldata_IT = pd.concat(data_frame_IT, ignore_index=True)
fulldata_CV.to_csv(path_or_buf=f'{output}/dataframe_CV.csv')
fulldata_IT.to_csv(path_or_buf=f'{output}/dataframe_IT.csv')


fontinfo = {'fontsize': 'x-large'}



## plot the steady state current as function of concentration
plt.figure()
lim_current = fulldata_IT.loc[(fulldata_IT['Run'] == num_experiments), 'Steady State']*1e12
lim_current = lim_current.values.tolist()
conc_plot = fulldata_IT.loc[(fulldata_IT['Run'] == num_experiments), 'Concentration / mM']
X = lim_current
Y = conc_plot
a = [x for _, x in sorted(zip(Y, X))]
b = sorted(Y)
plt.plot(b, a, linestyle = ':', marker='o', markerfacecolor='w', markeredgecolor='k')
plt.xlabel('[TBAPF6] / mM',fontdict=fontinfo)
plt.ylabel('i / pA',fontdict=fontinfo)
for i in range(num_folders):
    plt.text(conc_plot[i]*1.01, lim_current[i]*1.01, f'#{i+1}')
plt.tight_layout()
plt.savefig(f'{output}/concplot.png')
plt.close()


plt.figure()
current = fulldata_CV.loc[(fulldata_IT['Run'] == num_experiments), 'Current Data']*1e9
current = current.values.tolist()
potential = fulldata_CV.loc[(fulldata_IT['Run'] == num_experiments), 'Potential Data']
potential = potential.values.tolist()
print(current)
legend = []
for i in range(num_folders):
    legend.append(f'{conc_fxn(1,500,mix_to_conc[i],1500):.1f} mM')
    plt.plot(potential[i],current[i])
plt.xlabel('potential / V',fontdict=fontinfo)
plt.ylabel('i / nA',fontdict=fontinfo)
plt.legend(legend)
plt.tight_layout()
plt.savefig(f'{output}/cvs.png')
plt.close()