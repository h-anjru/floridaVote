# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 14:04:09 2016

@author: h-anjru
"""

from urllib.request import urlopen
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import time
import matplotlib.cbook as cbook
from scipy.misc import imread
import locale

# download reports
vm = urlopen('http://fvrselectionfiles.elections.myflorida.com/countyballotreportfiles/Stats_10282_AbsVoted.txt')
ve = urlopen('http://fvrselectionfiles.elections.myflorida.com/countyballotreportfiles/Stats_10282_EarlyVoted.txt')

# save downloaded files, you know, because
path = 'D:\\Dropbox\\Personal\\Python\\floridaVote\\'
os.chdir(path)
vm_txt = path+'from_state\\absVoted_'+time.strftime('%m%d')+'.txt'
f = open(vm_txt,'wb')
f.write(vm.read())
f.close()
ve_txt = path+'from_state\\earlyVoted_'+time.strftime('%m%d')+'.txt'
f = open(ve_txt,'wb')
f.write(ve.read())
f.close()

# text file of county centroids (lat/lon)
dots = path+'countyCentroids.txt'

def readdata( file ):
    "Reads data from text into arrays"
    f = open(file)
    with f as myfile:
        data = myfile.readlines()      
    for x in range(0,len(data)):
        data[x] = re.split(r'\t+',data[x].rstrip('\t')) # split string @ tab
        for z in range(5,10):
            data[x][z] = data[x][z].replace(',','') # strip commas
    f.close()
    return data
def differencing( data ):
    "Returns difference of Dem - Rep"    
    diff = [] # initialize
    for y in range(2,len(data)):         
        diff.append(int(data[y][6]) - int(data[y][5]))
    return diff
      
def column(matrix, i):
    "grab a single column from a matrix"
    return [row[i] for row in matrix]

    
# call functions above, get useable data, convert diff to array
mail = readdata(vm_txt)
early = readdata(ve_txt)
mail_diff = np.array(differencing(mail))
early_diff = np.array(differencing(early))

diff = mail_diff + early_diff

# grab totals from line 1 of mail and early
tot_m = mail[1][5:10]
tot_e = early[1][5:10]

tot_m = [int(i) for i in tot_m]
tot_e = [int(i) for i in tot_e]

dem = tot_m[1] + tot_e[1]
rep = tot_m[0] + tot_e[0]
oth = tot_m[2] + tot_e[2]
npa = tot_m[3] + tot_e[3]
tot = tot_m[4] + tot_e[4]

when = mail[1][10] # date grabbed from file
when = when.replace('\n','')
when = when.replace('  ',' ') # date formatted for plot
when2 = when.replace('/','')
when2 = when2.replace(' ','_')
when2 = when2.replace(':','') # date formatted for filename

# convert centroids of counties into arrays for plotting
f = open(dots)
with f as myfile:
    data = myfile.readlines()
for x in range(0,len(data)):
    data[x] = re.split(r'\t+',data[x].rstrip('\t'))
    data[x][2] = data[x][2].replace('\n','')
    
c = np.array(data) 
x_c = column(c,1)
scl = 1.18 # scale factor to square up the map
y_c = column(c,2)
y_c = [float(i) * scl for i in y_c] # scale up the lats

# size array from diff: area = f(abs(diff[x]))
scale = 0.15 # tinker with this
area = np.pi * (scale * np.sqrt(abs(diff)))**2

# color array from diff: 1=blue, -1=red
colors = np.sign(diff)
colors = np.array(colors).tolist()
for x in range(0,len(colors)):
    if colors[x] == 1:
        colors[x] = 'blue'
    else:
        colors[x] = 'red'

# plot results
locale.setlocale(locale.LC_ALL,'');

def set( num ):
    "Adds 1000s separator (,) to numbers"
    out = locale.format('%d',num,grouping=True)
    return out

datafile = cbook.get_sample_data(path+'assets\\countyMap.png') # background image
img = imread(datafile)
fig = plt.figure(frameon=False)
fig.set_size_inches(10,9)
plt.scatter(x_c, y_c, zorder=1, s=area, c=colors, alpha = 0.5)
plt.axis([-88,-79,24.8*scl,31.2*scl])
plt.axis('off')
plt.imshow(img,zorder=0,extent=[-88.3,-79.35,24.5*scl,31.1*scl])
plt.annotate('Ballots by party (mail) (early)',
             xy=(-88,scl*27.4),fontsize=13)
plt.annotate('Thru '+when,
             xy=(-88,scl*27.2),fontsize=8)
plt.annotate('Dem: '+
             set(dem)+', '+str(round(100*dem/tot,1))+'% '+
             '('+set(tot_m[1])+', '+str(round(100*tot_m[1]/tot_m[4],1))+'%) '+
             '('+set(tot_e[1])+', '+str(round(100*tot_e[1]/tot_e[4],1))+'%) ',
             xy=(-88,scl*27),fontsize=9)
plt.annotate('Rep: '+
             set(rep)+', '+str(round(100*rep/tot,1))+'% '+
             '('+set(tot_m[0])+', '+str(round(100*tot_m[0]/tot_m[4],1))+'%) '+
             '('+set(tot_e[0])+', '+str(round(100*tot_e[0]/tot_e[4],1))+'%) ',
             xy=(-88,scl*26.8),fontsize=9)
plt.annotate('Other: '+
             set(oth)+', '+str(round(100*oth/tot,1))+'% '+
             '('+set(tot_m[2])+', '+str(round(100*tot_m[2]/tot_m[4],1))+'%) '+
             '('+set(tot_e[2])+', '+str(round(100*tot_e[2]/tot_e[4],1))+'%) ',
             xy=(-88,scl*26.6),fontsize=9)
plt.annotate('NPA: '+
             set(npa)+', '+str(round(100*npa/tot,1))+'% '+
             '('+set(tot_m[3])+', '+str(round(100*tot_m[3]/tot_m[4],1))+'%) '+
             '('+set(tot_e[3])+', '+str(round(100*tot_e[3]/tot_e[4],1))+'%) ',
             xy=(-88,scl*26.4),fontsize=9)
plt.annotate('Total: '+
             set(tot)+' '+
             '('+set(tot_m[4])+') '+
             '('+set(tot_e[4])+') ',
             xy=(-88,scl*26.2),fontsize=10,weight='bold')
plt.annotate('Created by @h_anjroo',
             xy=(-88,scl*25),fontsize=7)
plt.annotate('Source: https://countyballotfiles.elections.myflorida.com/FVRSCountyBallotReports/AbsenteeEarlyVotingReports/PublicStats',
             xy=(-88,scl*24.8),fontsize=7)
plt.savefig('pngs\\voting_thru_'+when2+'.png',
            dpi=200, bbox_inches='tight')


# counties report
def totals( report ):
    "Reads the lists, returns arrays of totals"
    data = []
    for i in range(0,len(report)):
        data.append(report[i][9])
    data = data[2:]
    data = [int(i) for i in data]
    data = np.array(data)
    return data
    
mail_county = totals(mail)
early_county = totals(early)

# array of county names
names = column(c,0)
names = np.array(names)

# generate Excel spreadsheet
header = np.array(('County','VBM','EIP','Total','D - R'))
report = np.vstack((names,mail_county,early_county,mail_county+early_county,diff)).T
report = np.vstack((header.T,report))
np.savetxt('reports\\'+when2+'_report.csv',report,delimiter=',',fmt='%s')