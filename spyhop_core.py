# -*- coding: utf-8 -*-
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
def get_profile(fn):
    '''
    Reads in a profile, and sorts the information according to the Spyhop rules.
   
    :param: fn: {string} 
                The filename (+path!) to the profile to load.
                
    :returns: []                    
    '''  
    
    # Create some varables for the trajectory:
    
    trajectory = []
    sidetrack = []
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
        
        if items[2] in ['E','P','A']:
            trajectory.append(items)
        elif items[2] in ['S']:
            sidetrack.append(items)
        elif items[2] in ['T']:
            talks.append(items)
        else:
            sys.exit('Position type unknown: %s' % items[2])    
    
    trajectory.sort()
    sidetrack.sort()
    talks.sort()

    # Alright, now, turn this data into something we can plot
    trajectory_coords = np.zeros((len(trajectory),2))
    for (i,loc) in enumerate(trajectory):
        if loc[3] in known_locations.keys():
            trajectory_coords[i,0] = np.float(known_locations[loc[3]][1])
            trajectory_coords[i,1] = np.float(known_locations[loc[3]][2])
    
        else:
            print ' Use custom locations from file - not yet implemented'
     
                                        
    sidetrack_coords = np.zeros((len(sidetrack)*2,2))
    for (i,loc) in enumerate(sidetrack):
        st_year = np.int(loc[0])
        # Find where one was before the side track

        for (i,main_loc) in enumerate(trajectory[:-1]):
            if (np.int(main_loc[0])<= st_year) and (np.int(trajectory[i+1][0])>=st_year):
                sidetrack_coords[2*i,0] = trajectory_coords[i,0]
                sidetrack_coords[2*i,1] = trajectory_coords[i,1]
                sidetrack_coords[2*i+1,0] = np.float(known_locations[loc[3]][1])
                sidetrack_coords[2*i+1,1] = np.float(known_locations[loc[3]][2])
                
        # And then find where one was after the side track as well ?
    
    talks_coords = np.zeros((len(talks),2))
    for (i,loc) in enumerate(talks):
        if loc[3] in known_locations.keys():
            talks_coords[i,0] = np.float(known_locations[loc[3]][1])
            talks_coords[i,1] = np.float(known_locations[loc[3]][2])
    
        else:
            print ' Use custom locations from file - not yet implemented'                                                                      
                                                                                                              
                                                                                                                                                 
                                                                                                                                                                                                                       
    return [trajectory, sidetrack, talks, trajectory_coords, sidetrack_coords,
            talks_coords]                                                                                                            

# ------------------------------------------------------------------------------

def draw_map(profile_fn, profile_loc = '.', plot_format = 'pdf'):  
    '''
    Draw the map linked to a specific profile.
   
    :param: profile_fn: {string} 
                        Profile filename.
    :param: profile_loc: {string, default='.'}
                         Path to the profile
    :param: plot_fmt: {string, default='pdf'}
                         Any valid matplotlib format for exporting the figure.                         
                
    :returns: True                    
    '''     

    # First, create figure.
    plt.close(1)
    fig = plt.figure(1,figsize=(15,10))
    gs = gridspec.GridSpec(1,1, height_ratios=[1], width_ratios=[1])
    gs.update(left=0.05,right=0.95,bottom=0.05,top=0.95,
                    wspace=0.1,hspace=0.1) 

    ax1 = plt.subplot(gs[0,0])

    # Then, create a Basemap instance.
    m = Basemap(llcrnrlon=-180, llcrnrlat=-90, urcrnrlon=180, urcrnrlat=90, 
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
    m.drawmapscale(-7., -50, -7, -50, 5000, barstyle='fancy')
    
    
    # Get the data
    [trajectory, sidetrack, talks, trajectory_coords, sidetrack_coords, 
     talks_coords] = \
                    get_profile(os.path.join(profile_loc,profile_fn))
                    
    # And now draw the data: 
    # Main path
    for i in range(len(trajectory)-1):
        
        gc = m.drawgreatcircle(trajectory_coords[i,0],trajectory_coords[i,1],
                          trajectory_coords[i+1,0],trajectory_coords[i+1,1],
                          c='k', lw=2)
                          
        # In case we cross the map edge, let's make it look a bit prettier.
        # This is supposed to be fixed in Basemap 1.8
        # See http://stackoverflow.com/questions/13888566/python-basemap-drawgreatcircle-function
        this_path = gc[0].get_path()
        
        # find the index which crosses the dateline (the delta is large)
        cut_point = np.where(np.abs(np.diff(this_path.vertices[:, 0])) > 
                             5*np.median(np.diff(this_path.vertices[:,0])))[0]

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
                          
        m.plot(trajectory_coords[i,0],trajectory_coords[i,1],latlon=True, 
               marker=my_markers[trajectory[i][2]],
               c=my_colors[trajectory[i][2]],
               markersize = 10)
               
    # And let us not forget the last point:           
    m.plot(trajectory_coords[-1,0],trajectory_coords[-1,1],latlon=True, 
               marker=my_markers[trajectory[-1][2]],
               c=my_colors[trajectory[-1][2]],
               markersize = 10)
    
    
    # Side tracks
    for i in range(len(sidetrack)):
        gc = m.drawgreatcircle(sidetrack_coords[i*2,0],sidetrack_coords[i*2,1],
                          sidetrack_coords[i*2+1,0],sidetrack_coords[i*2+1,1],
                          c='k', lw=2, ls = '--')
                          
        # In case we cross the map edge, let's make it look a bit prettier.
        # This is supposed to be fixed in Basemap 1.8
        # See http://stackoverflow.com/questions/13888566/python-basemap-drawgreatcircle-function
        this_path = gc[0].get_path()
        
        # find the index which crosses the dateline (the delta is large)
        cut_point = np.where(np.abs(np.diff(this_path.vertices[:, 0])) > 
                             5*np.median(np.diff(this_path.vertices[:,0])))[0]

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
                          
        m.plot(sidetrack_coords[i*2+1,0],sidetrack_coords[i*2+1,1],latlon=True, 
               marker=my_markers['S'],
               c=my_colors['S'],
               markersize = 10)           
                                                                     
    # Talks
    for i in range(len(talks)):                                              
        m.plot(talks_coords[i,0],talks_coords[i,1],latlon=True, 
               marker=my_markers['T'],
               c=my_colors['T'],
               markersize = 8)          
               

    plt.show()
    
    # Save the figure
    plt.savefig(os.path.join(profile_loc,profile_fn[-4]+plot_format),bbox_inches='tight')
    
    return True