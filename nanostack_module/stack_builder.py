#stack_csv_path = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\DEMO\stack_description_heitz.csv"

import pandas as pd
from nanostack_module import input_file_manager as ifm
from nanostack_module import grid_manager as gm
from nanostack_module import stack_manager as stm

def stack_builder(stack_csv_path):
    df = pd.read_csv(stack_csv_path)
    df.dropna(how='all', inplace=True)
    material_csv_path = ifm.get_material_file_path(df)
    material_df = pd.read_csv(material_csv_path)
    material_df.dropna(how='all', inplace=True)
    height, width = ifm.get_grid_xy_dimension_from_patterns(df)
    active_processes_df = ifm.get_active_processes_df(df)
    estimated_stack_thickness = int(
        active_processes_df[active_processes_df['Process'] == 'Deposit']['Thickness'].sum()) + 1

    grid_props = gm.Grid_Properties()
    grid = gm.create_grid_v2(width, height, estimated_stack_thickness, cube_size=grid_props.cube_size)
    processes, grid_states = stm.construct_active_processes(df, grid)


    return grid_states,material_df