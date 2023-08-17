from scipy.spatial import KDTree
from vesselTrees import *
import numpy as np
import matplotlib.pyplot as plt
import pyvista as pv

from vesselTrees import VTree

##################################################################

class SetVisibilityCallback:
    """Helper callback to keep a reference to the actor being modified."""

    def __init__(self, actor, actor_id):
        self.actor = actor
        self.name  = actor_id

    def __call__(self, state):
        self.actor.SetVisibility(state)
        seeks.buttons_state[self.name]  = state
        print("Seekers-State: ", seeks.buttons_state)
        if state:
            if self.name == 'normal_arrows':
                seeks.seekers_dir = seeks.normal_arrows
                seeks.mesh.active_normals = seeks.normal_arrows
            elif self.name == 'flip_normal_arrows':
                seeks.seekers_dir = seeks.flip_normal_arrows
                seeks.mesh.active_normals = seeks.flip_normal_arrows

# Aqui empieza todo ...
class Seekers:
    def __init__(self, cfg_file) :

        self.seekers        = []
        self.dwall          = []
        self.nseekers       = -1
        self.Plott          = pv.Plotter()
        self.actors         = {}
        self.buttons_state  = {}
        self.kdt            = []  # seekers kdt
        self.inlet          = -1
        self.outlets_border = []
        self.outlets        = []
        self.dwall_outlets  = []
        self.num_outlets    = 0  

        self.load_data()
        self.init()

    def load_data(self,):
        self.data_path      = "C0001_models/C0001/surface/"
        self.stlfile        = "model"
        #self.stlfile        = "01_1175145_SA"
        #self.data_path      = "/home/miguel/boids3D/aortas_con_carotidas/" #seekers/CMBE22_centerline/"

        mesh_file           = self.data_path+self.stlfile+'.stl'        
        self.mesh           = pv.read(mesh_file)
        self.dmesh          = []

    def init(self,):
        self.npoints_mesh = self.mesh.n_points    
        self.mesh.smooth(inplace=True, boundary_smoothing=True, n_iter=100)
        self.mesh.compute_normals(flip_normals=True, inplace=True)
        self.arrows = self.mesh.glyph(orient='Normals')
        self.Plott.set_background('white')
                      
    
    def show(self,):
        
    # Mesh
    #####################################################

        def show_mesh(flag):
            if 'mesh' in self.Plott.actors: 
                if flag:
                    self.Plott.actors['mesh'].visibility = True  
                else:
                    self.Plott.actors['mesh'].visibility = False
            return
        
        self.Plott.add_checkbox_button_widget(show_mesh, value=True, position=[25,15], size=20)
        self.Plott.add_text('show_mesh', position=[55, 15], font_size=10)

    #####################################################
    # Normals
    #####################################################

        def show_normals(flag):
            if not 'normals' in self.Plott.actors:
                self.Plott.actors['normals'] = self.Plott.add_mesh(self.arrows)
            if flag:
                self.Plott.actors['normals'].visibility =  True # self.Plott.add_mesh(self.arrows)
            else:
                self.Plott.actors['normals'].visibility =  False # self.Plott.remove_actor('normals')
            return
        
        self.Plott.add_checkbox_button_widget(show_normals, value=False, position=[225,15], size=20)
        self.Plott.add_text('show_normals', position=[255, 15], font_size=10)

    #####################################################
    # Flip
    #####################################################

        def flip_normals(flag):
            self.mesh.compute_normals(flip_normals=True, inplace=True)
            self.active_normals = self.mesh.active_normals
            self.arrows = self.mesh.glyph(orient='Normals')
            
            if 'normals' in self.Plott.actors:
                self.Plott.remove_actor('normals')

            self.Plott.actors['normals'] = self.Plott.add_mesh(self.arrows)

            return
        
        self.Plott.add_checkbox_button_widget(flip_normals, value=False, position=[425,15], size=20)
        self.Plott.add_text('flip_normals', position=[455, 15], font_size=10)

    #####################################################
    # Decimation slider (number of seekers)
    #####################################################  
     
        def size_slider(value):
            self.dmesh = self.mesh.decimate_pro(value/100, preserve_topology=True)
            self.dmesh.compute_normals(inplace=True)
            self.active_normals = self.dmesh.active_normals
            self.arrows = self.dmesh.glyph(orient='Normals')
            self.nseekers = self.dmesh.n_points

            polySeeks = pv.PolyData(self.dmesh.points)
            self.seekers = self.dmesh.points
            if 'seekers' in self.Plott.actors:
                self.Plott.remove_actor('seekers')  
            if 'mesh' in self.Plott.actors:    
                self.Plott.remove_actor('mesh')
            if 'npoints' in self.Plott.actors:    
                self.Plott.remove_actor('npoints')
            #if 'normals' in self.Plott.actors:    
            #    self.Plott.remove_actor('normals')

            self.Plott.actors['mesh'] = self.Plott.add_mesh(self.mesh, opacity=0.5, color='white', pickable=False) 
            self.Plott.actors['seekers'] = self.Plott.add_points(polySeeks, render_points_as_spheres = True, color = 'orange', point_size=5)
            self.Plott.actors['npoints'] = self.Plott.add_text('Npoints = '+str(self.nseekers), position=[850, 740], font_size=10)
            #self.Plott.actors['normals'] = self.Plott.add_mesh(self.arrows)
            return
        
        self.Plott.add_slider_widget(size_slider, [0,100],title='% points removed', value=50)

    #####################################################
    # Seekers
    #####################################################
  
        def show_seekers(flag):
            if 'seekers' in self.Plott.actors: 
                if flag:
                    self.Plott.actors['seekers'].visibility = True  
                else:
                    self.Plott.actors['seekers'].visibility = False
            return
        
        self.Plott.add_checkbox_button_widget(show_seekers, value=True, position=[180,100], size=20)
        self.Plott.add_text('show_seekers', position=[210, 100], font_size=10)

        # Run seekers callback + button

        def run_seekers(flag):
            if 'seekers' in self.Plott.actors and len(self.seekers) > 0:
                self.compute_seekers()
                polySeeks = pv.PolyData(self.seekers)
                polySeeks['radius'] = self.dwall
                self.Plott.remove_actor('seekers')
                # Low resolution geometry
                geom = pv.Sphere(theta_resolution=12, phi_resolution=12, radius=0.25)
                # Progress bar is a new feature on master branch
                glyphed_seekers = polySeeks.glyph(scale="radius", geom=geom) # progress_bar=True)
                self.Plott.actors['seekers'] = self.Plott.add_mesh(glyphed_seekers, opacity=0.4)
                
            print("Run:", self.nseekers)

        self.Plott.add_checkbox_button_widget(run_seekers, value=False, position=[25,100], size=20)
        self.Plott.add_text('run seekers', position=[50, 100], font_size=10)
    
    #####################################################
    # Outlets
    #####################################################

        def outlets(flag):
            if not flag:
                if 'outlets_borders' in self.Plott.actors:
                    self.Plott.remove_actor('outlets_borders') 
                    for i in range(self.num_outlets):
                         self.Plott.remove_actor('outlet_'+str(i))
            else:
                if 'outlets_borders' in self.Plott.actors:
                    self.Plott.remove_actor('outlets_borders')  
                
                self.outlets_border = self.mesh.extract_feature_edges(boundary_edges=True, manifold_edges=False, feature_edges=False)
                #self.Plott.actors['outlets_borders'] = self.Plott.add_mesh(self.outlets_border,  opacity=1, point_size=10) #
               
                connected_cells = self.outlets_border.connectivity()
                
                self.num_outlets = len(np.unique(connected_cells['RegionId']))
                self.outlets = []
                max_wall_dist = 0
                for i in range(self.num_outlets):
                    out_i = connected_cells.threshold(value=[i,i], scalars = 'RegionId')
                    centro = np.mean(out_i.points[:], axis=0)
                    
                    cp = self.mesh.find_closest_point(centro)
                    wall_dist = np.linalg.norm(self.mesh.points[cp] - centro)

                    if wall_dist > 0.2:
                        self.outlets.append(centro)
                        self.dwall_outlets.append(wall_dist)
                        
                        if wall_dist > max_wall_dist:
                            max_wall_dist = wall_dist
                            self.inlet    = len(self.outlets)-1
                            print(i, wall_dist)
                        
                    #print(self.dwall_outlets)

                        self.Plott.actors['outlet_'+str(i)] = self.Plott.add_points(centro, render_points_as_spheres = True, point_size = 20, color='red') #                

                # El inlet es el outlet mas gordo: mayor distancia a la pared
                self.Plott.actors['inlet'] = self.Plott.add_points(self.outlets[self.inlet], render_points_as_spheres = True, point_size =40, color = 'blue')
                self.Plott.actors['text_inlet'] = self.Plott.add_text("Inlet: "+str(self.inlet), [25, 200], font_size=16)
  

        self.Plott.add_checkbox_button_widget(outlets, value=False, position=[25,150], size=20)
        self.Plott.add_text('outlets', position=[50, 150], font_size=10)

    #####################################################
    # Inlet
    #####################################################

         # Inlet selection
        def inlet(point):
            self.kdt = KDTree(np.array(self.outlets))
            d, i = self.kdt.query(point)
            if 'inlet' in self.Plott.actors:
                self.Plott.remove_actor('inlet')
                self.Plott.remove_actor('text_inlet')
            self.Plott.actors['inlet'] = self.Plott.add_points(self.outlets[i], render_points_as_spheres = True, point_size =40, color = 'blue')
            self.inlet = i
            self.Plott.actors['text_inlet'] = self.Plott.add_text("Inlet: "+str(self.inlet), [25, 200], font_size=16)

        self.Plott.enable_surface_picking(callback=inlet, show_message=False, color='blue')

        if self.inlet >= 0:
            self.Plott.add_text("Inlet: "+str(self.inlet), [25, 200], font_size=16)
        #self.Plott.remove_scalar_bar("GlyphScale")

    #####################################################
    # Vessel Tree
    #####################################################

        def run_vessel_tree(flag):
            t = VTree(seeks.inlet, np.array(seeks.outlets), seeks.seekers, seeks.dwall, seeks.dwall_outlets)
           
            tree, joints_ids, seekers_in_paths = t.build_tree()
            print(tree)
            for i in range(len(tree)):
                if 'path_'+str(i) in self.Plott.actors:
                    self.Plott.remove_actor('path_'+str(i))

            for i, node in enumerate(tree):
                print(node)
                tube = pv.Spline(t.domain[tree[node]], 400)
                c = np.random.rand(3)
                self.Plott.actors['path_'+str(i)] = self.Plott.add_mesh(tube, opacity=1,color=c, line_width=6)#)

            
            self.Plott.actors['joints'] = self.Plott.add_points(t.domain[joints_ids], render_points_as_spheres = True, point_size = 15, color='white') #                
            if 'seekers' in self.Plott.actors:
                self.Plott.remove_actor('seekers')
            
            polySeeks = pv.PolyData(self.seekers[seekers_in_paths])
            polySeeks['radius'] = self.dwall[seekers_in_paths]
            geom = pv.Sphere(theta_resolution=12, phi_resolution=12, radius=1)
            # Progress bar is a new feature on master branch
            glyphed_seekers = polySeeks.glyph(scale='radius', geom=geom) # progress_bar=True)
            self.Plott.actors['seekers'] = self.Plott.add_mesh(glyphed_seekers, opacity=1, color = 'orange')  
            return
    
        self.Plott.add_checkbox_button_widget(run_vessel_tree, value=False, position=[25,300], size=30)
        self.Plott.add_text('run vessel tree', position=[75,300], font_size=14)
        
        # Load Tree
        def load_vessel_tree(flag):
            pt = paths_tree("model.tree")
            tree, joints_ids, seekers_in_paths = pt.load()
            
            for i in range(len(tree)):
                if 'path_'+str(i) in self.Plott.actors:
                    self.Plott.remove_actor('path_'+str(i))

            for i, node in enumerate(tree):
                tube = pv.Spline(pt.domain[tree[node]], 400)
                c = np.random.rand(3)
                self.Plott.actors['path_'+str(i)] = self.Plott.add_mesh(tube, opacity=1,color=c, line_width=6)#)
                
            self.Plott.actors['joints'] = self.Plott.add_points(pt.domain[joints_ids], render_points_as_spheres = True, point_size = 15, color='white') #                
            
            return

        self.Plott.add_checkbox_button_widget(load_vessel_tree, value=False, position=[25,240], size=30)
        self.Plott.add_text('load vessel tree', position=[75,240], font_size=14)

        
        # ... finally
        self.Plott.show()

    def compute_seekers(self):

        #selected = np.linspace(0, self.npoints_mesh-1, self.nseekers,dtype='int')
        self.seekers_dir = self.active_normals
        self.seekers_pos = self.seekers
        
        #  3 - Define line segment (long 50)
        start = self.seekers_pos + self.seekers_dir*0.02
        stop = self.seekers_pos + 40*self.seekers_dir   # Ojo este numero magico ...

        #  4 - CenterPoints (centro del rayo que cruza el tubo)
        CPoints, id_interior = [], []
        
        # Perform ray trace
        i = 0
        for ini, end in zip(start, stop):
            points, ind = self.mesh.ray_trace(ini, end)

            # Create geometry to represent ray trace
            ray = pv.Line(ini, end)
            intersection = pv.PolyData(points)
            
            if intersection.n_points == 1:
                center_points = (intersection.points[0] + ini)/2
                centers = pv.PolyData(center_points)
                interiores = centers.select_enclosed_points(self.mesh, check_surface=False)
                
                if interiores['SelectedPoints'] == [1]:     # dentro
                    CPoints.append(centers.points.flatten())
                    id_interior.append(i)       

            i+=1

        self.seekers  = np.array(CPoints)
        print("Seekers Fin:", self.seekers.shape)
        
        # Wall distance
        self.dwall = []
        start = start[id_interior]
        for i,p in enumerate(self.seekers):
            self.dwall.append(np.linalg.norm(p - start[i])) 
        self.dwall = np.array(self.dwall)
        m, s = self.dwall.mean(), self.dwall.std()
        print("dwall (mu,std):", m, s)
        ii = self.dwall > m 
        self.dwall[ii] = m 

seeks = Seekers("kk")
seeks.show()




#CPoints = np.loadtxt(scaso+"_pos.txt")
#dwall   = np.loadtxt(scaso+"_dwall.txt")

#data = {'caso1': [inlet=2190, radius=2.5, min_length=10],[max_neighbours=12, goals_dist = 0.5]}

#t = VesselTree(seeks.data_path, seeks.stlfile, seeks.dwall, seeks.seekers)
#t.find_paths_from(inlet=2097, radius=1.5*seeks.dwall, min_length=10)
#t.build_tree(max_neighbours=8, goals_dist = 0.05, use_dist_in_h= False)
#t.plot_tree(show_mesh=True, show_boundaries=False, show_points=False)

# exit()
# data_path = "../boids3D/aortas_con_carotidas/"
# caso      = "01_1175145_SA"
# t = VesselTree(data_path, caso)
# t.find_paths_from(inlet=249, radius= 12.5, min_length= 5)
# t.build_tree(max_neighbours=16, goals_dist = 4, use_dist_in_h= True)
# t.plot_tree(show_mesh=True, show_boundaries=True, show_points=True)

# data_path = "../boids3D/seekers/CMBE22_centerline/"
# caso      = "LCA_fixed"
# t = VesselTree(data_path, caso)
# t.find_paths_from(inlet=25, radius=4.0, min_length=2)
# t.build_tree(max_neighbours=16, goals_dist = 1.5, use_dist_in_h= True)
# t.plot_tree(show_mesh=True, show_boundaries=False, show_points=False)

# data_path = "../boids3D/seekers/CMBE22_centerline/"
# caso      = "test_pipes_tris_dec9"
# t = VesselTree(data_path, caso)
# t.find_paths_from(inlet=1409, radius=1.2, min_length=8)
# t.build_tree(max_neighbours=16, goals_dist = 1, use_dist_in_h= True)
# t.plot_tree(show_mesh=True, show_boundaries=False, show_points=False)