import numpy as np
    
# Funcionalidades para VTK-WWW-VeselTrees : Arbol de vasos sanguineos (tubos)
#----------------------------------------------------------------------------



#####################################################################################################
# Calculo de inlet y outlets por defecto: 
#   Al pulsar el botón (checkbox) calculara y devolvera
#
# Outlets       : Lista con los Puntos centrales interiores de los tubos de salida del arbol
# Inlet         : Indice del Outlet (lista anterior) que corresponde con la entrada de flujo (inlet) 
# Outlets_WD    : Distancia a la pared (mesh) de cada outlet (outlet)

def default_inlet_outlets(mesh):
    
    outlets                 = []
    outlets_wall_distance   = []
    inlet                   = -1

    outlets_border          = mesh.extract_feature_edges(boundary_edges=True, manifold_edges=False, feature_edges=False)
    connected_cells         = outlets_border.connectivity()
    num_outlets             = len(np.unique(connected_cells['RegionId']))

    max_wall_dist           = 0
    for i in range(num_outlets):
        outlet_i    = connected_cells.threshold(value=[i,i], scalars = 'RegionId')
        centro      = np.mean(outlet_i.points[:], axis=0)
        outlets.append(centro)

        # wall distance to centro    
        closest_p = mesh.find_closest_point(centro)
        wall_dist = np.linalg.norm(mesh.points[closest_p] - centro)
        outlets_wall_distance.append(wall_dist)
        if wall_dist > max_wall_dist:
            max_wall_dist = wall_dist
            inlet    = i

    return inlet, outlets, outlets_wall_distance
                        
#####################################################################################################
