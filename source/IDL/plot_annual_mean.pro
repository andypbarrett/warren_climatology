OPENR,1,'/disks/arctic5_raid/stroeve/Snow_on_Seaice/comparisons/Aug-Apr_mean_snow_depth'
a=FLTARR(5,35)
READF,1,a
year=REFORM(a(0,*),35)+1
erai=REFORM(a(1,*),35)
merra=REFORM(a(2,*),35)
erai_lo=erai-a(3,*)
erai_hi=erai+a(3,*)
merra_lo=merra-a(4,*)
merra_hi=merra+a(4,*)
CLOSE,1

xtitle='Year'
ytitle='Snow Depth (cm)'
position = [0.125, 0.125, 0.9, 0.925]
w99=FLTARR(35)
w99(*)=21.6
   
; Set up a "window" for the plot. The PostScript output will have
; the same aspect ratio as the graphics window on the display.
; >>>>> Error was here <<<<<<
; >>>>> You had <<<<<
; cgDisplay, 800, 500, Title='Error Estimate Plot',/FREE
; cgDisplay, 800, 500, Title='Polygon Window',/FREE
; 
; dataWin=!D.WINDOW
; polyWin=!D.WINDOW
; >>>>> Should be... <<<<<<<
; >>>>> Formatting on David's page is messed up.
; >>>>> the poly gon window was being written to dataWin and polyWin
cgDisplay, 800, 500, Title='MERRA data',/FREE
MERRAWin=!D.WINDOW
cgDisplay, 800, 500, Title='ERAI data',/FREE
ERAIWin=!D.WINDOW
      
; Draw the line plot with no data
WSET, MERRAWin
cgPlot, year, merra, $
        XTITLE=xtitle, $
        YTITLE=ytitle, $
        POSITION=position, $
        YRANGE=[0, 25], YSTYLE=1, $
        XRANGE=[1980,2016], XSTYLE=1, $
        /NODATA

; Fill in the error estimates.
cgColorFill, [year, Reverse(year), year[0]], $
       [merra_hi, Reverse(merra_lo), merra_hi[0]], $
       Color='grey'
cgPLOTs,year,merra,COLOR='black',THICK=3
cgPlotS, year,erai, Color='dark grey', Thick=3
cgPLOTs,year,w99,THICK=3,COLOR='blue'
;take snapshot of window
background=cgSnapShot()

WSET, ERAIWin
DEVICE,COPY=[0, 0, !D.X_Size, !D.Y_Size, 0, 0, MERRAWin]
cgColorFill, [year, Reverse(year), year[0]], $
       [erai_hi, Reverse(erai_lo), erai_hi[0]], $
             Color='light grey'
;take snapshot of window
foreground=cgSnapshot()

cgDISPLAY, Title='Tranparent plot', /FREE
cgBLENDIMAGE,foreground,background,ALPHA=0.25

END
