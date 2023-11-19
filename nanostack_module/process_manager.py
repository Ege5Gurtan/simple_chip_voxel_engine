import importlib.util
import os
import threading
import multiprocessing
import psutil
import time
from functools import partial
import numpy as np

from nanostack_module import grid_manager as gm
from nanostack_module import input_file_manager as ifm

def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_if_grid_cube_has_material(cube):
    if not(cube == None):
        if not(cube.material == None):
            return True
    else:
        return False


class Deposition():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material =  material
        self.resist_type = None
        self.order = order
        self.name = 'Deposition'
    
class Exposure():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material = material
        self.order = order
        self.name = 'Exposure'

class Development():
    def __init__(self,cubes,order):
        self.cubes = cubes
        self.order = order
        self.name = 'Development'
        
class Etching():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material = material
        self.order = order
        self.name = 'Etch'


class Polishing():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material = material
        self.order = order
        self.name = 'Polish'
        
class Doping():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material = material
        self.order = order
        self.name = 'Dope'

class Diffusion():
    def __init__(self,cubes,diffusion_material,diffusion_medium_material,order):
        self.cubes = cubes
        self.diffusion_material = diffusion_material
        self.diffusion_medium_material = diffusion_medium_material
        self.order = order
        self.name = 'Diffuse'

class SpinCoating():
    def __init__(self,cubes,resist_material,resist_type,order):
        self.cubes = cubes
        self.resist_material = resist_material
        self.order = order
        self.name = 'SpinCoat'
        self.resist_type = resist_type


def Grid_SpinCoat(grid,material_name,resist_type,resist_thickness=1):
    surface_height_map = grid.get_top_surface_heights().values()
    surface_height_min_level = min(surface_height_map)
    surface_height_max_level = max(surface_height_map)
    deposition_amount = surface_height_max_level - surface_height_min_level
    spin_coated_resist_cubes = Grid_Deposit(deposition_amount,grid,material_name)
    Grid_Polish(material_name,grid)
    spin_coated_resist_cubes = spin_coated_resist_cubes + Grid_Deposit(resist_thickness,grid,material_name)
    
    
    return spin_coated_resist_cubes
    
def Grid_Deposit(thickness,grid,material_name):
    deposited_cubes = []
    for column_index in range(0,grid.grid_num_columns):
        column = grid.grid_select_column(column_index)
        number_of_deposited_cubes = 0
        for grid_cube in column:
            grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
            if number_of_deposited_cubes < thickness:
                deposit = False
                cube_index = grid.grid_cube_indices[grid_cube]
                bottom_neighbour_index = cube_index-1
                
                if grid_cube in grid.grid_surfaces_xy['surface_xy0']:
                    bottom_neighbour_index = None
                
                bottom_neighbour_grid_cube = grid.grid_select_cube(bottom_neighbour_index)
                
                bottom_grid_cube_has_material = check_if_grid_cube_has_material(bottom_neighbour_grid_cube)
                grid_cube_itself_has_material = check_if_grid_cube_has_material(grid_cube)
                
                if bottom_grid_cube_has_material and not(grid_cube_itself_has_material):
                    deposit = True
                elif bottom_neighbour_grid_cube == None and not(grid_cube_itself_has_material):
                    deposit = True
                
                if deposit:
                    grid_cube.material = material_name
                    number_of_deposited_cubes +=1
                    deposited_cubes.append(grid_cube)
                    grid.grid_cube_history[grid_cube][-1] = material_name

    return deposited_cubes
    

def Grid_Expose_Pattern_v2(grid,material_to_expose,pattern_df):
    exposed_indices = []
    counter = 0
    grid_size_z = grid.num_z
    for column in pattern_df:
        for index, value in enumerate(pattern_df[column]):
            if not(value == None):
                exposed_indices.append(counter)
            counter = counter +1

    
    exposed_cubes = []
    top_resist_layer_cubes = []
    
    top_surface_cubes_dict = grid.get_top_surface_cubes_with_material()
    top_surface_cubes_to_expose = []
    for column_name in top_surface_cubes_dict:
        cube = top_surface_cubes_dict[column_name]
        if cube.material == material_to_expose:
            top_surface_cubes_to_expose.append(cube)
    
    top_surface_cubes_dict_reversed = {v: k for k, v in top_surface_cubes_dict.items()}
    
    
    exposed_column_names = []
    if len(top_surface_cubes_to_expose) > 0:
    
        for i in exposed_indices:    
            exposed_cube = top_surface_cubes_to_expose[i]
            exposed_cube.material = material_to_expose+'_exposed'
            exposed_cube.is_exposed = True
            exposed_cubes.append(exposed_cube)
            column_name = top_surface_cubes_dict_reversed[exposed_cube]
            exposed_column_names.append(column_name)
        
        for exposed_column_name in exposed_column_names:
            for cube in grid.grid_all_columns[exposed_column_name]:
                if cube.material == material_to_expose:
                    cube.material = material_to_expose+'_exposed'
                    cube.is_exposed = True
                    if not(cube in exposed_cubes):
                        exposed_cubes.append(cube)
        
        #import pdb;pdb.set_trace();
                    
            
        for grid_cube in grid.grid_cubes:
            
            if grid_cube in exposed_cubes:
                grid.grid_cube_history[grid_cube].append(grid_cube.material)
            else:
                grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
  
    return exposed_cubes
 

def Grid_Develop_Pattern(resist_layer_cubes,material_name_to_develop,grid,resist_type='positive'):
    developed_cubes = []
    print('Resist type is: '+resist_type)
    for grid_cube in resist_layer_cubes:
        if resist_type == 'positive':
            if not(grid_cube.material == None) and (material_name_to_develop+'_exposed' == grid.grid_cube_history[grid_cube][-1]):
                grid_cube.material = None
                grid_cube.is_exposed = False
                developed_cubes.append(grid_cube)
                
           
        elif resist_type== 'negative':
            if not(grid_cube.material == None) and material_name_to_develop==grid_cube.material:
                grid_cube.material = None
                developed_cubes.append(grid_cube)
              
        else:
            print('Please specify resist_type as positive or negative')
            
    for grid_cube in grid.grid_cubes:
        if grid_cube in developed_cubes:
            grid.grid_cube_history[grid_cube].append('empty')
        else:
            grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
            

    return developed_cubes
            

def Remove_Cube_Material_Content(cubes,grid):
    removed_cubes = []
    for cube in cubes:
        cube.data.materials.clear()### add empty material instead
        removed_cubes.append(cube)
        grid.cube_history[cube].append('empty')
    cubes = gm.get_layer_difference(cubes,removed_cubes)
    return removed_cubes
        

def Grid_Etch(materials_to_etch,grid,etch_depth=100000000000):
    etched_cubes = []
    grid_size_z = grid.num_z
    #materials_to_etch = ['nitride','SIO2']
    #Etch(materials_to_etch,grid)
    for column in grid.grid_all_columns:
        column_cubes = grid.grid_all_columns[column]
        etched_cube_amount = 0
        for grid_cube in column_cubes[::-1]:
            grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
            cube_index = grid.grid_cube_indices[grid_cube]

            ##if cube itself has material to be etched and it above neighbour is empty            
            neighbour_z_cube_index = cube_index+1
            
            if grid_cube in grid.grid_surfaces_xy['surface_xy'+str(grid_size_z-1)]:
                neighbour_z_cube_index = None

            neighbour_z_cube = grid.grid_select_cube(neighbour_z_cube_index)
            
            top_has_material = check_if_grid_cube_has_material(neighbour_z_cube)
            cube_has_material =  check_if_grid_cube_has_material(grid_cube)
            name = grid_cube.material
            if not(name==None) and '_exposed' in name:
                #import pdb;pdb.set_trace();
                name = name.replace('_exposed',"")
                #import pdb;pdb.set_trace();

            if not(top_has_material) and cube_has_material and etched_cube_amount<etch_depth:
                for material_name in materials_to_etch:
                    if material_name in name: #or (material_name in name+'_exposed'):
                        grid_cube.material = None
                        grid_cube.is_exposed = False
                        etched_cubes.append(grid_cube)
                        grid.grid_cube_history[grid_cube][-1] = 'empty'
                        etched_cube_amount = etched_cube_amount + 1

    return etched_cubes

def Grid_Polish(material_to_polish,grid):
    polished_cubes = []
    for xy_surface in reversed(grid.grid_surfaces_xy):
        surface_cubes = grid.grid_surfaces_xy[xy_surface]
        found_materials = []
        for grid_cube in surface_cubes:
            material =  grid_cube.material
            found_materials.append(material)
        
        
        found_materials_without_none = [item for item in found_materials if item is not None]
        layer_to_remove = all(material_to_polish in item for item in found_materials_without_none)
        #import pdb;pdb.set_trace();
        if layer_to_remove:
            for grid_cube in surface_cubes:
                grid_cube.material = None
                polished_cubes.append(grid_cube)
        else:
            break
        
    for column in grid.grid_all_columns:
        column_cubes = grid.grid_all_columns[column]
        for grid_cube in column_cubes:
            if grid_cube in polished_cubes:
                grid.grid_cube_history[grid_cube].append('empty')
            else:
                #import pdb;pdb.set_trace();
                grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
    
    return polished_cubes

def Grid_Dope(doping_material,materials_to_dope,grid,doping_depth=2):
    doped_cubes = []
    grid_size_z = grid.num_z
    #materials_to_etch = ['nitride','SIO2']
    #Etch(materials_to_etch,grid)
    for column in grid.grid_all_columns:
        column_cubes = grid.grid_all_columns[column]
        doped_cube_amount = 0
        for grid_cube in column_cubes[::-1]:
            grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
            cube_index = grid.grid_cube_indices[grid_cube]

            ##if cube itself has material to be etched and it above neighbour is empty            
            neighbour_z_cube_index = cube_index+1
            if grid_cube in grid.grid_surfaces_xy['surface_xy'+str(grid_size_z-1)]:
                neighbour_z_cube_index = None
            neighbour_z_cube = grid.grid_select_cube(neighbour_z_cube_index)
            
            top_has_material = check_if_grid_cube_has_material(neighbour_z_cube)
            cube_has_material =  check_if_grid_cube_has_material(grid_cube)
            if top_has_material:
                neighbour_z_cube_material_name = neighbour_z_cube.material
                if neighbour_z_cube_material_name == doping_material:
                    top_has_material = False
                    
            name = grid_cube.material
            if not(top_has_material) and cube_has_material and doped_cube_amount<doping_depth:
                for material_name in materials_to_dope:
                    if material_name in name:                         
                        grid_cube.material = doping_material
                        doped_cubes.append(grid_cube)
                        grid.grid_cube_history[grid_cube][-1] = doping_material
                        doped_cube_amount = doped_cube_amount + 1
    
    return doped_cubes
   
def Grid_Diffuse_xy(diffusion_material,diffusion_medium_material,grid,diffusion_radius):
    diffused_cubes = []
    for grid_cube in grid.grid_cubes:
        if grid_cube.material == diffusion_material:
            diffused_cube_index_pairs = gm.circular_grid_selector(grid.num_x,grid.num_y, grid_cube.index_x+1,grid_cube.index_y+1,diffusion_radius)
            xy_plane_grid_cubes = grid.grid_surfaces_xy['surface_xy'+str(grid_cube.index_z)]
            for cube_to_diffuse in xy_plane_grid_cubes:
                for index_pair in diffused_cube_index_pairs:
                    if cube_to_diffuse.index_x == index_pair[0]-1 and cube_to_diffuse.index_y == index_pair[1]-1:
                        if cube_to_diffuse.material == diffusion_medium_material:
                            if cube_to_diffuse not in diffused_cubes:
                                diffused_cubes.append(cube_to_diffuse)
    for diffused_cube in diffused_cubes:
        diffused_cube.material = diffusion_material
        grid.grid_cube_history[diffused_cube][-1] = diffusion_material
                                
    return diffused_cubes
    
def Grid_Diffuse_x(diffusion_material,diffusion_medium_material,grid,diffusion_amount):
    diffused_cubes = []
    for grid_cube in grid.grid_cubes:
        if grid_cube.material == diffusion_material:
            cube_index = grid.grid_cube_indices[grid_cube]
            for i in range(0,int(diffusion_amount)+1):
                neighbour_x_cube_index = cube_index + grid.num_z*grid.num_y*i
                neighbour_minus_x_cube_index = cube_index - grid.num_z*grid.num_y*i
                neighbour_x_cube = grid.grid_select_cube(neighbour_x_cube_index)
                neighbour_minus_x_cube = grid.grid_select_cube(neighbour_minus_x_cube_index)
                if neighbour_x_cube.material == diffusion_medium_material:
                    diffused_cubes.append(neighbour_x_cube)
                if neighbour_minus_x_cube.material == diffusion_medium_material:
                    diffused_cubes.append(neighbour_minus_x_cube)
    
    for diffused_cube in diffused_cubes:
        diffused_cube.material = diffusion_material
        grid.grid_cube_history[diffused_cube][-1] = diffusion_material
    
    return diffused_cubes
                

def Grid_Diffuse_y(diffusion_material,diffusion_medium_material,grid,diffusion_amount):
    diffused_cubes = []
    for grid_cube in grid.grid_cubes:
        if grid_cube.material == diffusion_material:
            cube_index = grid.grid_cube_indices[grid_cube]
            for i in range(0,int(diffusion_amount)+1):
                neighbour_y_cube_index = cube_index + grid.num_z*i
                neighbour_minus_y_cube_index = cube_index - grid.num_z*i
                neighbour_y_cube = grid.grid_select_cube(neighbour_y_cube_index)
                neighbour_minus_y_cube = grid.grid_select_cube(neighbour_minus_y_cube_index)
                if neighbour_y_cube.material == diffusion_medium_material:
                    diffused_cubes.append(neighbour_y_cube)
                if neighbour_minus_y_cube.material == diffusion_medium_material:
                    diffused_cubes.append(neighbour_minus_y_cube)
    
    for diffused_cube in diffused_cubes:
        diffused_cube.material = diffusion_material
        grid.grid_cube_history[diffused_cube][-1] = diffusion_material
    
    return diffused_cubes                    
            
            
            
            
            