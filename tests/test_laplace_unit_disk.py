# 31.05.2007, c
# last revision: 25.02.2008

filename_mesh = 'database/tests/circle_sym.mesh'

material_1 = {
    'name' : 'coef',
    'mode' : 'here',
    'region' : 'Omega',
    'val' : 1.0,
}
material_2 = {
    'name' : 'm',
    'mode' : 'here',
    'region' : 'Omega',
    'K' : [[1.0, 0.0], [0.0, 1.0]],
}

field_1 = {
    'name' : 'a_harmonic_field',
    'dim' : (1,1),
    'flags' : (),
    'domain' : 'Omega',
    'bases' : {'Omega' : '2_3_P2'}
}

variable_1 = {
    'name' : 't',
    'kind' : 'unknown field',
    'field' : 'a_harmonic_field',
    'order' : 0,
}
variable_2 = {
    'name' : 's',
    'kind' : 'test field',
    'field' : 'a_harmonic_field',
    'dual' : 't',
}

region_1000 = {
    'name' : 'Omega',
    'select' : 'all',
}

region_1 = {
    'name' : 'Centre',
    'select' : 'nodes in (x < 1e-8) & (x > -1e-8) & (y < 1e-8) & (y > -1e-8)',
}

region_2 = {
    'name' : 'Gamma',
    'select' : 'nodes of surface',
    'can_cells' : True,
}

ebc_1 = {
    'name' : 't_centre',
    'region' : 'Centre',
    'dofs' : {'t.0' : 1.0},
}
ebc_2 = {
    'name' : 't_gamma',
    'region' : 'Gamma',
    'dofs' : {'t.0' : 0.0},
}

integral_1 = {
    'name' : 'i1',
    'kind' : 'v',
    'quadrature' : 'gauss_o2_d2',
}

integral_2 = {
    'name' : 'i2',
    'kind' : 'v',
    'quadrature' : 'gauss_o1_d1',
}

equations = {
    'Temperature' : """dw_laplace.i1.Omega( coef.val, s, t ) = 0"""
}

solution = {
    't' : '- 5.0 * (x - 0.5)',
}

solver_0 = {
    'name' : 'ls',
    'kind' : 'ls.umfpack',
}

solver_1 = {
    'name' : 'newton',
    'kind' : 'nls.newton',

    'i_max'      : 1,
    'eps_a'      : 1e-10,
    'eps_r'      : 1.0,
    'macheps'   : 1e-16,
    'lin_red'    : 1e-2, # Linear system error < (eps_a * lin_red).
    'ls_red'     : 0.1,
    'ls_red_warp' : 0.001,
    'ls_on'      : 1.1,
    'ls_min'     : 1e-5,
    'check'     : 0,
    'delta'     : 1e-6,
    'is_plot'    : False,
    'lin_solver' : 'umfpack',
    'matrix'    : 'internal', # 'external' or 'internal'
    'problem'   : 'nonlinear', # 'nonlinear' or 'linear' (ignore i_max)
}

fe = {
    'chunk_size' : 1000
}


from sfepy.base.testing import TestCommon

##
# 31.05.2007, c
class Test( TestCommon ):

    ##
    # 30.05.2007, c
    def from_conf( conf, options ):
        from sfepy.solvers.generic import solve_stationary

        problem, vec, data = solve_stationary( conf )

        test = Test( problem = problem, vec = vec, data = data,
                     conf = conf, options = options )
        return test
    from_conf = staticmethod( from_conf )

    ##
    # 31.05.2007, c
    # 02.10.2007
    def test_boundary_fluxes( self ):
        from sfepy.base.base import Struct
        from sfepy.fem.evaluate import eval_term_op, BasicEvaluator
        problem  = self.problem
        vec = self.vec

        region_names = ['Gamma']

        get_state = problem.variables.get_state_part_view
        state = vec.copy()
        
        problem.time_update( conf_ebc = {}, conf_epbc = {} )
#        problem.save_ebc( 'aux.vtk' )

        problem.apply_ebc( state )
        ev = BasicEvaluator( problem )
        aux = ev.eval_residual( state )[0]

        field = problem.variables['t'].field

        ok = True
        for ii, region_name in enumerate( region_names ):
            flux_term = 'd_hdpm_surfdvel.i2.%s( m.K, t )' % region_name
            val1 = eval_term_op( None, flux_term, problem )

            rvec = get_state( aux, 't', True )
            reg = problem.domain.regions[region_name]
            nods = reg.get_field_nodes( field, merge = True )
            val2 = rvec[nods].sum() # Assume 1 dof per node.

            eps = 1e-2
            ok = ok and ((abs( val1 - val2 ) < eps))
            self.report( '%d. %s: |%e - %e| = %e < %.2e'\
                         % (ii, region_name, val1, val2, abs( val1 - val2 ),
                            eps) )
        
        return ok
