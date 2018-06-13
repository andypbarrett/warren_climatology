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
  erai = f->precTot
  erai_avg = dim_avg_n_Wrap(erai(0:29,:,:),0)

  ;; CFSR
  diri = "/disks/arctic5_raid/abarrett/CFSR/PRATE"
  fili = "CFSR.flxf06.gdas.PRECIP_STATS.accumulation.annual.nc"
  f = addfile(diri+"/"+fili, "r")
  cfsr = f->precTot
  cfsr_avg = dim_avg_n_Wrap(cfsr(0:29,:,:),0)
  
  ;; MERRA2
  diri = "/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT"
  fili = "MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.nc4"
  f = addfile(diri+"/"+fili, "r")
  merra2 = f->precTot
  merra2_avg = dim_avg_n_Wrap(merra2(0:29,:,:),0)
  
  ;; MERRA
  diri = "/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT"
  fili = "MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.accumulation.annual.nc4"
  f = addfile(diri+"/"+fili, "r")
  merra = f->precTot
  merra_avg = dim_avg_n_Wrap(merra(0:,:,:),0)
  ;;print (cd_calendar(merra&time, 2) )

  ;; JRA25
  diri = "/disks/arctic5_raid/abarrett/JRA55/PRECTOT"
  fili = "fcst_phy2m.061_tprat.reg_tl319.PRECIP_STATS.accumulation.annual.nc4"
  f = addfile(diri+"/"+fili, "r")
  jra55 = f->precTot
  jra55_avg = dim_avg_n_Wrap(jra55(1:,:,:), 0)
  ;;print (cd_calendar(jra55&time, 2) )

  wks = gsn_open_wks("png","arctic_aug2apr_prectot")
;  gsn_define_colormap(wks, "MPL_YlGnBu")
  gsn_define_colormap(wks, "precip_11lev")

  plot = new(5, graphic)
  
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
  res@cnMinLevelValF    = 50.
  res@cnMaxLevelValF    = 900.
  res@cnLevelSpacingF   = 50.                    ; interval spacing

  res@lbLabelBarOn         = False

  res@gsnRightString = " "
  res@gsnLeftString  = " "

  plot(0) = gsn_csm_contour_map_polar(wks, erai_avg, res)
  plot(1) = gsn_csm_contour_map_polar(wks, cfsr_avg, res)
  plot(2) = gsn_csm_contour_map_polar(wks, merra2_avg, res)
  plot(3) = gsn_csm_contour_map_polar(wks, merra_avg, res)
  plot(4) = gsn_csm_contour_map_polar(wks, jra55_avg, res)

;;----------------------------------------------------------------------
;; Create panel
;;----------------------------------------------------------------------
  resP = True

  resP@gsnPanelLabelBar    = True                ; add common colorbar
  resP@lbLabelFontHeightF  = 0.015               ; make labels smaller
  resP@lbTitleOn            =  True                ; turn on title
  resP@lbTitleString        = "mm"                ; title string
  resP@lbTitlePosition      = "bottom" ;"Right"              ; title position
  resP@lbTitleFontHeightF   = .015                ; make title smaller
  resP@lbTitleDirection     = "Across"
  resP@lbLabelStride        = 4
  resP@lbLabelAutoStride    = True
;  resP@cnLabelBarEndStyle    = "ExcludeOuterBoxes"

  resP@gsnPanelFigureStringsPerimOn = False
  resP@gsnPanelFigureStrings = (/"ERAI","CFSR","MERRA2","MERRA","JRA55"/)
  resP@gsnPanelFigureStringsFontHeightF = 0.018
  resP@amOrthogonalPosF = -0.55
  resP@amParallelPosF = -0.5
  resP@gsnPanelFigureStringsBackgroundFillColor = -1
  resP@amJust   = "TopLeft"

  resP@gsnPanelMainFontHeightF = 0.03
  resP@gsnPanelMainPosYF = 0.9
  resP@gsnPanelMainString="August to April Total Precipitation" 

  resP@pmLabelBarOrthogonalPosF = .001
  
  gsn_panel(wks,plot,(/2,3/),resP)               ; now draw as one plot
  
end
