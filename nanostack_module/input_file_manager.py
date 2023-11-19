import pandas as pd
import numpy as np
import pya
import os
import random

def add_optional_column(df,optional_column_name,default_value,column_location=1):
    if not(optional_column_name in df.columns):
        df.insert(column_location,optional_column_name,[default_value]*(len(df.index)))
    else:
        is_nan = pd.isna(df[optional_column_name])
        df[optional_column_name][is_nan] = default_value
    return df

def get_material_file_path(df):
    if not(df[df['Process']=='Material_file'].empty):
        material_file_path = df[df['Process'] == 'Material_file'].iloc[0]['Path']
    else:
        material_file_path = ''
    return material_file_path
    

def get_active_processes_df(df):
    ##detect the row number where # exists.
    condition1 = (df['Process'].apply(lambda x: '#' in x)) #process col should not have #
    condition2 = (df['Process'].apply(lambda x: not '%' in x)) #process col should not have #
    rows_with_hash = df[condition1]
    if len(rows_with_hash.index) >0:
        min_row_index = min(rows_with_hash.index)
        df_without_hash = df.drop(df.index[min_row_index:],inplace=False)
    else:
        df_without_hash = df
    df_with_processes_to_execute = df_without_hash[condition2]
    return df_with_processes_to_execute

def get_active_pattern_file_paths(df):
    df = get_active_processes_df(df)
    condition1 = (df['Path'].apply(lambda x: isinstance(x,str))) #pattern file has to be string
    condition2 = (df['Process'].apply(lambda x: not '%' in x)) #process col should not have %
    condition3 = (df['Process'].apply(lambda x: not '#' in x)) #process col should not have #
    condition4 = (df['Process'].apply(lambda x: 'Expose' == x))
    filter_condition = condition1 & condition2 & condition3 & condition4
    pattern_files = df[filter_condition]
    return pattern_files

def get_grid_xy_dimension_from_patterns(df,default_height=5,default_width=5):
    pattern_files = get_active_pattern_file_paths(df)
    pattern_paths = pattern_files['Path']
    feature_layer_names = pattern_files['Feature_Layer']
    grid_layer_names = pattern_files['Grid_Layer']
    
    recorded_heights = []
    recorded_widths = []
    for path,feature_layer_name,grid_layer_name in zip(pattern_paths,feature_layer_names,grid_layer_names):
        df_pattern = create_pattern_df_from_oas(path,feature_layer_name,grid_layer_name)
        width = len(df_pattern.columns)
        height = len(df_pattern)
        if any(df_pattern.loc[height-1].isin(['end'])):
            height = height - 1
        recorded_heights.append(height)
        recorded_widths.append(width)
    if recorded_heights == []:
        recorded_heights = [default_height]
    if recorded_widths == []:
        recorded_widths = [default_width]
    return max(recorded_heights),max(recorded_widths)

def get_pattern_dfs(df):
    pattern_files = get_active_pattern_file_paths(df)
    pattern_paths = pattern_files['Pattern']
    pattern_dfs = []
    for path in pattern_paths:
        df_pattern = pd.read_csv(path)
        pattern_dfs.append(df_pattern)
    return pattern_dfs

def reshape_pattern_df(pattern_df,height,width):
    if any(pattern_df.loc[len(pattern_df)-1].isin(['end'])):
        pattern_df = pattern_df.drop(len(pattern_df)-1)
    reshaped_pattern_df_column_names = [i for i in range(1,width+1)]
    data = [[None for _ in range(width)] for _ in range(height)]
    reshaped_pattern_df = pd.DataFrame(data,columns = reshaped_pattern_df_column_names)
    for row_index,row in pattern_df.iterrows():
        for col_index, value in row.items():
            if isinstance(value,str) or (isinstance(value,float) and not(np.isnan(value))):
                reshaped_pattern_df.at[row_index,int(col_index)] = 'X'
    return reshaped_pattern_df

def make_drc_region(output_layout,input_cell,input_layer_index):
    drc_region = pya.Region.new()
    shape_iterator = pya.RecursiveShapeIterator.new(output_layout, input_cell, input_layer_index)
    drc_region.insert(shape_iterator)
    return drc_region

def extract_layers_and_indices(layout):
    layers_in_layout = pya.Layout.layer_infos(layout)
    layers = {}
    for layer_in_layout, layer_index in zip(layers_in_layout, layout.layer_indexes()):

        formatted_name = str(layer_in_layout)
        formatted_name = formatted_name.replace(' (', '/')
        formatted_name = formatted_name.replace(')', '')
        layers[formatted_name] = layer_index

    return layers

def create_pattern_df_from_oas(input_oasis_path,feature_layer_name,grid_layer_name):
    layout = pya.Layout()
    layout.read(input_oasis_path)
    selected_grid_layer= layout.layer(random.randint(100,1000),random.randint(100,1000),'selected')

    cell = layout.top_cell()
    cell.flatten(-1)
    layers = extract_layers_and_indices(layout)

    shape_iterator_grid = pya.RecursiveShapeIterator.new(layout, cell, layers[grid_layer_name])
    feature_region = make_drc_region(layout,cell,layers[feature_layer_name])
    grid_region = make_drc_region(layout,cell,layers[grid_layer_name])

    feature_region.merged_semantics = False
    grid_region.merged_semantics = False

    all_centers = []
    
    
    all_center_x = []
    all_center_y = []
    zeroes = []
    while not shape_iterator_grid.at_end():
        shape = shape_iterator_grid.shape()
        center = [shape.dbbox().center().x,shape.dbbox().center().y]
        all_centers.append(center)
        all_center_x.append(shape.dbbox().center().x)
        all_center_y.append(shape.dbbox().center().y)
        zeroes.append(0)
        
        shape_iterator_grid.next()

    interacting_region = grid_region.interacting(feature_region)
    interacting_region.merged_semantics = False

    dbu = layout.dbu
    interacting_region.insert_into(layout, cell.cell_index(),selected_grid_layer)
    shape_iterator_selected_grid = pya.RecursiveShapeIterator.new(layout, cell, selected_grid_layer)

    
    selected_centers = []
    selected_x = []
    selected_y = []
    ones = []
    while not shape_iterator_selected_grid.at_end():
        shape = shape_iterator_selected_grid.shape()
        center = [shape.dbbox().center().x,shape.dbbox().center().y]
        selected_x.append(shape.dbbox().center().x)
        selected_y.append(shape.dbbox().center().y)
        ones.append(1)
        selected_centers.append(center)
        shape_iterator_selected_grid.next()

    df_selected = pd.DataFrame({'x':selected_x,'y':selected_y,'selected':ones})    
    df_all = pd.DataFrame({'x':all_center_x,'y':all_center_y,'selected':zeroes})    
    df_merged = df_all.merge(df_selected[['x','y','selected']],on=['x','y'],suffixes=('','_df_selected'),how='left')
    df_merged['selected'] = df_merged['selected_df_selected'].fillna(df_merged['selected'])
    df_merged.drop('selected_df_selected',axis=1,inplace=True)
    df_merged_sorted = df_merged.sort_values(by=['y','x'])
    df_merged_sorted = df_merged_sorted.reset_index(drop=True)
    selected_indices_from_df = []
    for i in df_merged_sorted.index.tolist():
        is_selected = df_merged_sorted.loc[i, "selected"]
        if is_selected == 1:
            selected_indices_from_df.append(i)
    
    

    x_vals,y_vals = zip(*all_centers)
    col_num = len(set(x_vals))
    row_num = len(set(y_vals))
    pattern_array = np.zeros((row_num,col_num))
    pattern_array = pattern_array.astype('int')
    pattern_array_str = pattern_array.astype('str')
    for selected_index in selected_indices_from_df:
        column_number = selected_index%col_num
        row_number = selected_index//col_num
        pattern_array_str[row_num-row_number-1][column_number] = 'X'
    
    

    col_names = [str(i) for i in range(1,col_num+1)]
    df = pd.DataFrame(pattern_array_str,columns=col_names)
    df = df.replace('0','')
    final_row  = {}
    for i in range(1,col_num+1):
        final_row[str(i)] = ''
    final_row['1'] = 'end'
    last_index = df.index[-1] + 1 if not df.empty else 0
    df.loc[last_index] = final_row
    #new_row = pd.Series(final_row)
    #df = df.append(new_row,ignore_index=True)
    base, _ = os.path.splitext(input_oasis_path)
    output_csv_path =  os.path.join(base,".csv")
    
    #import pdb;pdb.set_trace();
    
    folder_path = os.path.split(input_oasis_path)[0]
    file_name_with_extension = os.path.split(input_oasis_path)[1]
    filename, ext = os.path.splitext(file_name_with_extension)
    output_csv_path = os.path.join(folder_path,filename+'.csv')

    df.to_csv(output_csv_path,index=False)
    pattern_df = pd.read_csv(output_csv_path)
    
    output_oas_path_debugging = os.path.join(folder_path,filename+'.debug.oas')
    layout.write(output_oas_path_debugging)
    
    os.remove(output_csv_path)
    return pattern_df

    

def is_number(string_value):
    try:
        number = float(string_value)
        return np.isfinite(number)
    except ValueError:
        return False