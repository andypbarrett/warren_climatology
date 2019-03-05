# warren_climatology

This repo contains python utilities to generate the Warren snow on sea ice snow depth and SWE climatologies reported in Warren et al (1999).

Climatologies are expressed as 2-dimensional quadratic functions of the form:

$H = H_0 + Ax + By + Cxy + Dx^2 + Ey^2$

Parameters $H_0, A, B, C, D, E$ are given in tables 1 and 2 of Warren et al (1999).  The functions are developed from snow obervations made at Soviet North Pole drifting stations between 1956 and 1991.  Parameter values are optimized using a least-square method.  Further details can be found in Warren et al (1999). 

The main workhorse functions are warren_climatology.snow_depth and warren_climatology.swe. These functions take latitude and longitude as scalars, 1D vectors or 2D grids.  Vectors and grids must be the same size.

Note: because these a functions negative values are generated outside of the region with data.  For example, in May, negative depths and SWE occur over the Kara and Barents Seas.  These values should be masked out.  See Figure 1 in Warren et al (1999) for extent of data. 

## References
Warren, S.G., I.G. Rigor, N. Untersteiner, V.F. Radionov, N.N. Bryazgin, Y.I. Aleksandrov, and R. Colony, 1999: Snow Depth on Arctic 
Sea Ice. J. Climate, 12, 1814–1829, https://doi.org/10.1175/1520-0442(1999)012<1814:SDOASI>2.0.CO;2 
