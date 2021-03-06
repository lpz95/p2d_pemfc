"""
Fickian Diffusion function (w/ advective term) in 1-D cartesian:
    This function takes in the TDY states at two adjacent points and uses
    average conditions at the boundary between them to calculate the mass flux
    by combining a gradient in mass fractions (Fickian diffusion) with a
    pressure driven gradient (advection term). Hence the name adf for advection
    diffusion flux.

    Positive flux implies net flux from the TDY1 node into the TDY2 node. Make
    sure to correctly emphasize this sign convention in runner codes."""

def fickian_adf(TDY1, TDY2, gas, p, tog):
    " Inputs to this function are as follows: "
    # TDY1, TDY2: temperature, density, and mass fractions [K, kg/m^3, -]
    # gas: cantera solution object to handle thermodynamics and properties
    # p: dictionary with 'wt1'(gdl), 'wt2'(cl), 'K_g', '1/dy', 'eps/tau2'
    # tog: toggle (i.e. 0 or 1) to turn function off from runner
    
    " Descriptions of the dictionary terms are as follows: "
    # 'gdl_wt', 'cl_wt': fractional dy of gdl and cl for weighted averages [-]
    # 'K_g': permeability of the porous domain [m^2]
    # '1/dy': inverse of distance between nodes [1/m]
    # 'eps/tau2': porosity of the domain divided by its tortuosity squared [-]
    
    # set state 1 properties:
    gas.TDY = TDY1
    D_k1 = gas.mix_diff_coeffs_mass
    rho1 = gas.density_mass
    mu1 = gas.viscosity
    P1 = gas.P
    Y1 = gas.Y
    rho_k1 = rho1*Y1
    
    # set state 2 properties:
    gas.TDY = TDY2
    D_k2 = gas.mix_diff_coeffs_mass
    rho2 = gas.density_mass
    mu2 = gas.viscosity
    P2 = gas.P
    Y2 = gas.Y
    rho_k2 = rho2*Y2
    
    # calculate average boundary properties:
    " when not at a boundary between two domains, wt terms shoud each be 0.5 "
    
    D_k = p['wt1']*D_k1 + p['wt2']*D_k2
    rho = p['wt1']*rho1 + p['wt2']*rho2
    mu = p['wt1']*mu1 + p['wt2']*mu2
    rho_k = p['wt1']*rho_k1 + p['wt2']*rho_k2
    
    # convective and diffusive driving terms:
    J_conv = -rho_k*p['K_g']*(P2 - P1)*p['1/dy'] / mu
    J_diff = -p['eps/tau2']*D_k*rho*(Y2 - Y1)*p['1/dy']
    
    # net mass flux of each species:
    mass_flux = tog*(J_conv + J_diff)
    
    # Output returns mass flux vector [kg/m^2-s]
    return mass_flux

"""
Fickian Diffusion function in 1-D radial:
    This function uses a finite difference method to approximate the radial 
    mass flux between two adjacent nodes. 
    
    When using this code:
    Positive flux implies net flux from the outer (rho_k1) node into the inner
    (rho_k2) node. Make sure to correctly emphasize this sign convention in
    runner codes."""
    
def radial_fdiff(rho_k1, rho_k2, p, node, ver, flag):
    " Inputs to this function are as follows: "
    # rho_k1, rho_k1: vectors with mass density of each species [kg/m^3]
    # p: parameters with terms as defined below
    # node: index to pull correct geometric values from p
    
    " Descriptions of the dictionary terms are as follows: "
    # 'D_eff': effective duffusion coefficient [m^2/s]
    # 'r_jph': radius at bounday between nodes (j+1/2) [m]
    # '1/dr': inverse of distance between nodes [1/m]
    
    " Core-shell only parameters: "
    # 'p_eff_SAnaf': effective Nafion SA based on Pt and max angle [-]
    
    " Flooded-agg only parameters: "
    # 'eps/tau2_n2': vol frac of Nafion over tortuosity**2 for inner agg [-]
    
    if ver == 1:
    	drho_dt = p['D_eff_naf'] *p['p_eff_SAnaf'] *p['eps/tau2_n2']\
            	*(p['r_jph'][node]**2 *(rho_k1 - rho_k2) *p['1/dr'][node])
    elif ver == 2:
        drho_dt = p['D_eff_naf'] *p['p_eff_SAnaf'] *p['eps/tau2_n2']\
                *(p['r_jph'][node]**2 *(rho_k1 - rho_k2) *p['1/dr'][node])\
                *p['1/r_j'][node]**2 *p['1/t_shl'][node]
                	
    # Output returns change in mass vector [kg/s] for ver = 1
    # Output returns change in density vector [kg/m^3-s] for ver = 2
    return drho_dt

