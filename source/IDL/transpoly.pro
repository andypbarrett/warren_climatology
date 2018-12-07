
; Create test data
signal = cgDemoData(1) - 15
time = FINDGEN(N_ELEMENTS(signal)) * 6.0 / N_ELEMENTS(signal)

; Create some windows
cgDisplay, Title='Data Window', /FREE
dataWin = !D.Window
cgDisplay, Title='Polygon Window', /FREE
polyWin = !D.Window

; Draw plot in data window
WSET, dataWin
cgPlot, time, signal, COLOR='navy', /NODATA, $
        XTITLE='Time', YTITLE='Signal Strength'
cgPlot, time, signal, THICK=2, COLOR='cornflower blue', /OVERPLOT
cgPlot, time, signal, PSYM=2, COLOR='olive', /OVERPLOT
; Take snapshot
background = cgSnapShot()

WSET, polyWin
DEVICE, COPY=[0, 0, !D.X_SIZE, !D.Y_SIZE, 0, 0, dataWin]
cgColorFill, [0, 6, 6, 0, 0], $
             [-5, -5, 5, 5, -5], /DATA, $
             COLOR='deep pink'
; Take snapshot of this window
foreground = cgSnapshot()

cgDisplay, Title='Transparent Polygon Window', /FREE
cgBlendImage, foreground, background, ALPHA=0.25

END
