load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl" 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"  

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
  var = f->precTot
  var = deal_with_nan(var)

  dims = dimsizes(var)
  ndims = dimsizes(dims)

  mdname = "/oldhome/apbarret/projects/ancillary/masks"
  mfname = "arctic_mask_1x1deg.nc"                  
  
  mf = addfile(mdname+"/"+mfname, "r")
  mask1d = landsea_mask(mf->arctic_mask, var&lat, var&lon)
  masknd = conform_dims(dims, mask1d, (/ndims-2, ndims-1/))
  varMsk = mask( var, masknd .eq. 6, True)
  copy_VarCoords(var, varMsk)
  
  wks = gsn_open_wks("png","test_landsea_mask")
  gsn_define_colormap(wks, "MPL_YlGnBu")

  res            = True                         ; plot mods desired

  ;res@gsnDraw             = False           ; don't draw
  ;res@gsnFrame            = False           ; don't advance frame

  res@gsnPolar   = "NH"                         ; specify the hemisphere
  res@mpMinLatF  = 50                           ; minimum lat to plot

  res@mpFillOn   = False

  res@cnFillOn          = True                  ; color fill
  res@cnLinesOn             = False    ; turn of contour lines
;;  res@cnFillMode            = "CellFill" ;"RasterFill"
  res@cnInfoLabelOn         = False
  res@cnLineLabelsOn        = False

  res@cnLevelSelectionMode = "ManualLevels"
  res@cnMinLevelValF    = 50.
  res@cnMaxLevelValF    = 900.
  res@cnLevelSpacingF   = 50.                    ; interval spacing

  res@lbLabelBarOn         = False

  res@gsnRightString = " "
  res@gsnLeftString  = " "

  plot = gsn_csm_contour_map_polar(wks, varMsk(0,:,:), res)
  
end