########################################
# SPECBfield.py: setup the SPEC Bfield system for oculus ODE solver
# written by @zhisong (zhisong.qu@anu.edu.au)
#
from .SPECProblem import SPECProblem
import numpy as np

class SPECBfield(SPECProblem):
    """
    Class that used to setup the SPEC bfield problem for interfacing Fortran, used in ODE solver.
    Call signature:
        spec_bfield = SPECBfield(spec_data, lvol) 

    Contains:
        f - function to compute the RHS of the ODE
        f_tangent - function to compute the RHS of the ODE, with tangent
        coords_convert - function that converts curvilinear coordinates to real coordinates
    """
    problem_size = 2


    # by default plotting the RZ plane
    poincare_plot_type = 'RZ'
    poincare_plot_xlabel = 'R(m)'
    poincare_plot_ylabel = 'Z(m)'

    def __init__(self, spec_data, lvol):
        '''Set up the equilibrium for use of the fortran module 
        parameters:
            spec_data -- the SPEC data generated by py_spec.SPEC
            lvol -- which volume we are interested in, from 1 to spec_data.input.Mvol
        '''
        super().__init__(spec_data, lvol)
        if self.Igeometry == 1:
            self.poincare_plot_type = 'yx'
            self.poincare_plot_xlabel = '\theta'
            self.poincare_plot_ylabel = 'R'
        elif self.Igeometry == 2:
            pass
        elif self.Igeometry == 3:
            pass
        else:
            raise Exception('Unknown Igeometry!')

    def f(self, zeta, st, arg1=None):
        '''Python wrapper for magnetic field ODE RHS 
        parameters:
            zeta -- the zeta coordinate
            st -- array size 2, the (s, theta) coordinate
            arg1 -- parameter for the ODE, not used here

        return:
            array size 2, the RHS of the ODE
        '''
        return self.fortran_module.bfield.get_bfield(zeta, st)

    def f_tangent(self, zeta, st, arg1=None):
        '''Python wrapper for magnetic field ODE RHS, with RHS
        parameters:
            zeta -- the zeta coordinate
            st -- array size 6, the (s, theta, ds1, dtheta1, ds2, dtheta2) coordinate
            arg1 -- parameter for the ODE, not used here

        return:
            array size 6, the RHS of the ODE
        '''
    #return self.fortran_module.bfield.get_bfield_tangent(zeta, st)

    def convert_coords(self, stz):
        '''Python wrapper for getting the xyz coordinates from stz
        parameters:
            stz -- the stz coordinate

        return:
            the xyz coordinates
        '''
        xyz = self.fortran_module.coords.get_xyz(stz)
        
        # depending on the geometry, return RZ or yx
        if self.Igeometry == 1:
            # for a slab, return x=R, y=theta, z=zeta
            return np.array([xyz[0], stz[1]*self.rpol, stz[2]*self.rtor], dtype=np.float64)
        if self.Igeometry == 2:
            # for cylinderical geometry, return x=r*cos theta, y=zeta*rtor, z=sin theta
            return np.array([xyz[0]*np.cos(stz[1]), stz[2]*self.rtor, xyz[0]*np.sin(stz[1])], dtype=np.float64)
        if self.Igeometry == 3:
            # for toroidal geometry, return x=R, y=zeta, z=Z
            return xyz
