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

begin

  ;; Get data
  ;; ERA-Interim
  diri = "/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT"
  fili = "era_interim.PRECIP_STATS.accumulation.annual.nc"
  f = addfile(diri+"/"+fili, "r")
  erai = f->nwetdays
  erai_avg = dim_avg_n_Wrap(erai(0:29,:,:),0)

  ;; CFSR
  diri = "/disks/arctic5_raid/abarrett/CFSR/PRATE"
  fili = "CFSR.flxf06.gdas.PRECIP_STATS.accumulation.annual.nc"
  f = addfile(diri+"/"+fili, "r")
  cfsr = f->nwetdays
  cfsr_avg = dim_avg_n_Wrap(cfsr(0:29,:,:),0)
  
  ;; MERRA2
  diri = "/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT"
  fili = "MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.nc4"
  f = addfile(diri+"/"+fili, "r")
  merra2 = f->nwetdays
  merra2_avg = dim_avg_n_Wrap(merra2(0:29,:,:),0)

  print ( max(erai_avg({60:90},:)) )
  print ( max(cfsr_avg({60:90},:)) )
  print ( max(merra2_avg({60:90},:)) )

  wks = gsn_open_wks("png","arctic_aug2apr_wetdays")
  gsn_define_colormap(wks, "MPL_YlGnBu")

  plot = new(3, graphic)
  
  res            = True                         ; plot mods desired

  res@gsnDraw             = False           ; don't draw
  res@gsnFrame            = False           ; don't advance frame

  res@gsnPolar   = "NH"                         ; specify the hemisphere
  res@mpMinLatF  = 70                           ; minimum lat to plot

  res@mpFillOn   = False

  res@cnFillOn          = True                  ; color fill
  res@cnLinesOn             = False    ; turn of contour lines
;;  res@cnFillMode            = "CellFill" ;"RasterFill"
  res@cnInfoLabelOn         = False
  res@cnLineLabelsOn        = False

  res@cnLevelSelectionMode = "ManualLevels"
  res@cnMinLevelValF    = 20.
  res@cnMaxLevelValF    = 200.
  res@cnLevelSpacingF   = 20.                    ; interval spacing

  res@lbLabelBarOn         = False

  res@gsnRightString = " "
  res@gsnLeftString  = " "

  plot(0) = gsn_csm_contour_map_polar(wks, erai_avg, res)
  plot(1) = gsn_csm_contour_map_polar(wks, cfsr_avg, res)
  plot(2) = gsn_csm_contour_map_polar(wks, merra2_avg, res)

;;----------------------------------------------------------------------
;; Create panel
;;----------------------------------------------------------------------
  resP = True

  resP@gsnPanelLabelBar    = True                ; add common colorbar
  resP@lbLabelFontHeightF  = 0.015               ; make labels smaller
  resP@lbTitleOn            =  True                ; turn on title
  resP@lbTitleString        = "days"                ; title string
  resP@lbTitlePosition      = "bottom" ;"Right"              ; title position
  resP@lbTitleFontHeightF   = .015                ; make title smaller
  resP@lbTitleDirection     = "Across"
  resP@lbLabelStride        = 4
  resP@lbLabelAutoStride    = True
;  resP@cnLabelBarEndStyle    = "ExcludeOuterBoxes"

  resP@gsnPanelFigureStringsPerimOn = False
  resP@gsnPanelFigureStrings = (/"ERAI","CFSR","MERRA2"/)
  resP@gsnPanelFigureStringsFontHeightF = 0.018
  resP@amOrthogonalPosF = -0.59
  resP@amParallelPosF = -0.5
  resP@gsnPanelFigureStringsBackgroundFillColor = -1
  resP@amJust   = "TopLeft"

  resP@gsnPanelMainFontHeightF = 0.03
  resP@gsnPanelMainPosYF = 0.5
  resP@gsnPanelMainString="August to April Wetdays" 

  gsn_panel(wks,plot,(/1,3/),resP)               ; now draw as one plot
  
end