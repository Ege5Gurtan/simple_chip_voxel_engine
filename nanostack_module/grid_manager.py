import copy
import importlib
def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class Grid_Properties:
    def __init__(self):
        self.default_grid_size_x = 5
        self.default_grid_size_y = 5
        self.cube_size = 1

class Grid():
    def __init__(self,num_x,num_y,num_z,cube_size=1):
        self.num_x = num_x
        self.num_y = num_y
        self.num_z = num_z
        self.cube_size = cube_size
        self.grid_num_columns = num_x*num_y
        self.grid_num_yz_surface = num_x
        self.grid_num_xy_surface = num_z
        self.grid_num_xz_surface = num_y
        
        self.all_columns = self.construct_all_columns_scheme()
        self.surfaces_yz = self.construct_yz_surface_scheme()
        self.surfaces_xy = self.construct_xy_surface_scheme()
        self.surfaces_xz = self.construct_xz_surface_scheme()
        
        self.grid_all_columns = self.construct_all_columns_scheme()
        self.grid_surfaces_yz = self.construct_yz_surface_scheme()
        self.grid_surfaces_xy = self.construct_xy_surface_scheme()
        self.grid_surfaces_xz = self.construct_xz_surface_scheme()
        
        
        
        self.cubes = []
        self.cube_indices = {}
        self.cube_history = {}
        
        self.grid_cubes = []
        self.grid_cube_indices = {}
        self.grid_cube_history = {}
        self.grid_cube_locations = {}
    
    def get_top_surface_cubes_with_material(self):
        top_surface_cubes = {}
        for column in self.grid_all_columns:
            for cube in self.grid_all_columns[column]:
                if column in list(top_surface_cubes.keys()):
                    if cube.location[2] > top_surface_cubes[column].location[2] and not(cube.material==None):
                        top_surface_cubes[column] = cube
                else:
                    top_surface_cubes[column] = cube
        return top_surface_cubes
                

    def get_top_surface_heights(self):
        column_lengths = {}
        for column in self.grid_all_columns:
            current_column_length_with_material = 0
            for cube in self.grid_all_columns[column]:
                if not(cube.material == None):
                    current_column_length_with_material = current_column_length_with_material + 1
            column_lengths[column] = current_column_length_with_material
        return column_lengths
        
    def construct_all_columns_scheme(self):
        all_columns = {}
        for i in range(0,self.grid_num_columns):
            all_columns['column'+str(i)] = []
        return all_columns
    
    def construct_yz_surface_scheme(self):
        yz_surfaces = {}
        for i in range(0,self.grid_num_yz_surface):
            yz_surfaces['surface_yz'+str(i)] = []
        return yz_surfaces
    
    def construct_xy_surface_scheme(self):
        xy_surfaces = {}
        for i in range(0,self.grid_num_xy_surface):
            xy_surfaces['surface_xy'+str(i)] = []
        return xy_surfaces
    
    def construct_xz_surface_scheme(self):
        xz_surfaces = {}
        for i in range(0,self.grid_num_xz_surface):
            xz_surfaces['surface_xz'+str(i)] = []
        return xz_surfaces
    
    def select_column(self,column_index):
        column_name = 'column'+str(column_index)
        for each_column in self.all_columns:
            if each_column == column_name:
                for cube in self.all_columns[column_name]:
                    cube.select_set(True)
                    
                return self.all_columns[column_name]
        
        print(column_name+' '+'could not be found')
        
    def grid_select_column(self,column_index):
        selected_grid_cubes = []
        column_name = 'column'+str(column_index)
        #import pdb;pdb.set_trace();
        for each_column in self.grid_all_columns:
            if each_column == column_name:
                for grid_cube in self.grid_all_columns[column_name]:
                    selected_grid_cubes.append(grid_cube)
                
                return self.grid_all_columns[column_name]
                
        
        
    
    def select_surface_yz(self,surface_yz_index):
        surface_yz_name = 'surface_yz'+str(surface_yz_index)
        for each_surface in self.surfaces_yz:
            if each_surface == surface_yz_name:
                for cube in self.surfaces_yz[surface_yz_name]:
                    cube.select_set(True)
                return self.surfaces_yz[surface_yz_name]
            
    def select_surface_xy(self,surface_xy_index):
        surface_xy_name = 'surface_xy'+str(surface_xy_index)
        for each_surface in self.surfaces_xy:
            if each_surface == surface_xy_name:
                for cube in self.surfaces_xy[surface_xy_name]:
                    cube.select_set(True)
                return self.surfaces_xy[surface_xy_name]
            
    def select_surface_xz(self,surface_xz_index):
        surface_xz_name = 'surface_xz'+str(surface_xz_index)
        for each_surface in self.surfaces_xz:
            if each_surface == surface_xz_name:
                for cube in self.surfaces_xz[surface_xz_name]:
                    cube.select_set(True)
                return self.surfaces_xz[surface_xz_name]
    
    def select_cube(self,cube_index):
        if not(cube_index == None):
            return self.cubes[cube_index]
        else:
            return None
    
    def grid_select_cube(self,cube_index):

        if not(cube_index==None) and cube_index<len(self.grid_cubes):
            return self.grid_cubes[cube_index]
        else:
            return None
    
    def select_grid_corners(self):
        num_x = self.num_x
        num_y = self.num_y
        num_z = self.num_z
        
        grid_corners = []
        grid_corners.append(self.select_cube(0))
        grid_corners.append(self.select_cube(num_z-1))
        grid_corners.append(self.select_cube(num_z*(num_y-1)))
        grid_corners.append(self.select_cube(num_z*(num_y)-1))
        grid_corners.append(self.select_cube(num_z*(num_y)*(num_x)-1))
        grid_corners.append(self.select_cube(num_z*(num_y)*(num_x)-num_z))
        grid_corners.append(self.select_cube(num_z*(num_y)*(num_x)-(num_y*num_z)))
        grid_corners.append(self.select_cube(num_z*(num_y)*(num_x)-(num_y*num_z)+num_z-1))
        
        return grid_corners
        
    def get_cube_index(self,cube):
        pass

    def hide_empty_cubes(self):
        for cube in self.cubes:
            if len(cube.data.materials) == 0:
                cube.hide_viewport = True
                cube.hide_render = True
    
    def show_non_empty_cubes(self):
        for cube in self.cubes:
            if len(cube.data.materials) > 0:
                cube.hide_viewport = False
                cube.hide_render = False
        
                
    def delete_empty_cubes(self):
        #bpy.ops.object.select_all(action='DESELECT')
        for cube in self.cubes:
            if len(cube.data.materials) == 0:
                cube.select_set(True)
        #bpy.ops.object.delete()
        
                


        
        

class Grid_Cube:
    def __init__(self,grid,cube_index):
        self.grid = grid
        self.cube_size = grid.cube_size
        #self.total_cube_number = grid.num_x*grid.num_y*grid.num_z
        self.cube_index = cube_index
        self.neighbour_z_cube_index = cube_index+1
        self.neighbour_minus_z_cube_index = cube_index-1
        self.neighbour_x_cube_index = cube_index + grid.num_z*grid.num_y 
        self.neighbour_minus_x_cube_index = cube_index - grid.num_z*grid.num_y
        self.neighbour_y_cube_index = cube_index + grid.num_z
        self.neighbour_minus_y_cube_index = cube_index - grid.num_z
        
        self.verify_neighbour_existance()
        
        
        self.neighbour_z_cube = grid.select_cube(self.neighbour_z_cube_index)
        self.neighbour_minus_z_cube = grid.select_cube(self.neighbour_minus_z_cube_index)
        
        self.neighbour_x_cube = grid.select_cube(self.neighbour_x_cube_index)
        self.neighbour_minus_x_cube = grid.select_cube(self.neighbour_minus_x_cube_index)
        
        self.neighbour_y_cube = grid.select_cube(self.neighbour_y_cube_index)
        self.neighbour_minus_y_cube = grid.select_cube(self.neighbour_minus_y_cube_index)
        
        #bpy.ops.object.select_all(action='DESELECT')
            
        
    def verify_neighbour_existance(self):
        grid_size_y = self.grid.num_y
        grid_size_x = self.grid.num_x
        grid_size_z = self.grid.num_z
        cube = self.grid.cubes[self.cube_index]
        
        if cube in self.grid.surfaces_xy['surface_xy'+str(grid_size_z-1)]:
            self.neighbour_z_cube_index = None
        
        if cube in self.grid.surfaces_xy['surface_xy0']:
            self.neighbour_minus_z_cube_index = None
            
            
        if cube in self.grid.surfaces_xz['surface_xz'+str(grid_size_y-1)]:
            self.neighbour_y_cube_index = None
        
        if cube in self.grid.surfaces_xz['surface_xz0']:
            self.neighbour_minus_y_cube_index = None
            
        if cube in self.grid.surfaces_yz['surface_yz'+str(grid_size_x-1)]:
            self.neighbour_x_cube_index = None
        
        if cube in self.grid.surfaces_yz['surface_yz0']:
            self.neighbour_minus_x_cube_index = None
        
    
    def select_cube(self,itself=True,
    z=False,_z=False,
    y=False,_y=False,
    x=False,_x=False):
        selected_cubes = {'itself':None,'z':None,'_z':None,'y':None,'_y':None,'x':None,'_x':None}
        if itself:
            selected_cubes['itself']=self.grid.select_cube(self.cube_index)
        if z and not(self.neighbour_z_cube_index==None):
            selected_cubes['z']=self.grid.select_cube(self.neighbour_z_cube_index)
        if _z and not(self.neighbour_minus_z_cube_index==None):
            selected_cubes['_z']=self.grid.select_cube(self.neighbour_minus_z_cube_index)
        if y and not(self.neighbour_y_cube_index==None):
            selected_cubes['y']=self.grid.select_cube(self.neighbour_y_cube_index)
        if _y and not(self.neighbour_minus_y_cube_index==None):
            selected_cubes['_y']=self.grid.select_cube(self.neighbour_minus_y_cube_index)
        if x and not(self.neighbour_x_cube_index==None):
            selected_cubes['x']=self.grid.select_cube(self.neighbour_x_cube_index)
        if _x and not(self.neighbour_minus_x_cube_index==None):
            selected_cubes['_x']=self.grid.select_cube(self.neighbour_minus_x_cube_index)    
        return selected_cubes
    
    
    @staticmethod
    def get_cube_center_point(test_cube):
        test_center_v = test_cube.matrix_world @ test_cube.location
        test_point = (test_center_v.x,test_center_v.y,test_center_v.z)
        return test_point
    
    @staticmethod
    def is_cube_inside_grid(test_cube,grid):
        test_point = self.get_cube_center_point(test_cube)
        is_inside = self.is_point_inside_grid(test_point,grid)
        return is_inside
        
    @staticmethod
    def is_point_inside_grid(test_point,grid):
        edge_cubes = grid.select_grid_corners()
        corner_points = []
        for obj in edge_cubes:
            center_coordinates = obj.matrix_world @ obj.location
            corner_points.append((center_coordinates.x,center_coordinates.y,center_coordinates.z))
        
        min_x, min_y, min_z = map(min, zip(*corner_points))
        max_x, max_y, max_z = map(max, zip(*corner_points))
        x, y, z = test_point

        if min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z:
            return True
        else:
            return False
    
    @staticmethod
    def print_neighbour_indices(cube):
        print('+z : ' + str(cube.neighbour_z_cube_index))
        print('-z : ' + str(cube.neighbour_minus_z_cube_index))
        print('+x : ' + str(cube.neighbour_x_cube_index))
        print('-x : ' + str(cube.neighbour_minus_x_cube_index))
        print('+y : ' + str(cube.neighbour_y_cube_index))
        print('-y : ' + str(cube.neighbour_minus_y_cube_index))
    
        
class Grid_Element:
        def __init__(self,cube_name,location,index_x,index_y,index_z):
            self.cube_name = cube_name
            self.location = location
            self.material = None
            self.index_x = index_x
            self.index_y = index_y
            self.index_z = index_z
            self.is_exposed = False
            #self.material = material_name
            

def create_grid_v2(num_x,num_y,num_z,cube_size=1):
    # Create cubes in a grid
    grid = Grid(num_x,num_y,num_z,cube_size=cube_size)
    column_counter = 0
    cube_counter = 0
    yz_surface_counter = -1
    for i in range(num_x):
        yz_surface_counter = yz_surface_counter + 1
        for j in range(num_y):
            for k in range(num_z):
                grid_cube = Grid_Element('Cube.'+str(cube_counter),(i * cube_size, j * cube_size, k * cube_size),i,j,k)
                
                grid.grid_cubes.append(grid_cube)
                grid.grid_cube_indices[grid_cube] = cube_counter
                grid.grid_cube_history[grid_cube] = ['empty']
                
                grid.grid_cube_locations[(i * cube_size, j * cube_size, k * cube_size)] = grid_cube
                
                cube_counter = cube_counter +1
                if len(grid.grid_all_columns['column'+str(column_counter)]) == num_z:
                    column_counter = column_counter+1
                xz_surface_index = column_counter % num_y
                xy_surface_index = len(grid.grid_all_columns['column'+str(column_counter)])
                
                
                grid.grid_surfaces_xy['surface_xy'+str(xy_surface_index)].append(grid_cube)
                grid.grid_surfaces_xz['surface_xz'+str(xz_surface_index)].append(grid_cube)
                grid.grid_all_columns['column'+str(column_counter)].append(grid_cube)
                grid.grid_surfaces_yz['surface_yz'+str(yz_surface_counter)].append(grid_cube)
                
    return grid
    

def get_layer_difference(layer_1_cubes,layer_2_cubes):
    difference = list(set(layer_1_cubes) - set(layer_2_cubes))
    return difference



def circular_grid_selector(grid_num_x,grid_num_y,circle_center_index_x,circle_center_index_y,circle_radius):
    rows = grid_num_x
    columns = grid_num_y
    # Define the row and column for the circle's center
    circle_row = circle_center_index_x  # Fifth row
    circle_col = circle_center_index_y  # Fourth column
    circle_radius = circle_radius  # You can adjust the radius as needed

    circle_row = circle_row - 1
    selected_grids = []
    for i in range(rows):
        for j in range(columns):
            x, y = j + 0.5, rows - i - 0.5
            if (x - (circle_col -0.5))** 2 + (y - (rows-circle_row-0.5))** 2 <= circle_radius ** 2:
                selected_grids.append([i+1,j+1])
    
    return selected_grids