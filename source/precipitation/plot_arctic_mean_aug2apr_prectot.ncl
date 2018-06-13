;;----------------------------------------------------------------------
;; Generate a time series of Aug-Apr precipitation statistics for the
;; Arctic region.
;;
;; 2017-12-07 A.P.Barrett
;;----------------------------------------------------------------------

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl" 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"  

diri = "/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT"
fili = "era_interim.PRECIP_STATS.accumulation.annual.nc"

undef( "make_timeseries")
function make_timeseries(var)
begin

  dims = dimsizes(var)
  ndims = dimsizes(dims)

  nlat = dimsizes( var&lat )

  wgt = NormCosWgtGlobe(var&lat)
  
  mdname = "/oldhome/apbarret/projects/ancillary/masks"
  mfname = "arctic_mask_1x1deg.nc"                  

  ;; Get mask
  mf = addfile(mdname+"/"+mfname, "r")
  mask1d = landsea_mask(mf->arctic_mask, var&lat, var&lon)
  masknd = conform_dims(dims, mask1d, (/ndims-2, ndims-1/))

  varMsk = mask( var, masknd .eq. 1, False)

  varAvg = wgt_areaave_Wrap( varMsk, wgt, 1.0, 1)

  return( varAvg )

end

undef ("deal_with_nan")
function deal_with_nan(var)
begin
  var@_FillValue = default_fillvalue(typeof(var))
  if ( any(isnan_ieee(var)) ) then
    replace_ieeenan( var, var@_FillValue, 0)
  end if
  return var
end

begin

  ;; Get data
  ;; ERA-Interim
  diri = "/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT"
  fili = "era_interim.PRECIP_STATS.accumulation.annual.nc"
  f = addfile(diri+"/"+fili, "r")
  erai = f->precTot
  erai = deal_with_nan(erai)
  eraiAvg = make_timeseries(erai)
  print (eraiAvg)
  
  ;; CFSR
  diri = "/disks/arctic5_raid/abarrett/CFSR/PRATE"
  fili = "CFSR.flxf06.gdas.PRECIP_STATS.accumulation.annual.nc"
  f = addfile(diri+"/"+fili, "r")
  cfsr = f->precTot
  cfsr!1 = "lat"
  cfsr!2 = "lon"
  cfsr = deal_with_nan(cfsr)
  cfsrAvg = make_timeseries(cfsr)
  print (cfsrAvg)
  
  ;; MERRA2
  diri = "/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT"
  fili = "MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.nc4"
  f = addfile(diri+"/"+fili, "r")
  merra2 = f->precTot
  merra2 = deal_with_nan(merra2)
  merra2Avg = make_timeseries(merra2)
  print (merra2Avg)

  fo = addfile("reanalysis_arctic_mean_prectot.nc", "c")
  fo->erai = eraiAvg
  fo->cfsr = cfsrAvg
  fo->merra2 = merra2Avg
  
end