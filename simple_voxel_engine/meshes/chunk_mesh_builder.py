from settings import *

def is_void(voxel_pos,cube_locations):
    x,y,z = voxel_pos
    if 0<=x <grid.num_x and 0 <=y <grid.num_y and 0<=z <grid.num_z:
        if not(voxel_pos in list(cube_locations.keys())):
            return False
    return True

def add_data(vertex_data,index,*vertices):
    for vertex in vertices:
        for attr in vertex:
            vertex_data[index] = attr
            index +=1
    return index

def build_chunk_mesh(chunk_voxels,format_size,chunk_voxel_colors,grid):
    vertex_data = np.empty(CHUNK_VOL*18*format_size,dtype='uint8')
    index = 0

    for voxel_index in grid.voxel_indices:

        voxel_id = voxel_index
        voxel_color = chunk_voxel_colors[voxel_index]
        element = grid.voxel_indices[voxel_index]
        x = element.location[0]
        y = element.location[1]
        z = element.location[2]

        if voxel_color == 0:
            continue

        #top face
        if is_void((x, y + 1, z),grid.grid_cube_locations):
            v0 = (x, y + 1, z, voxel_id,0 )  + voxel_color
            v1 = (x + 1, y + 1, z, voxel_id, 0) + voxel_color
            v2 = (x + 1, y + 1, z + 1, voxel_id,0)+ voxel_color
            v3 = (x, y + 1, z + 1, voxel_id, 0)+ voxel_color

            index = add_data(vertex_data,index,v0,v3,v2,v0,v2,v1)

        #bottom face
        if is_void((x, y - 1, z), grid.grid_cube_locations):
            v0 = (x,y,z,voxel_id,1) + voxel_color
            v1 = (x+1,y,z,voxel_id,1) + voxel_color
            v2 = (x+1,y,z+1,voxel_id,1)+ voxel_color
            v3 = (x,y,z+1,voxel_id,1)+ voxel_color

            index = add_data(vertex_data,index,v0,v2,v3,v0,v1,v2)

        #right face
        if is_void((x+1,y,z),grid.grid_cube_locations):
            v0 = (x+1,y,z,voxel_id,2)+ voxel_color
            v1 = (x+1,y+1,z,voxel_id,2)+ voxel_color
            v2 = (x+1,y+1,z+1,voxel_id,2)+ voxel_color
            v3 = (x+1,y,z+1,voxel_id,2)+ voxel_color

            index = add_data(vertex_data,index,v0,v1,v2,v0,v2,v3)

        #left face
        if is_void((x-1,y,z),grid.grid_cube_locations):
            v0 = (x,y,z,voxel_id,3)+ voxel_color
            v1 = (x,y+1,z,voxel_id,3)+ voxel_color
            v2 = (x,y+1,z+1,voxel_id,3)+ voxel_color
            v3 = (x,y,z+1,voxel_id,3)+ voxel_color

            index = add_data(vertex_data,index,v0,v2,v1,v0,v3,v2)

        #back face
        if is_void((x,y,z-1),grid.grid_cube_locations):
            v0 = (x,y,z,voxel_id,4)+ voxel_color
            v1 = (x,y+1,z,voxel_id,4)+ voxel_color
            v2 = (x+1,y+1,z,voxel_id,4)+ voxel_color
            v3 = (x+1,y,z,voxel_id,4)+ voxel_color

            index = add_data(vertex_data,index,v0,v1,v2,v0,v2,v3)

        #front face
        if is_void((x,y,z+1),grid.grid_cube_locations):
            v0 = (x,y,z+1,voxel_id,5)+ voxel_color
            v1 = (x,y+1,z+1,voxel_id,5)+ voxel_color
            v2 = (x+1,y+1,z+1,voxel_id,5)+ voxel_color
            v3 = (x+1,y,z+1,voxel_id,5)+ voxel_color

            index = add_data(vertex_data,index,v0,v2,v1,v0,v3,v2)

    return vertex_data[:index+1]

























