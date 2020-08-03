
"""
Main Classes of volpy
"""

import numpy as np
import pyvista as pv
import itertools
import pandas as pd
import networkx as nx
import compas
from compas.datastructures import Mesh
import concurrent.futures
import warnings

__author__ = "Shervin Azadi, and Pirouz Nourian"
__copyright__ = "???"
__credits__ = ["Shervin Azadi", "Pirouz Nourian"]
__license__ = "???"
__version__ = "0.0.2"
__maintainer__ = "Shervin Azadi"
__email__ = "shervinazadi93@gmail.com"
__status__ = "Dev"

class lattice(np.ndarray):

    def __new__(subtype, bounds, unit=1, dtype=float, buffer=None, offset=0,
                strides=None, order=None, default_value=None):

        # extracting min and max from bound and discrtizing it
        bounds = np.array(bounds)
        minbound = np.rint(bounds[0] / unit).astype(int)
        maxbound = np.rint(bounds[1] / unit).astype(int)
        bounds = np.array([minbound, maxbound])*unit

        # unit nparray
        unit = np.array(unit)

        # raise value error if the size of unit is neighter 1 nor the length of the minimum
        if unit.size != 1 and unit.size != minbound.size:
            raise ValueError(
                'the length of unit array needs to be either 1 or equal to the min/max arrays')

        # calculating shape based on bounds and unit
        shape = 1 + maxbound - minbound

        # set defualt value
        if default_value != None:
            buffer = np.tile(
                default_value, shape)
            #obj = obj * 0 + default_value

        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to lattice.__array_finalize__
        obj = super(lattice, subtype).__new__(subtype, shape, dtype,
                                              buffer, offset, strides,
                                              order)

        # set the  'bounds' attribute
        obj.bounds = bounds
        # set the attribute 'unit' to itself if it has the same size as the minimum,
        # if the size is 1, tile it with the size of minimum vector
        obj.unit = unit if unit.size == minbound.size else np.tile(
            unit, minbound.size)

        # init an empty connectivity
        obj.connectivity = None
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(lattice, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. lattice():
        #    obj is None
        #    (we're in the middle of the lattice.__new__
        #    constructor, and self.bounds will be set when we return to
        #    lattice.__new__)
        if obj is None:
            return
        # From view casting - e.g arr.view(lattice):
        #    obj is arr
        #    (type(obj) can be lattice)
        # From new-from-template - e.g lattice[:3]
        #    type(obj) is lattice
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'bounds', because this
        # method sees all creation of default objects - with the
        # lattice.__new__ constructor, but also with
        # arr.view(lattice).
        self.bounds = getattr(obj, 'bounds', None)
        self.bounds = getattr(obj, 'bounds', None)
        self.unit = getattr(obj, 'unit', None)
        self.connectivity = getattr(obj, 'connectivity', None)
        # We do not need to return anything

    @property
    def minbound(self):
        return self.bounds[0]

    @property
    def maxbound(self):
        return self.bounds[1]

    @property
    def centroids(self):
        # extract the indicies of the True values # with sparse matrix we dont need to search
        point_array = np.argwhere(self == True)
        # convert to float
        point_array = point_array.astype(float)
        # multply by unit
        point_array *= self.unit
        # move to minimum
        point_array += self.minbound
        # return as a point cloud
        return cloud(point_array, dtype=float)

    def fast_vis(self, plot, show_outline=True, show_centroids=True):

        # Set the grid dimensions: shape + 1 because we want to inject our values on the CELL data
        grid = pv.UniformGrid()
        grid.dimensions = np.array(self.shape) + 1
        # The bottom left corner of the data set
        grid.origin = self.minbound - self.unit * 0.5
        grid.spacing = self.unit  # These are the cell sizes along each axis
        # Add the data values to the cell data
        grid.cell_arrays["values"] = self.flatten(
            order="F").astype(float)  # Flatten the array!
        # filtering the voxels
        threshed = grid.threshold([0.9, 1.1])

        # adding the voxels: light red
        plot.add_mesh(threshed, show_edges=True, color="#ff8fa3", opacity=0.3, label="Cells")

        if show_outline:
            # adding the boundingbox wireframe
            plot.add_mesh(grid.outline(), color="grey", label="Domain")

        if show_centroids:
            # adding the voxel centeroids: red
            plot.add_mesh(pv.PolyData(self.centroids), color='#ff244c', point_size=5, render_points_as_spheres=True, label="Cell Centroidss")

        return plot

    def fast_notebook_vis(self, plot, show_outline=True, show_centroids=True):

        # Set the grid dimensions: shape + 1 because we want to inject our values on the CELL data
        grid = pv.UniformGrid()
        grid.dimensions = np.array(self.shape) + 1
        # The bottom left corner of the data set
        grid.origin = self.minbound - self.unit * 0.5
        grid.spacing = self.unit  # These are the cell sizes along each axis
        # Add the data values to the cell data
        grid.cell_arrays["values"] = self.flatten(
            order="F").astype(float)  # Flatten the array!
        # filtering the voxels
        threshed = grid.threshold([0.9, 1.1])

        # adding the voxels: light red
        plot.add_mesh(threshed, color="#ff8fa3", opacity=0.3)
        # plot.add_mesh(threshed, show_edges=True, color="#ff8fa3", opacity=0.3, label="Cells")

        if show_outline:
            # adding the boundingbox wireframe
            plot.add_mesh(grid.outline(), color="grey")
            # plot.add_mesh(grid.outline(), color="grey", label="Domain")

        if show_centroids:
            # adding the voxel centeroids: red
            plot.add_points(pv.PolyData(self.centroids), color='#ff244c')
            # plot.add_mesh(pv.PolyData(self.centroids), color='#ff244c', point_size=5, render_points_as_spheres=True, label="Cell Centroidss")

        return plot

    def find_connectivity(self, stencil):
        pass


class cloud(np.ndarray):

    def __new__(subtype, point_array, dtype=float, buffer=None, offset=0,
                strides=None, order=None):

        # extracting the shape from point_array
        shape = point_array.shape
        # using the point_array as the buffer
        buffer = point_array.flatten(order="C")

        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to cloud.__array_finalize__
        obj = super(cloud, subtype).__new__(subtype, shape, dtype,
                                            buffer, offset, strides,
                                            order)

        # set the  'bounds' attribute
        obj.bounds = np.array([obj.min(axis=0), obj.max(axis=0)])

        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(cloud, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. cloud():
        #    obj is None
        #    (we're in the middle of the cloud.__new__
        #    constructor, and self.bounds will be set when we return to
        #    cloud.__new__)
        if obj is None:
            return
        # From view casting - e.g arr.view(cloud):
        #    obj is arr
        #    (type(obj) can be cloud)
        # From new-from-template - e.g cloud[:3]
        #    type(obj) is cloud
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'bounds', because this
        # method sees all creation of default objects - with the
        # cloud.__new__ constructor, but also with
        # arr.view(cloud).
        self.bounds = getattr(obj, 'bounds', None)
        # We do not need to return anything

    @property
    def minbound(self):
        return self.bounds[0]

    @property
    def maxbound(self):
        return self.bounds[1]

    def regularize(self, unit, **kwargs):
        """[summary]

        Arguments:
            unit {[float or array of floats]} -- [the unit separation between cells of lattice]

        Keyword Arguments:
            closed {[Boolean]} -- [False by default. If the cell intervals are closed intervals or not.]

        Raises:
            ValueError: [unit needs to be either a float or an array of floats that has the same dimension of the points in the point cloud]

        Returns:
            [lattice] -- [a boolian latice representing the rasterization of point cloud]
        """
        ####################################################
        # INPUTS
        ####################################################
        unit = np.array(unit)
        if unit.size != 1 and unit.size != self.bounds.shape[1]:
            raise ValueError(
                'the length of unit array needs to be either 1 or equal to the dimension of point cloud')
        elif unit.size == 1:
            unit = np.tile(unit, (1, self.bounds.shape[1]))

        closed = kwargs.get('closed', False)

        ####################################################
        # PROCEDURE
        ####################################################

        if closed:
            # retrieve the identity matrix as a list of main axes
            axes = np.identity(unit.size).astype(int)
            # R3 to Z3 : finding the closest voxel to each point
            point_scaled = self / unit
            # shift the hit points in each 2-dimension (n in 1-axes) backward and formard (s in [-1,1]) and rint all the possibilities
            vox_ind = [np.rint(point_scaled + unit * n * s * 0.001) for n in (1-axes) for s in [-1, 1]]
            vox_ind = np.vstack(vox_ind)
        else:
            vox_ind = np.rint(self / unit).astype(int)

        # removing repetitions
        unique_vox_ind = np.unique(vox_ind, axis=0).astype(int)

        # mapping the voxel indicies to real space
        reg_pnt = unique_vox_ind * unit

        # initializing the volume
        l = lattice([self.minbound, self.maxbound], unit=unit,
                    dtype=bool, default_value=False)

        # mapp the indicies to start from zero
        mapped_ind = unique_vox_ind - np.rint(l.bounds[0]/l.unit).astype(int)

        # setting the occupied voxels to True
        l[mapped_ind[:, 0], mapped_ind[:, 1], mapped_ind[:, 2]] = True

        ####################################################
        # OUTPUTS
        ####################################################

        return l

    def fast_vis(self, plot):

        # adding the original point cloud: blue
        plot.add_mesh(pv.PolyData(self), color='#2499ff', point_size=3, render_points_as_spheres=True, label="Point Cloud")

        return plot

    def fast_notebook_vis(self, plot):

        # adding the original point cloud: blue
        plot.add_points(pv.PolyData(self), color='#2499ff')

        return plot


def expand_stencil(stencil):
    locations = np.argwhere(stencil) - (stencil.shape[0] - 1) / 2
    # calculating the distance of each neighbour
    sums = np.abs(locations).sum(axis=1)
    # sorting to identify the main cell
    order = np.argsort(sums)
    # sort and return
    return locations[order].astype(int)


def create_stencil(type_str, steps, clip=None):
    # check if clip is specified. if it is not, set it to the steps
    if clip == None:
        clip = steps
    # von neumann neighborhood
    if type_str == "von_neumann":
        # https://en.wikipedia.org/wiki/Von_Neumann_neighborhood
        # claculating all the possible shifts to apply to the array
        shifts = np.array(list(itertools.product(
            list(range(-clip, clip+1)), repeat=3)))

        # the number of steps that the neighbour is appart from the cell (setp=1 : 6 neighbour, step=2 : 18 neighbours, step=3 : 26 neighbours)
        shift_steps = np.sum(np.absolute(shifts), axis=1)
        # check the number of steps
        chosen_shift_ind = np.argwhere(shift_steps <= steps).ravel()
        # select the valid indices from shifts variable, transpose them to get separate indicies in rows, add the number of steps to make this an index
        locs = np.transpose(shifts[chosen_shift_ind]) + clip

        stencil = np.zeros((clip*2+1, clip*2+1, clip*2+1)).astype(int)
        stencil[locs[0], locs[1], locs[2]] = 1
    elif type_str == "moore":
        # https://en.wikipedia.org/wiki/Moore_neighborhood
        raise NotImplementedError
    else:
        raise ValueError(
            'non-valid neighborhood type for stencil creation')
    return stencil


def scatter(bounds, count):
    """[summary]

    Arguments:
        bounds {[2d array]} -- [array of two vectors, indicating the bounding box of the scattering envelope with a minimum and maximum of the bounding box]
        count {[int]} -- [number of the points to scatter within the bounding box]

    Returns:
        [cloud] -- [returns a cloud object countaing the coordinates of the scattered points]
    """
    point_array = np.random.uniform(
        bounds[0], bounds[1], (count, bounds.shape[1]))
    return cloud(point_array)


def cloud_from_csv(file_path, delimiter=','):

    point_array = np.genfromtxt(file_path, delimiter=delimiter)
    return cloud(point_array)


def lattice_from_csv(file_path):

    # read the voxel 3-dimensional indices
    ind_flat = np.genfromtxt(file_path, delimiter=',',
                             skip_header=8, usecols=(0, 1, 2)).astype(int)

    # read the voxel values
    vol_flat = np.genfromtxt(
        file_path, delimiter=',', skip_header=8, usecols=(3)).astype(int)

    # read volume meta data
    meta = np.genfromtxt(
        file_path, delimiter='-', skip_header=1, max_rows=3, usecols=(1, 2, 3))
    unit = meta[0]
    min_bound = meta[1]
    volume_shape = meta[2].astype(int)
    max_bound = min_bound + unit * volume_shape

    # reshape the 1d array to get 3d array
    vol = vol_flat.reshape(volume_shape)

    # initializing the lattice
    l = lattice([min_bound, max_bound], unit=unit,
                dtype=bool, default_value=False)

    # setting the latice equal to volume
    l[ind_flat[:, 0], ind_flat[:, 1], ind_flat[:, 2]
      ] = vol[ind_flat[:, 0], ind_flat[:, 1], ind_flat[:, 2]]

    return l


def find_neighbours(lattice, stencil):

    # flatten the lattice
    lattice_flat = lattice.ravel()

    # the id of voxels (0,1,2, ... n)
    lattice_inds = np.arange(lattice.size).reshape(lattice.shape)

    # removing the indecies that are not filled in the volume
    lattice_inds = ((lattice_inds + 1) * lattice) - 1

    # offset the 1-dimensional indices of the voxels that is rshaped to volume shape with value -1
    lattice_inds_paded = np.pad(lattice_inds, (1, 1), mode='constant',
                                constant_values=(-1, -1))

    # flatten
    lattice_inds_paded_flat = lattice_inds_paded.ravel()

    # index of padded cells in flatten
    origin_flat_ind = np.argwhere(lattice_inds_paded_flat != -1).ravel()

    # retrievig all the possible shifts corresponding to the neighbours defined in stencil
    shifts = expand_stencil(stencil)

    # gattering all the replacements in the collumns
    replaced_columns = [
        np.roll(lattice_inds_paded, shift, np.arange(3)).ravel() for shift in shifts]

    # stacking the columns and removing the pads (and also removing the neighbours of the empty voxels since we have tagged them -1 like paddings)
    cell_neighbors = np.stack(replaced_columns, axis=-1)[origin_flat_ind]

    return cell_neighbors


def mesh_sampling(geo_mesh, unit, tol=1e-06, **kwargs):
    """This algorithm samples a mesh based on unit size

    Args:
        geo_mesh ([COMPAS Mesh]): [description]
        unit ([numpy array]): [description]
        tol ([type], optional): [description]. Defaults to 1e-06.

    Returns:
        [type]: [description]
    """
    ####################################################
    # INPUTS
    ####################################################

    dim_num = unit.size
    multi_core_process = kwargs.get('multi_core_process', False)
    return_ray_origin = kwargs.get('return_ray_origin', False)

    # compare voxel size and tolerance and warn if it is not enough
    if min(unit) * 1e-06 < tol:
        warnings.warn(
            "Warning! The tolerance for rasterization is not small enough, it may result in faulty results or failure of rasterization. Try decreasing the tolerance or scaling the geometry.")

    ####################################################
    # Initialize the volumetric array
    ####################################################

    # retrieve the bounding box information
    mesh_bb = np.array(geo_mesh.bounding_box())
    mesh_bb_min = np.amin(mesh_bb, axis=0)
    mesh_bb_max = np.amax(mesh_bb, axis=0)
    mesh_bb_size = mesh_bb_max - mesh_bb_min

    # find the minimum index in discrete space
    mesh_bb_min_z3 = np.rint(mesh_bb_min / unit).astype(int)
    # calculate the size of voxelated volume
    vol_size = np.ceil((mesh_bb_size / unit)+1).astype(int)
    # initiate the 3d array of voxel space called volume
    vol = np.zeros(vol_size)

    ####################################################
    # claculate the origin and direction of rays
    ####################################################

    # increasing the vol_size by one to accomodate for shooting from corners
    vol_size_off = vol_size + 1
    # retriev the voxel index for ray origins
    hit_vol_ind = np.indices(vol_size_off)
    vol_ind_trans = np.transpose(hit_vol_ind) + mesh_bb_min_z3
    hit_vol_ind = np.transpose(vol_ind_trans)

    # retieve the ray origin indicies
    ray_orig_ind = [np.take(hit_vol_ind, 0, axis=d + 1).transpose((1,
                                                                   2, 0)).reshape(-1, 3) for d in range(dim_num)]
    ray_orig_ind = np.vstack(ray_orig_ind)

    # retrieve the direction of ray shooting for each origin point
    normals = np.identity(dim_num).astype(int)
    # tile(stamp) the X-ray direction with the (Y-direction * Z-direction) . Then repeat this for all dimensions
    ray_dir = [np.tile(normals[d], (vol_size_off[(d+1) % dim_num]*vol_size_off[(d+2) % dim_num], 1))
               for d in range(dim_num)]  # this line has a problem given the negative indicies are included now
    ray_dir = np.vstack(ray_dir)

    # project the ray origin + shift it with half of the voxel siz to move it to corners of the voxels
    ray_orig = ray_orig_ind * unit + unit * -0.5  # * (1 - ray_dir)

    # project the ray origin
    proj_ray_orig = ray_orig * (1 - ray_dir)

    ####################################################
    # intersection
    ####################################################

    samples = []

    # check if multiprocessing is allowed
    if multi_core_process:
        # open the context manager
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # submit the processes
            results = [executor.submit(
                intersect, geo_mesh, face, unit, mesh_bb_size, ray_orig, proj_ray_orig, ray_dir, tol) for face in geo_mesh.faces()]
            # fetch the results
            for f in concurrent.futures.as_completed(results):
                samples.extend(f.result())
    else:
        # iterate over the faces
        for face in geo_mesh.faces():
            face_hit_pos = intersect(geo_mesh, face, unit, mesh_bb_size,
                                         ray_orig, proj_ray_orig, ray_dir, tol)
            samples.extend(face_hit_pos)

    ####################################################
    # OUTPUTS
    ####################################################

    # set the output list
    out = [cloud(np.array(samples))]
    # check if the ray origins are requested
    if return_ray_origin:
        out.append(cloud(np.array(ray_orig)))

    return tuple(out)


def intersect(geo_mesh, face, unit, mesh_bb_size, ray_orig, proj_ray_orig, ray_dir, tol):
    face_hit_pos = []
    face_verticies_xyz = geo_mesh.face_coordinates(face)

    if len(face_verticies_xyz) != 3:
        return([])

    face_verticies_xyz = np.array(face_verticies_xyz)

    # check if any coordinate of the projected ray origin is in betwen the max and min of the coordinates of the face
    min_con = proj_ray_orig >= np.amin(
        face_verticies_xyz, axis=0)*(1 - ray_dir)
    max_con = proj_ray_orig <= np.amax(
        face_verticies_xyz, axis=0)*(1 - ray_dir)
    in_range_rays = np.all(min_con * max_con, axis=1)

    # retrieve the ray indicies that are in range
    in_rang_ind = np.argwhere(in_range_rays).flatten()

    # iterate over the rays
    for ray in in_rang_ind:
        # retrieve ray direction
        direction = ray_dir[ray]
        # retrieve ray origin
        orig_pos = ray_orig[ray]
        # calc the destination of ray (max distance that it needs to travel)
        # this line has a problem given the negative indicies are included now
        dest_pos = orig_pos + direction * mesh_bb_size

        # intersction
        # compas version
        # hit_pt = compas.geometry.intersection_line_triangle((orig_pos, dest_pos), face_verticies_xyz, tol=tol)
        # Translated from Pirouz C#
        hit_pt = TriangleLineIntersect(
            (orig_pos, dest_pos), face_verticies_xyz, tol=tol)
        if hit_pt is not None:
            face_hit_pos.append(hit_pt)

    return(face_hit_pos)


def TriangleLineIntersect(L, Vx, tol=1e-06):
    """
    Computing the intersection of a line with a triangle
    Algorithm from http://geomalgorithms.com/a06-_intersect-2.html
    C# implementation from https://github.com/Pirouz-Nourian/Topological_Voxelizer_CSharp/blob/master/Voxelizer_Functions.cs

    Args:
        L ([2d np array]): List of two points specified by their coordinates
        Vx ([2d np array]): List of three points specified by their coordinates
        tol ([float], optional): tolerance. Defaults to 1e-06.

    Raises:
        ValueError: If the triangle contains more than three vertices

    Returns:
        [np array]: [description]
    """

    ####################################################
    # INPUTS
    ####################################################

    if len(Vx) != 3:
        raise ValueError('A triangle needs to have three vertexes')
    
    ####################################################
    # PROCEDURE
    ####################################################

    # finding U & V vectors
    O = Vx[0]
    U = Vx[1] - Vx[0]
    V = Vx[2] - Vx[0]
    # finding normal vector
    N = surface_normal_newell_vectorized(Vx) # np.cross(U, V)

    Nomin = np.dot((O - L[0]), N)
    Denom = np.dot(N, (L[1] - L[0]))

    if Denom != 0:
        alpha = Nomin / Denom

        # L[0] + np.dot(alpha, (L[1] - L[0])): parameter along the line where it intersects the plane in question, only if not paralell to the plane
        W = L[0] + np.dot(alpha, (L[1] - L[0])) - O

        UU = np.dot(U, U)
        VV = np.dot(V, V)
        UV = np.dot(U, V)
        WU = np.dot(W, U)
        WV = np.dot(W, V)

        STDenom = UV**2 - UU * VV

        s = (UV * WV - VV * WU) / STDenom
        t = (UV * WU - UU * WV) / STDenom

    ####################################################
    # OUTPUTS
    ####################################################

        if s + tol >= 0 and t + tol >= 0 and s + t <= 1 + 2*tol:
            Point = O + s * U + t * V
            return Point
        else:
            return None
    else:
        return None


def surface_normal_newell_vectorized(poly):
    """    
    https://stackoverflow.com/questions/39001642/calculating-surface-normal-in-python-using-newells-method
    Newell Method explained here: https://www.researchgate.net/publication/324921216_Topology_On_Topology_and_Topological_Data_Models_in_Geometric_Modeling_of_Space

    Args:
        poly ([2d np array]): List of vertices specified by their coordinates 

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """

    # This section is the vectorized equivalent of this code

    """
    n = np.array([0.0, 0.0, 0.0])

    for i in range(3):
        j = (i+1) % 3
        n[0] += (poly[i][1] - poly[j][1]) * (poly[i][2] + poly[j][2])
        n[1] += (poly[i][2] - poly[j][2]) * (poly[i][0] + poly[j][0])
        n[2] += (poly[i][0] - poly[j][0]) * (poly[i][1] + poly[j][1])
    """

    poly_10 = np.roll(poly, [-1, 0], np.arange(2))
    poly_01 = np.roll(poly, [0, -1], np.arange(2))
    poly_11 = np.roll(poly, [-1, -1], np.arange(2))

    n = np.roll(np.sum((poly - poly_10) * (poly_01 + poly_11), axis=0), -1, 0)
   
    norm = np.linalg.norm(n)
    if norm == 0:
        raise ValueError('zero norm')
    else:
        normalised = n/norm

    return normalised
