import numpy as np
import heapq as hp
from scipy.spatial import KDTree
import pyvista as pv
from multiprocessing import Process

class paths_tree:
    def __init__(self, fname) :
        self.fname = fname
        self.nodes      = set()
        self.tree       = {}
        self.joints     = []
        self.outlets    = []
        self.inlet      = -1
        self.domain     = []
    
    def init_tree(self, _inlet, _outlets, _domain) :
        self.nodes      = set()
        self.tree       = {}
        self.joints     = []
        self.outlets    = _outlets
        self.inlet      = _inlet
        self.domain     = _domain
    
    def build_tree_from_paths(self, paths):
        self.joints = []
        main_branch                 = paths[0]              # the longest
        self.tree[self.inlet]       = [main_branch] 
        for n in main_branch:
            self.nodes.add(n) 
        paths.remove(main_branch)
        print("Main Branch Length: ", len(self.tree[self.inlet]))
        
        # inserto el resto de caminos en el arbol
        # branch = path desde el outlet hasta el primer nodo del arbol comun 
        for path in paths:
            rpath = reversed(path)
            new_branch = []
            for n in rpath:
                if n not in self.nodes:
                    new_branch.append(n)
                    self.nodes.add(n) 
                else:
                    break

            # Guardo el joint por el que conecto el camino
            if n not in self.joints: self.joints.append(n)
            new_branch.append(n)
            branch_outlet = new_branch[0]
            if len(new_branch) > 0: 
                if branch_outlet not in self.tree:
                    self.tree[branch_outlet] = [new_branch]
                    print("path outlet-joint:", new_branch[0],n )
                else:
                    self.tree[branch_outlet].append(new_branch)

    def load(self,):
        fin         = open(self.fname, "r")
        header      = fin.readline()
        header      = fin.readline()
        self.inlet  = int(fin.readline())
        header      = fin.readline()
        toks_out    = fin.readline().split()
        for soutlet in toks_out:
            self.outlets.append(int(soutlet))
        header      = fin.readline()
        toks_j      = fin.readline().split()
        for sjoint in toks_j:
            self.joints.append(int(sjoint))

        toks_npaths = fin.readline().split(':')
        npaths = int(toks_npaths[1])
        for i in range(npaths):
            line = fin.readline().strip().replace('[','').replace(']','')
            tpath = line.split(',')
            path = []
            for n in tpath:
                path.append(int(n))
            self.tree[path[0]] = path

        toks_dom = fin.readline().split(':')
        npoints = int(toks_dom[1])
        for i in range(npoints):
            line = fin.readline().replace('[','').replace(']','').rstrip()
            print(line)
            toks = line.split()
            print(toks)
            p = [float(toks[0]), float(toks[1]), float(toks[2])]
            self.domain.append(p) 

        self.domain = np.array(self.domain)    
        fin.close()
        
        return self.tree, self.joints, []
                   
    def save(self,):
        fout = open(self.fname, "w")
        fout.write("Tree model V.0\n")
        fout.write("Inlet:\n")
        fout.write(str(self.inlet)+'\n')
        fout.write("Outlets:\n")
        for o in self.outlets:
            fout.write(str(o)+" ")
        fout.write('\n')
        fout.write("Joints:\n")
        for j in self.joints:
            fout.write(str(j)+" ")
        fout.write('\n')
        fout.write("NPaths:"+str(len(self.tree))+"\n")
        for p in self.tree:
            path = self.tree[p]
            for n in path:
                fout.write(str(n)+" ")
            fout.write('\n')
        fout.write("NPoints:"+str(len(self.domain))+"\n")
        for p3 in self.domain:
            fout.write(str(p3)+"\n")
        fout.write("\n")
        fout.close()
        
        return               


class VTree:
    
    def __init__(self, _inlet, _outlets, _seekers, _dwall, _dwall_outlets) :
        self.inlet              = _inlet
        self.outlets            = _outlets
        self.domain             = _seekers
      
        # outlets al dominio (no son seekers)
        np_domain               = self.domain.shape[0]
        new_domain              = np.zeros([np_domain + self.outlets.shape[0], 3])
        new_domain[:np_domain]  = self.domain
        new_domain[np_domain:]  = self.outlets

        self.kdt                = KDTree(new_domain)
        self.domain             = new_domain

        dw_domain               = _dwall.shape[0]
        new_dwall               = np.zeros([dw_domain + self.outlets.shape[0]]) #inlet + outlets
        new_dwall[:dw_domain]   = _dwall
        new_dwall[dw_domain:]   = _dwall_outlets
        
        self.wall_distance      = new_dwall
        self.fcost              = lambda x : 1/new_dwall[x] # lambda x : 1 #

        # Ids of inlet and outlets in the domain
        outlets_id         = []
        for i, outlet in enumerate(self.outlets):
            d, id = self.kdt.query(outlet)
            if self.inlet == i:
                self.inlet = id
            else:
                outlets_id.append(id) 
                print(id,d)
        
        self.outlets = np.array(outlets_id)  # outlets pasan a ser un id del nuevo dominio
        self.paths_from_inlet = []
      
        
        print("Vtree created ")
        print("Vtree:: inlet   = ", self.inlet)
        print("Vtree:: outlets = ", self.outlets)
        print("Vtree:: domain  = ", self.domain.shape)
        print("Vtree:: wall distance  = ", self.wall_distance.shape)
        
        
    def succesors(self, id, radius_increment):
        dwall = self.wall_distance[id] + radius_increment
        sucs = self.kdt.query_ball_point(self.domain[id], r=dwall)
       
        return sucs
     
    def build_path(self, current_node, pointers):
        path = []
        previous = current_node

        while previous is not None:
            path.append(previous)
            previous =  pointers[previous]
        path.reverse()

        return path
    
    def path_to_outlet(self, outlet):
        path =  self.A_star(self.inlet, outlet, 0)
        inc = 0.02
        dwall_w = 0
        while len(path) == 0:
            dwall_w+=inc
            print("new path_to_outlet", outlet, dwall_w)
            path =  self.A_star(self.inlet, outlet, dwall_w)
        
        return path
             

    def from_inlet_to_outlets(self, ):
        
        self.paths_from_inlet = []
        for outlet in self.outlets:
            path = self.path_to_outlet(outlet)
            print("a*:", len(path))
            self.paths_from_inlet.append(path)

    def build_tree(self, ):
        
        self.from_inlet_to_outlets()

        if len(self.paths_from_inlet) > 0:
            paths = self.ordena_caminos(self.paths_from_inlet)
            npaths = len(paths)
            self.tree = paths_tree("model.tree")
            self.tree.init_tree(self.inlet, self.outlets, self.domain)
            self.tree.build_tree_from_paths(paths)
            self.tree.save()

            seekers_in_paths = set()
            for p in paths:
                for n in p:
                    if n != self.inlet and n not in self.outlets:
                        seekers_in_paths.add(n)


            return self.tree.tree, self.tree.joints, list(seekers_in_paths) 

    def A_star(self, id_ini, goal, radius_inc=0):
        
        dirs = {}
        pointers = {}
        pointers[id_ini] = None
       
        g = {}
        g[id_ini] = self.fcost(id_ini)
        h = {}
        h[id_ini] = 0 # self.heuristic(id_ini, goal)
        f = {}
        f[id_ini] = g[id_ini] + h[id_ini]
        
        OpenH = []
        hp.heappush(OpenH, (f[id_ini], id_ini))

        Open, Closed = set(), set()
        Open.add(id_ini)

        while OpenH != []:
            (f_current, id_current) = hp.heappop(OpenH)
            Open.remove(id_current)
            Closed.add(id_current)

            if id_current == goal:
                path = self.build_path(id_current, pointers)
                return path
            else: 
                Lsuc = self.succesors(id_current, radius_inc)
                nsuc = 0
                for s in Lsuc:
                    if pointers[id_current] != s:
                        nsuc+=1       
                        gs =  self.fcost(s)
                                    
                        s_in_open = s in Open
                        s_in_closed = s in Closed
                        if not s_in_open and not s_in_closed:
                            g[s] = gs
                            h[s] = 0 # self.heuristic(s, goal)
                            f[s] = g[s] + h[s]
                            hp.heappush(OpenH, (f[s], s))
                            Open.add(s)
                            pointers[s] = id_current
                    
                        elif s_in_open:
                            old = s
                            if gs < g[old] :
                                OpenH.remove((f[old],old))
                                g[old] = gs
                                pointers[old] = id_current
                                f[old] = g[old] + h[old]
                                hp.heappush(OpenH, (f[old], old))
                                
                        elif s_in_closed:
                            old = s
                            if gs < g[old] :
                                g[old] = gs
                                pointers[old] = id_current
                                f[old] = g[old] + h[old]
                                Closed.remove(old)
                                Open.add(old)
                                hp.heappush(OpenH, (f[old], old))
                if nsuc == 0: print("Oooooops")
               
        return []

    def heuristic(self, n, goal, use_dist_in_h = True):
        if use_dist_in_h:
            return np.linalg.norm(self.domain[goal] - self.domain[n])
        else:
            return 0
        
    def ordena_caminos(self, Lpaths):
        # ordeno los caminos del mas largo al mas corto
        Tree = []
        for path in Lpaths:
            hp.heappush(Tree, (len(path), path))

        Lpaths.clear()
        while Tree != []:
            (f, path) = hp.heappop(Tree)
            Lpaths.insert(0,path)
        
        return Lpaths
    
    def min_distance(self, p, goals):
        mind = 1e8
        id_min = -1
        for i, g in enumerate(goals):
            d = np.linalg.norm(g - p)
            if d < mind:
                mind = d
                id_min = i

        return mind, id_min

        