import copy
import importlib.util
import os
import pandas as pd

from nanostack_module import input_file_manager as ifm
from nanostack_module import process_manager as pm

def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
    
#ifm = include_module('input_file_manager.py')
#pm = include_module('process_manager.py')

def construct_active_processes(df,grid):
    processes = []
    grid_states = []

    df = ifm.add_optional_column(df,'Resist_Type','')
    df = ifm.add_optional_column(df,'Pattern','')    
    df = ifm.add_optional_column(df,'Show_Step',0)
    df = ifm.add_optional_column(df,'Material_to_Dope','')
    df = ifm.add_optional_column(df,'Diffusion_Medium','')
    df = ifm.add_optional_column(df,'Diffusivity',1)
    df = ifm.add_optional_column(df,'Feature_Layer','')
    df = ifm.add_optional_column(df,'Grid_Layer','')
    
    df = ifm.get_active_processes_df(df)
    
    executed_processes = []
    for i in df.index.tolist():
        
       #mandatory columns
       process = df.loc[i, "Process"]
       thickness = df.loc[i, "Thickness"]
       material_name =  df.loc[i, "Material"]
    
       #optional columns
       resist_type = df.loc[i,'Resist_Type']
       path = df.loc[i,'Path']
       show_step = df.loc[i,'Show_Step']
       material_to_dope = df.loc[i,"Material_to_Dope"]
       diffusion_medium_material = df.loc[i,"Diffusion_Medium"]
       diffusivity = df.loc[i,"Diffusivity"]
       feature_layer_name = df.loc[i,"Feature_Layer"]
       grid_layer_name = df.loc[i,"Grid_Layer"]
       
       process_order = i+2
       
       if process == 'Deposit':
           deposited_cubes = pm.Grid_Deposit(int(thickness),grid,material_name)
           current_process  = pm.Deposition(deposited_cubes,material_name,process_order)
           if not(resist_type == ''):
            current_process.resist_type = resist_type
            
       elif process == 'Expose':
            last_operation = executed_processes[-1]
            #cubes_to_expose = last_operation.cubes
            #material_name = 'exposed'
            file_name, file_extension = os.path.splitext(path)
            if file_extension == '.oas': 
                pattern_df = ifm.create_pattern_df_from_oas(path,feature_layer_name,grid_layer_name)
            else:
                pattern_df = pd.read_csv(path)
            pattern_df = ifm.reshape_pattern_df(pattern_df,grid.num_y,grid.num_x)
            exposed_cubes = pm.Grid_Expose_Pattern_v2(grid,material_name,pattern_df)
            current_process = pm.Exposure(exposed_cubes,material_name,process_order)
       elif process == 'Develop':
            last_operation = executed_processes[-1] ##exposure
            last_operation_before_exposure = executed_processes[-2] #resist deposition before exposure
            resist_type = last_operation_before_exposure.resist_type
            exposed_material = last_operation.material #exposed material
            developed_cubes = pm.Grid_Develop_Pattern(last_operation_before_exposure.cubes,exposed_material,grid,resist_type=resist_type)   
            current_process = pm.Development(developed_cubes,process_order)
       
       elif process == 'Etch' or process == 'LiftOff':
            if ifm.is_number(thickness):
                etched_cubes = pm.Grid_Etch([material_name],grid,etch_depth=int(thickness))
            else:
                etched_cubes = pm.Grid_Etch([material_name],grid)                
            current_process = pm.Etching(etched_cubes,material_name,process_order)
        
       elif process == 'Polish':
            polished_cubes = pm.Grid_Polish(material_name,grid)
            current_process = pm.Polishing(polished_cubes,material_name,process_order)
       
       elif process == 'Dope':
            doped_cubes = pm.Grid_Dope(material_name,[material_to_dope],grid,doping_depth=thickness)
            current_process = pm.Doping(doped_cubes,material_name,process_order)
       
       elif process == 'Diffuse_xy':
            diffused_cubes = pm.Grid_Diffuse_xy(material_name,diffusion_medium_material,grid,diffusivity)
            current_process = pm.Diffusion(diffused_cubes,material_name,diffusion_medium_material,process_order)
        
       elif process == 'Diffuse_x':
            diffused_cubes = pm.Grid_Diffuse_x(material_name,diffusion_medium_material,grid,diffusivity)
            current_process = pm.Diffusion(diffused_cubes,material_name,diffusion_medium_material,process_order)
        
       elif process == 'Diffuse_y':
            diffused_cubes = pm.Grid_Diffuse_y(material_name,diffusion_medium_material,grid,diffusivity)
            current_process = pm.Diffusion(diffused_cubes,material_name,diffusion_medium_material,process_order)
       
       elif process == 'SpinCoat':
            if ifm.is_number(thickness):
                spin_coated_cubes = pm.Grid_SpinCoat(grid,material_name,resist_type,resist_thickness=int(thickness))
            else:
                spin_coated_cubes = pm.Grid_SpinCoat(grid,material_name,resist_type)
            current_process = pm.SpinCoating(spin_coated_cubes,material_name,resist_type,process_order)
            
       
            
       executed_processes.append(current_process)    
       if show_step == 1:
            grid_states.append(copy.deepcopy(grid))
            processes.append(current_process)
    
    grid_states.append(copy.deepcopy(grid))
    processes.append(current_process)
        
    return processes,grid_states
        