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
region = "arctic_ocean"

undef( "make_timeseries" )
function make_timeseries(var, region)
begin

  dims = dimsizes(var)
  ndims = dimsizes(dims)

  nlat = dimsizes( var&lat )

  wgt = NormCosWgtGlobe(var&lat)
  
  mdname = "/oldhome/apbarret/projects/ancillary/masks"
  mfname = "arctic_mask_1x1deg.nc"                  

  ;; Get mask
  if region .eq. "arctic_ocean" then
    mf = addfile(mdname+"/"+mfname, "r")
    mask1d = landsea_mask(mf->arctic_mask, var&lat, var&lon)
    masknd = conform_dims(dims, mask1d, (/ndims-2, ndims-1/))
    varMsk = mask( var, masknd .eq. 6, True)
  end if
  
  if ( region .eq. "north_of_80" ) then
    masknd = conform_dims( dims, var&lat, (/ (ndims-2) /) )
    varMsk = mask( var, masknd .gt. 80., True )
  end if

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
  eraiAvg = make_timeseries(erai, region)
  print (eraiAvg)
  
  ;; CFSR
  diri = "/disks/arctic5_raid/abarrett/CFSR/PRATE"
  fili = "CFSR.flxf06.gdas.PRECIP_STATS.accumulation.annual.nc"
  f = addfile(diri+"/"+fili, "r")
  cfsr = f->precTot
  cfsr!1 = "lat"
  cfsr!2 = "lon"
  cfsr = deal_with_nan(cfsr)
  cfsrAvg = make_timeseries(cfsr, region)
  print (cfsrAvg)
  
  ;; MERRA2
  diri = "/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT"
  fili = "MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.nc4"
  f = addfile(diri+"/"+fili, "r")
  merra2 = f->precTot
  merra2 = deal_with_nan(merra2)
  merra2Avg = make_timeseries(merra2, region)
  print (merra2Avg)

  ;; CFSR2
  diri = "/disks/arctic5_raid/abarrett/CFSR2/PRATE"
  fili = "CFSR2.flxf06.gdas.PRECIP_STATS.accumulation.annual.nc"
  f = addfile(diri+"/"+fili, "r")
  cfsr2 = f->precTot
  cfsr2!1 = "lat"
  cfsr2!2 = "lon"
  cfsr2 = deal_with_nan(cfsr2)
  cfsr2Avg = make_timeseries(cfsr2, region)
  print(cfsr2Avg)
  
  ;; MERRA
  diri = "/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT"
  fili = "MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.accumulation.annual.nc4"
  f = addfile(diri+"/"+fili, "r")
  merra = f->precTot
  merra = deal_with_nan(merra)
  merraAvg = make_timeseries(merra, region)
  print (merraAvg)

  ;; JRA25
  diri = "/disks/arctic5_raid/abarrett/JRA55/PRECTOT"
  fili = "fcst_phy2m.061_tprat.reg_tl319.PRECIP_STATS.accumulation.annual.nc4"
  f = addfile(diri+"/"+fili, "r")
  jra55 = f->precTot
  jra55 = deal_with_nan(jra55)
  jra55Avg = make_timeseries(jra55, region)
  print (jra55Avg)

  filo = "era_interim_arctic_mean_prectot_"+region+".nc" 
  if (isfilepresent(filo)) then
	system("rm "+filo)
  end if
  fo = addfile(filo, "c")
  fo->erai = eraiAvg

  filo = "cfsr_arctic_mean_prectot_"+region+".nc" 
  if (isfilepresent(filo)) then
	system("rm "+filo)
  end if
  fo = addfile(filo, "c")
  fo->cfsr = cfsrAvg
  
  filo = "cfsr2_arctic_mean_prectot_"+region+".nc" 
  if (isfilepresent(filo)) then
	system("rm "+filo)
  end if
  fo = addfile(filo, "c")
  fo->cfsr2 = cfsr2Avg
  
  filo = "merra2_arctic_mean_prectot_"+region+".nc" 
  if (isfilepresent(filo)) then
	system("rm "+filo)
  end if
  fo = addfile(filo, "c")
  fo->merra2 = merra2Avg
  
  filo = "merra_arctic_mean_prectot_"+region+".nc" 
  if (isfilepresent(filo)) then
	system("rm "+filo)
  end if
  fo = addfile(filo, "c")
  fo->merra = merraAvg
  
  filo = "jra55_arctic_mean_prectot_"+region+".nc" 
  if (isfilepresent(filo)) then
	system("rm "+filo)
  end if
  fo = addfile(filo, "c")
  fo->jra55 = jra55Avg
  
end
