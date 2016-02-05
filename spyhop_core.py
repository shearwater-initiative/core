# -*- coding: utf-8 -*-
#
# TODO:
# - find a workaround to draw the great circles properly when the map is centered
#   on something else than 0 ...
# - refine the connection rules between long-term spot and short term ones (e.g.
#   when the trasnition between two fixed spot is a short term visit)
# - add some statistics to the plot: countries visited, continents visited, 
#   total km migrated, etc ...
#
#
# If you find this code useful, please cite the corresponding paper
#
# Mapping the great migrations of astronomers with the Spyhop Initiative,
# Astronomy and Computing (2016).
#
# Copyright 2016 Frédéric Vogt (frederic.vogt -at- alumni.anu.edu.au)
#
# This file is part of the pyqz Spyhop Initiative module.
#
#   The Spyhop Initiative Python module is free software: you can redistribute 
#   it and/or modify it under the terms of the GNU General Public License as 
#   published by the Free Software Foundation, version 3 of the License.
#
#   The pyqz Python module is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along 
#   with the Spyhop Initiative module. 
#   If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.gridspec as gridspec


from spyhop_metadata import __version__
from spyhop_metadata import *
import spyhop_locations as sploc



# ------------------- Make the plots look good ---------------------------------
import matplotlib as mpl
# Use mathtext & Helvetica: avoid usetex for portability's sake ...
mpl.rc('font',**{'family':'sans-serif', 'serif':['Bitstream Vera Serif'], 
                 'sans-serif':['Helvetica'], 'size':20, 
                 'weight':'normal'})
mpl.rc('axes',**{'labelweight':'normal', 'linewidth':1})
mpl.rc('ytick',**{'major.pad':8, 'color':'k'})
mpl.rc('xtick',**{'major.pad':8, 'color':'k'})
mpl.rc('mathtext',**{'default':'regular','fontset':'cm', 
                     'bf':'monospace:bold'})
mpl.rc('text', **{'usetex':False})
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Some useful general variables
# ------------------------------------------------------------------------------
# For rapid identifications of the continents' locations variable
continent_keys = {'EU':sploc.locations_EU,
                 'NA':sploc.locations_NA,
                 'SA':sploc.locations_SA,
                 'As':sploc.locations_As,
                 'Oc':sploc.locations_Oc,
                 'An':sploc.locations_An,
                }
                
# Create a list with all the know locations                
known_locations = {}
for cont in continent_keys.keys():
    for loc in continent_keys[cont].keys():
        known_locations[loc] = np.append(continent_keys[cont][loc],cont)

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

# Plot the locations in the database
def show_locations(continent = 'all'):
    '''
    Shows the current state of the Spyhop database of universities and 
    research institutes.
   
    :param: continent: {string or list; default = 'all'} 
                        Whether to show 'all' locations, or for specific 
                        continents. E.g.: ['EU','NA','O']
    :returns: True                    
    '''                 
     
     
    # First, check what the user wants, with some safety checks   
    show_continent = []
        
    if type(continent) == str:
        if continent == 'all':
            for item in continent_keys.keys():  
                          
                show_continent.append(continent_keys[item])
        else:
            if not(continent in continents_keys.keys()):
                sys.exit('Continent key unknown. Must by any of %s.' %
                          continent_keys.keys())  
                            
            show_continent = [continent_keys[continent]]
            
    elif type(continent) == list:
        
        for item in continent:
            if not(item in continents_keys.keys()):
                sys.exit('Continent key unknown. Must by any of %s.' %
                          continent_keys.keys())  
                          
            show_continent.append(continent_keys[item])
    else:
        sys.exit('Continent format unknown. Must by str or list.')
        
      
    # Now, show it all if alphabetic order
    for cont in show_continent:
        print ' --- '
        for place in np.sort(cont.keys()):
            print place+':', cont[place][0], cont[place][1:] 
        print ' --- '
    return True
            
# ------------------------------------------------------------------------------

# Plot the locations in the database
def get_profile(fn, long_min):
    '''
    Reads in a profile, and sorts the information according to the Spyhop rules.
   
    :param: fn: {string} 
                The filename (+path!) to the profile to load.
    :param: long_min: the "cut" of the map
                
    :returns: []                    
    '''  
    
    # Create some varables for the trajectory:
    
    trajectory = []
    talks = []
    
    
    if not(os.path.isfile(fn)):
        sys.exit('No file found at %s.' % fn)
    
    p_file = open(fn, 'r')
    profile = p_file.readlines()
    p_file.close() 
    
    for line in profile:
        if line[0] == '#':
            continue
        
        items = line.split('\n')[0].split(',') 
        if len(items) != 6:
            sys.exit('Badly formatted profile step: %s' % line)
        
        if items[2] in ['E','P','A','S']:
            trajectory.append(items)
        elif items[2] in ['T']:
            talks.append(items)
        else:
            sys.exit('Position type unknown: %s' % items[2])    
    
    trajectory.sort()
    talks.sort()

    # Alright, now, turn this data into something we can plot
    # Main trajectory
    trajectory_coords = np.zeros((len(trajectory),2))
    for (i,loc) in enumerate(trajectory):
        if loc[3] in known_locations.keys():
            trajectory_coords[i,0] = np.float(known_locations[loc[3]][1])
            trajectory_coords[i,1] = np.float(known_locations[loc[3]][2])
    
        else:
            trajectory_coords[i,0] = np.float(loc[4])                                                                    
            trajectory_coords[i,1] = np.float(loc[5])        
    
    # Make sure it all falls on the map
    for i in range(len(trajectory_coords)):
        if trajectory_coords[i,0] < long_min:
                trajectory_coords[i,0] += 360.        
    
    # Talks and other visits
    talks_coords = np.zeros((len(talks),2))
    for (i,loc) in enumerate(talks):
        if loc[3] in known_locations.keys():
            talks_coords[i,0] = np.float(known_locations[loc[3]][1])
            talks_coords[i,1] = np.float(known_locations[loc[3]][2])
    
        else:
            talks_coords[i,0] = np.float(loc[4])                                                                      
            talks_coords[i,1] = np.float(loc[5]) 
            
    # make sure it all falls on the map        
    for i in range(len(talks_coords)):
        if talks_coords[i,0] < long_min:
            
                talks_coords[i,0] += 360.                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
    return [trajectory, talks, trajectory_coords, talks_coords]                                                                                                            
# ------------------------------------------------------------------------------
def drawgreatcircle_custom(m, long1,lat1,long2,lat2, **kwargs):
    '''
    A function that draws a great circle, and looks good if it crosses the edge
    of the map.
    
    :param m: the Basemap instance
    :param long1: the longitude of the starting point
    :param lat1: the latitude of the starting point
    :param long2: the longitude of the final point
    :param lat2: the latitude of the final point
    '''
    
    gc = m.drawgreatcircle(long1, lat1, long2, lat2,
                          **kwargs)
                          
    # In case we cross the map edge, let's make it look a bit prettier.
    # This is supposed to be fixed in Basemap 1.8
    # See http://stackoverflow.com/questions/13888566/python-basemap-drawgreatcircle-function
    this_path = gc[0].get_path()
        
    # find the index which crosses the dateline (the delta is large)
    cut_point = np.where(np.abs(np.diff(this_path.vertices[:, 0])) > 
                         np.abs(10*np.median(np.diff(this_path.vertices[:,0]))))[0]

    if len(cut_point>0):
        cut_point = cut_point[0]
        # create new vertices with a nan inbetween and set those as 
        # the path's vertices
        new_verts = np.concatenate( [this_path.vertices[:cut_point, :], 
                                    [[np.nan, np.nan]], 
                                    this_path.vertices[cut_point+1:, :]]
                                   )
        this_path.codes = None
        this_path.vertices = new_verts


# ------------------------------------------------------------------------------

def draw_map(profile_fn, profile_loc = '.', plot_format = 'png',
             long_mid=0):  
    '''
    Draw the map linked to a specific profile.
   
    :param: profile_fn: {string} 
                        Profile filename.
    :param: profile_loc: {string, default='.'}
                         Path to the profile
    :param: plot_fmt: {string, default='pdf'}
                         Any valid matplotlib format for exporting the figure.
    :param: long_mid: {float, default=-170}
                       The mean longitude of the map, i.e. where to "center it"                                              
                
    :returns: True                    
    '''     

    # First, create figure.
    plt.close(1)
    fig = plt.figure(1,figsize=(15,10))
    gs = gridspec.GridSpec(1,1, height_ratios=[1], width_ratios=[1])
    gs.update(left=0.05,right=0.95,bottom=0.05,top=0.95,
                    wspace=0.1,hspace=0.1) 

    ax1 = plt.subplot(gs[0,0])

    long_min = long_mid - 180.

    # Then, create a Basemap instance.
    m = Basemap(llcrnrlon=long_min, llcrnrlat=-90, urcrnrlon=long_min+360.,
                urcrnrlat=90,
                #lon_0 = 150,lat_0=0,
                projection='mill', ax = ax1)

    # Update the map to give that 'Spyhop feel' ...
    m.drawcoastlines(linewidth=.8,color='w')
    m.drawcountries(color='w')
    m.drawmapboundary(fill_color='w')
    m.fillcontinents(color='0.8',lake_color='w')
    #m.drawrivers(color='steelblue')
    m.drawparallels(np.linspace(-90,90,num=7),labels=[1,1,0,0],
                    color='0.8', dashes=[5,5])
    m.drawmeridians(np.linspace(0,360,13),labels=[0,0,0,1], 
                    color='0.8',dashes=[5,5])
    m.drawmapscale(long_mid, -80, long_mid, -80, 5000, barstyle='fancy')
    
    
    # Get the data
    [trajectory, talks, trajectory_coords, talks_coords] = \
                    get_profile(os.path.join(profile_loc,profile_fn), long_min)                  
                                                  
    # And now draw the data: 
    # Main path
    main_track = [loc for loc in trajectory if loc[2] !='S']
    side_track = [loc for loc in trajectory if loc[2] == 'S']
    
    for i in range(len(main_track)-1):
        
        k1 = trajectory.index(main_track[i])
        k2 = trajectory.index(main_track[i+1])
       
        drawgreatcircle_custom(m,
                               trajectory_coords[k1,0],trajectory_coords[k1,1],
                               trajectory_coords[k2,0],trajectory_coords[k2,1],
                               c='k', lw=2, ls = '-')
                               
    for i in range(len(side_track)):
        
        k1 = trajectory.index(side_track[i])
        st_year0 = np.float(side_track[i][0])
        
        
        for (j,mt) in enumerate(main_track):
            if (np.float(mt[0])<= st_year0) and (np.float(mt[1])>= st_year0) : 
            
                k2 = trajectory.index(main_track[j])
                                                            
                drawgreatcircle_custom(m,
                               trajectory_coords[k1,0],trajectory_coords[k1,1],
                               trajectory_coords[k2,0],trajectory_coords[k2,1],
                               c='k', lw=1, ls = '--')    
                pass                                                                  
                          
    # Plot the symbols for each location on the track 
    for i in range(len(trajectory)): 
        
        x,y = m(trajectory_coords[i,0],trajectory_coords[i,1])                                                              
        m.plot(x,y, 
               marker=my_markers[trajectory[i][2]],
               c=my_colors[trajectory[i][2]],
               markersize = 10)
                                                                          
    # Talks
    for i in range(len(talks)):  
        x,y = m(talks_coords[i,0],talks_coords[i,1])                                            
        m.plot(x,y,
               marker=my_markers['T'],
               c=my_colors['T'],
               markersize = 10)          
               

    plt.show()
    
    # Save the figure
    plt.savefig(os.path.join(profile_loc,profile_fn[:-3]+plot_format),bbox_inches='tight')
    
    return True