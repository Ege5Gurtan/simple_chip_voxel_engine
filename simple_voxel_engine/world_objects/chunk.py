from settings import *
from meshes.chunk_mesh import ChunkMesh
from nanostack_module.stack_builder import stack_builder




class Chunk:
    def __init__(self,app):
        self.app = app
        self.voxels,self.voxel_colors,self.grid = self.build_voxels()
        self.mesh: ChunkMesh = None
        self.build_mesh()

    def build_mesh(self):
        self.mesh = ChunkMesh(self)

    def render(self):
        self.mesh.render()


    def build_voxels(self,):
        #empty chunk
        ##fill chunk
        CHUNK_VOL = grid.num_x*grid.num_y*grid.num_z
        voxels = np.zeros(CHUNK_VOL, dtype='uint8')
        voxel_colors = [0]*CHUNK_VOL
        grid.voxel_indices = {}
        for grid_column_name in (grid.grid_all_columns):
            column_number = int(''.join(filter(str.isdigit,grid_column_name)))
            for element_index,element in enumerate(grid.grid_all_columns[grid_column_name]):
                voxel_index = column_number+element_index*grid.num_x*grid.num_y
                grid.voxel_indices[voxel_index] = element
                if not (grid.voxel_indices[voxel_index].material == None):
                    r = (material_df[material_df['Material'] ==grid.voxel_indices[voxel_index].material]['R'])#*255
                    g = (material_df[material_df['Material'] == grid.voxel_indices[voxel_index].material]['G'])#*255
                    b = (material_df[material_df['Material'] == grid.voxel_indices[voxel_index].material]['B'])#*255
                    if '_exposed' in grid.voxel_indices[voxel_index].material:
                        r,g,b = 128,0,128

                    r,g,b = float(r),float(g),float(b)
                    # r, g, b = round(r, 1), round(g, 1), round(b, 1)
                    voxels[voxel_index] = 1
                    voxel_colors[voxel_index] = (r, g, b)
                else:
                    voxels[voxel_index] = 0
                    voxel_colors[voxel_index] = 0

        return voxels,voxel_colors,grid