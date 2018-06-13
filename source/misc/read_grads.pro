;;---------------------------------------------------------------------
;; READ_GRADS reads a grads format file and returns a data structure
;; containing variables and coordinates.
;;
;; USAGE: result = READ_GRADS(gradsfile, CTL_FILE=ctl_file,
;;                            CTL_STRUCT=ctl_struct)
;;
;; Arguments
;; ---------
;; gradsfile - a Grads format file with extention .gdat.  The current 
;;             code is written to read grads files with single variables
;;             and with dimensions x, y, and time.
;;
;;             The default behavior if no CTL_FILE keyword is set is to
;;             look for a grads format ctl file with the same path and 
;;             root name as the grads data file.  For example, if gradsfile
;;             is:
;;
;;                   /some/path/tair_ease_grid.gdat
;; 
;;             then READ_GRADS looks for a ctl file
;;
;;                    /some/path/tair_ease_grid.ctl
;;             
;;
;; Keyword Arguments
;; -----------------
;; CTL_FILE - An alternative ctl file that describes the format and contents
;;            of gradsfile.  This option is useful is there are multiple grads 
;;            data files described by a ctl file or the ctl file has a
;;            different path to the gradsfile
;;
;; CTL_STRUCT - A variable to hold a structure with metadata extracted from
;;              the ctl file.
;;
;; Returns
;; -------
;; READ_GRADS returns an IDL data structure containing coordinate information
;; and data as follows
;;
;; IDL> data = READ_GRADS(dir+'/'+'tair_ease_grid.gdat', CTL_STRUCT=ctl)
;;
;; The contents of the structure can be viewed using the HELP command
;;
;; IDL> HELP, data
;; ** Structure <1a1b828>, 3 tags, length=190274504, data length=190274490, refs=1:
;;    DATAFILE        STRING    '/disks/arctic5_scratch/abarrett/SnowOnSeaIce/tair_ease_grid.gdat'
;;    COORDS          STRUCT    -> <Anonymous> Array[1]
;;    VALUES          FLOAT     Array[361, 361, 365]
;;
;; VALUES is a 2D or 3D array and can be accessed using
;; 
;; IDL> array = data.values
;; IDL> HELP, array
;; ARRAY           FLOAT     = Array[361, 361, 365]
;;
;; The data in VALUES can be subset as you normally do in IDL
;;
;; IDL> PRINT, data_struct.values[175:177,175:177,0]
;;    -0.0475006   -0.0462494   -0.0400047
;;    -0.0487480   -0.0475006   -0.0424995
;;    -0.0537491   -0.0400009   -0.0400047
;;
;; COORDINATES is a structure containing coordinate information as structures
;; for each dimension
;;
;; IDL> HELP, data.coords
;; ** Structure <1114828>, 3 tags, length=5824, data length=5814, refs=2:
;;    X               STRUCT    -> <Anonymous> Array[1]
;;    Y               STRUCT    -> <Anonymous> Array[1]
;;    T               STRUCT    -> <Anonymous> Array[1]
;;
;; Coordinate data for X, Y and T can be accessed by
;;
;; IDL> HELP, data.coords.x
;; ** Structure <1723148>, 2 tags, length=1448, data length=1446, refs=2:
;;    N               INT            361
;;    VALUES          FLOAT     Array[361]
;;
;; Where N is the size of dimension X and VALUES are the coordinate values.  
;;
;; X and Y coordinates have units described in the ctl file: normally either
;; degrees of arc or meters, etc.  T coordinates are in Julian days.  Julian
;; Days can be printed as dates using a formatted print statement or converted
;; to year, month, day, hour, minute values using IDL's CALDAT procedure.
;;
;; An example formatted print statement is
;;
;; IDL> PRINT, data_struct.coords.t.values[0:5], $
;;             FORMAT='(C(CYI4.4,1x,CMOI2.2,1x,CDI2.2,1x,CHI2.2,":",CMI2.2))'
;; 2013 08 01 00:00
;; 2013 08 02 00:00
;; 2013 08 03 00:00
;; 2013 08 04 00:00
;; 2013 08 05 00:00
;; 2013 08 06 00:00
;;
;; The ctl_struct contains metdata from the ctl file and has the follwoing
;; structure
;; 
;; IDL> HELP, ctl       
;; ** Structure <11143a8>, 10 tags, length=256, data length=218, refs=1:
;;    CTL_FILE        STRING    '/disks/arctic5_scratch/abarrett/SnowOnSeaIce/tair_ease_grid.ctl'
;;    DSET            STRING    '/data3/lagrangian/snowmodel/ease_grid/tair_ease_grid.gdat'
;;    TITLE           STRING    'xxxxxxxxxxxxxxxxxxxxxx'
;;    UNDEF           FLOAT          -9999.00
;;    XDEF            STRUCT    -> <Anonymous> Array[1]
;;    YDEF            STRUCT    -> <Anonymous> Array[1]
;;    ZDEF            STRUCT    -> <Anonymous> Array[1]
;;    TDEF            STRUCT    -> <Anonymous> Array[1]
;;    NVARS           INT              1
;;    VARIABLES       STRUCT    -> <Anonymous> Array[1]
;;
;; Where UNDEF is the value of undefined/missing data.
;;
;; XDEF, YDEF, ZDEF and TDEF are structures that contain definitions of x, y,
;; z and t dimensions.  Note that if any dimension has length 1 the VALUES
;; array is reduced.  For example, if the sizes of x, y, x, and t are (361,
;; 361, 1, 1) then the size of VALUES is (361, 361).
;;
;; Dimension metadata can be accessed using 
;;
;; IDL> HELP, ctl.xdef
;; ** Structure <1726878>, 4 tags, length=32, data length=26, refs=2:
;;    NUM             INT            361
;;    MAPPING         STRING    'LINEAR'
;;    START           FLOAT          -4500.00
;;    INCREMENT       FLOAT           25.0000
;;
;; Where NUM is the dimension size, MAPPING is the type of mapping used
;; (LINEAR, LEVELS or GAUS?? - see <http://cola.gmu.edu/grads/gadoc/descriptorfile.html> for details)
;;
;; The VARIABLES structure contains structures of metadata for each variable
;; contained in the grads file.  ***Currently, READ_GRADS only reads data from
;; grads files with one variable***
;;
;; IDL> HELP, ctl.variables
;; ** Structure <1723028>, 1 tags, length=40, data length=36, refs=2:
;;    TAIR            STRUCT    -> <Anonymous> Array[1]
;;
;; Metadata for a variable can be accessed as follows
;;
;; IDL> HELP, ctl.variables.tair
;; ** Structure <1724838>, 4 tags, length=40, data length=36, refs=2:
;;    VARNAME         STRING    'tair'
;;    LEVELS          INT              0
;;    XCODE           INT              0
;;    DESCRIPTION     STRING    'xxxxxxxxxxxxxxx'
;;
;; A description of these fields can be found at <http://cola.gmu.edu/grads/gadoc/descriptorfile.html>
;;
;; 2017-09-06 A.P.Barrett <apbarret@nsidc.org>
;;---------------------------------------------------------------------

;; Checks if string is a valid integer
FUNCTION ISINT, str
  RETURN, STREGEX(str, '^[-+]?[0-9]+$', /BOOLEAN)
END

;; Checks if a string is a valid float
FUNCTION ISFLOAT, str
  RETURN, STREGEX(str, '^[-+]?[0-9]+\.[0-9]*$', /BOOLEAN)
END

;; Parser for x, y or z coordinates
;; Returns structure with coordinate definition
FUNCTION PARSE_XYZCOORD, line

  ;; Parses XDEF, YDEF, and ZDEF tags
  field = STRSPLIT(line, /EXTRACT)
  num = FIX(field[1])
  mapping = field[2]
  
  CASE 1 OF
     STREGEX(mapping, 'LINEAR', /BOOLEAN, /FOLD_CASE): BEGIN
        RETURN, {NUM: num, $
                 MAPPING: mapping, $
                 START: FLOAT(field[3]), $
                 INCREMENT: FLOAT(field[4])}
     END
     STREGEX(mapping, 'LEVELS', /BOOLEAN, /FOLD_CASE): BEGIN
        RETURN, {NUM: num, $
                 MAPPING: mapping, $
                 LEVELS: FLOAT(field[3:N_ELEMENTS(field)-1])}
     END
     STREGEX(mapping, 'GAUS', /BOOLEAN, /FOLD_CASE): BEGIN
        RETURN, {NUM: num, $
                 MAPPING: mapping, $
                 START: FIX(field[3])}
     END
     ELSE: BEGIN
        PRINT, '% PARSE_XYZCOORDS: Unknown MAPPING, expects LINEAR, LEVELS, or GAUS*'
        RETURN, -1
     END
  ENDCASE

END

;; Parses time coordinate metadata in TDEF
;; Returns structure with time coordinate definition
FUNCTION PARSE_TCOORD, line

  field = STRSPLIT(line, /EXTRACT)
  num = FIX(field[1])
  mapping = field[2]

  IF STREGEX(mapping, 'LINEAR', /BOOLEAN, /FOLD_CASE) THEN BEGIN
     RETURN, {NUM: FIX(num), $
              MAPPING: mapping, $
              START: field[3], $
              INCREMENT: field[4]}
  ENDIF ELSE BEGIN
     PRINT, '% PARSE_TCOORD: Unexpected TDEF mapping, expects LINEAR'
     RETURN, -1
  ENDELSE
  
END

;; Parser for all other tags
;; Returns float or integer for UNDEF and VARS fields, otherwise
;; single string.
FUNCTION PARSE_OTHER, line

  field = STRSPLIT(line, /EXTRACT)
  tag = field[0]

  CASE STRUPCASE(tag) OF
     'UNDEF': RETURN, FLOAT(field[1])
     'VARS': RETURN, FIX(field[1])
     ELSE: RETURN, STRJOIN(field[1:N_ELEMENTS(field)-1], ' ')
  ENDCASE

END

;; Parser for variable definition
FUNCTION PARSE_VAR, line

  field = STRSPLIT(line, /EXTRACT)
  varname = field[0]
  levels = FIX(field[1])
  code = FIX(field[2])
  description = STRJOIN(field[3:N_ELEMENTS(field)-1],' ')

  RETURN, {VARNAME: varname, LEVELS: levels, XCODE: code, DESCRIPTION: description}

END

;; Reads the CTL file and returns a data structure
FUNCTION READ_CTL, ctlfile

  OPENR, U, ctlfile, /GET_LUN

  ;; Initialize structure to hold metadata
  struct = CREATE_STRUCT('CTL_FILE', ctlfile)

  line = ''
  WHILE NOT EOF(U) DO BEGIN
    
    READF, U, line
    tag = (STRSPLIT(line, /EXTRACT))[0]

    CASE 1 OF
       STREGEX(tag, '^[XYZ]DEF', /BOOLEAN, /FOLD_CASE): BEGIN
          struct = CREATE_STRUCT(struct, tag, PARSE_XYZCOORD(line))
       END
       STREGEX(tag, '^TDEF', /BOOLEAN, /FOLD_CASE): BEGIN
          struct = CREATE_STRUCT(struct, tag, PARSE_TCOORD(line))
       END
       STREGEX(tag, '^VARS', /BOOLEAN, /FOLD_CASE): BEGIN
          struct = CREATE_STRUCT(struct, 'NVARS', PARSE_OTHER(line))
          ivar = 0
          WHILE NOT EOF(U) DO BEGIN
             READF, U, line
             IF STREGEX(line, '^ENDVARS', /BOOLEAN, /FOLD_CASE) THEN BREAK
             vartag = (STRSPLIT(line,/EXTRACT))[0]
             IF ivar EQ 0 THEN BEGIN
                varstruct = CREATE_STRUCT(vartag, PARSE_VAR(line))
             ENDIF ELSE BEGIN
                varstruct = CREATE_STRUCT(varstruct, vartag, PARSE_VAR(line))
             ENDELSE
          ENDWHILE
          struct = CREATE_STRUCT(struct, 'VARIABLES', varstruct)
       END
       ELSE: BEGIN
          struct = CREATE_STRUCT(struct, tag, PARSE_OTHER(line))
       END
    ENDCASE

  ENDWHILE

  CLOSE, U
  FREE_LUN, U

  RETURN, struct

END

;; Generates coordinates
FUNCTION MAKE_XYZCOORD, struct
  CASE struct.mapping OF
     'LINEAR': RETURN, FINDGEN(struct.num)*struct.increment + struct.start
     'LEVELS': RETURN, struct.levels
     ELSE: BEGIN
        PRINT, '% MAKE_XYZCOORD: Unexpected MAPPING.  Expects LINEAR or LEVELS'
        RETURN, -1
     END
  ENDCASE
END

FUNCTION PARSE_MONTH, mstr

  month = ['-','JAN','FEB','MAR','APR','MAY','JUN', $
           'JUL','AUG','SEP','OCT','NOV','DEC']

  idx = WHERE(STRUPCASE(mstr) EQ month, num)

  IF num GT 0 THEN BEGIN
     RETURN, idx
  ENDIF ELSE BEGIN
     PRINT, '% PARSE_MONTH: Unexpected month - '+mstr
     RETURN, -1
  ENDELSE

END

FUNCTION PARSE_YEAR, ystr
  yy = FIX(ystr)
  CASE 1 OF
     yy GT 100: RETURN, yy
     yy LT 50: RETURN, 2000+yy
     ELSE: RETURN, 1900+yy
  ENDCASE
END

;; Returns start time as a julian day
FUNCTION PARSE_TIME, tstr

  CASE 1 OF
     STREGEX(tstr, '^[a-zA-Z]{3}[0-9]{2,4}', /BOOLEAN): BEGIN
        result = STREGEX(tstr, '([a-zA-Z]{3})([0-9]{2,4})', /SUBEXPR, /EXTRACT)
        RETURN, JULDAY(PARSE_MONTH(result[1]), 1, PARSE_YEAR(result[2]), 0, 0)
     END
     STREGEX(tstr, '^[0-9]{1,2}[a-zA-Z]{3}[0-9]{2,4}', /BOOLEAN): BEGIN
        result = STREGEX(tstr, '([0-9]{1,2})([a-zA-Z]{3})([0-9]{2,4})', /SUBEXPR, /EXTRACT)
        RETURN, JULDAY(PARSE_MONTH(result[2]), FIX(result[1]), PARSE_YEAR(result[3]), 0, 0)
     END
     STREGEX(tstr, '^[0-9]{1,2}Z[0-9]{1,2}[a-zA-Z]{3}[0-9]{2,4}', /BOOLEAN): BEGIN
        result = STREGEX(tstr, '([0-9]{1,2})Z([0-9]{1,2})([a-zA-Z]{3})([0-9]{2,4})', /SUBEXPR, /EXTRACT)
        RETURN, JULDAY(PARSE_MONTH(result[3]), FIX(result[2]), PARSE_YEAR(result[4]), 0, FIX(result[1]))
     END
     STREGEX(tstr, '^[0-9]{1,2}:[0-9]{1,2}Z[0-9]{1,2}[a-zA-Z]{3}[0-9]{2,4}', /BOOLEAN): BEGIN
        result = STREGEX(tstr, '([0-9]{1,2}):([0-9]{1,2})Z([0-9]{1,2})([a-zA-Z]{3})([0-9]{2,4})', $
                         /SUBEXPR, /EXTRACT)
        RETURN, JULDAY(PARSE_MONTH(result[4]), FIX(result[3]), PARSE_YEAR(result[5]), FIX(result[1]), FIX(result[2]))
     END
  ENDCASE

  RETURN, -1
  
END

FUNCTION PARSE_TINC, inc
  parts = STREGEX(inc,'([0-9]{1,2})([a-z]{2})',/SUBEXPR,/EXTRACT)
  CASE parts[2] OF
     'mn': unit = 'Minutes'
     'hr': unit = 'Hours'
     'dy': unit = 'Days'
     'mo': unit = 'Months'
     'yr': unit = 'Years'
     ELSE: BEGIN
        PRINT, '% PARSE_TINC: Unexpected time unit'
        RETURN, -1
     END
  ENDCASE
  RETURN, {MULTI: parts[1], UNIT: unit}
END

;; Generates time coordinates
FUNCTION MAKE_TCOORD, struct
  start = PARSE_TIME(struct.start)
  increment = PARSE_TINC(struct.increment)
  RETURN, TIMEGEN(struct.num, START=start, STEP_SIZE=increment.multi, UNITS=increment.unit)
END

FUNCTION READ_DATA, gradsfile, ctl_struct

  dims = [ctl_struct.xdef.num, ctl_struct.ydef.num, ctl_struct.tdef.num]
  dims = dims[WHERE(dims GT 1)]

  data = MAKE_ARRAY(dims, /FLOAT)
  OPENR, U, gradsfile, /GET_LUN
  READU, U, data
  CLOSE, U
  FREE_LUN, U

  ;; Flip data on y-axis
  data = REVERSE(data,2)

  RETURN, data

END

FUNCTION GEN_COORDS, ctl_struct

  ;; Generate coordinate variables
  IF (ctl_struct.xdef.num GT 1) THEN BEGIN
     IF N_ELEMENTS(coords) GT 0 THEN BEGIN
        coords = CREATE_STRUCT(coords, 'X', {N:ctl_struct.xdef.num, $
                                             VALUES: MAKE_XYZCOORD(ctl_struct.xdef)} )
     ENDIF ELSE BEGIN
        coords = CREATE_STRUCT('X', {N:ctl_struct.xdef.num, $
                                     VALUES: MAKE_XYZCOORD(ctl_struct.xdef)} )
     ENDELSE
  ENDIF

  IF (ctl_struct.ydef.num GT 1) THEN BEGIN
     IF N_ELEMENTS(coords) GT 0 THEN BEGIN
        coords = CREATE_STRUCT(coords, 'Y', {N:ctl_struct.ydef.num, $
                                             VALUES: MAKE_XYZCOORD(ctl_struct.ydef)} )
     ENDIF ELSE BEGIN
        coords = CREATE_STRUCT('Y', {N:ctl_struct.ydef.num, $
                                     VALUES: MAKE_XYZCOORD(ctl_struct.ydef)} )
     ENDELSE
  ENDIF

; Currently doesn't read 4D grids
;  IF (ctl_struct.zdef.num GT 1) THEN BEGIN
;     result = CREATE_STRUCT(result, 'NZ', ctl_struct.zdef.num, 'ZDIM', MAKE_XYZCOORD(ctl_struct.zdef))
;  ENDIF

  IF (ctl_struct.tdef.num GT 1) THEN BEGIN
     IF N_ELEMENTS(coords) GT 0 THEN BEGIN
        coords = CREATE_STRUCT(coords, 'T', {N:ctl_struct.tdef.num, $
                                             VALUES: MAKE_TCOORD(ctl_struct.tdef)} )
     ENDIF ELSE BEGIN
        coords = CREATE_STRUCT('T', {N:ctl_struct.tdef.num, $
                                     VALUES: MAKE_TCOORD(ctl_struct.tdef)} )
     ENDELSE
;     result = CREATE_STRUCT(result, 'NT', ctl_struct.tdef.num, 'TDIM', MAKE_TCOORD(ctl_struct.tdef))
  ENDIF

  RETURN, coords

END

;; Reader for Grads files
FUNCTION READ_GRADS, gradsfile, CTL_FILE=ctl_file, CTL_STRUCT=ctl_struct

  IF N_ELEMENTS(ctl_file) EQ 0 THEN BEGIN
    ctl_file = STR_REPLACE(gradsfile,'.gdat','.ctl')
  ENDIF

  ctl_struct = READ_CTL(ctl_file)

  IF (ctl_struct.nvars GT 1) THEN BEGIN
     PRINT, '% READ_GRADS: Currently only reads files with one variable'
     RETURN, -1
  ENDIF

  IF (ctl_struct.zdef.num GT 1) THEN BEGIN
     PRINT, '% READ_GRADS: Currently only reads files with 3D grids (x,y,t)'
     RETURN, -1
  ENDIF

  ;; Read variables - returns variables, dropping dimensions that are 1
  result = {DATAFILE: gradsfile, $
            COORDS: GEN_COORDS(ctl_struct), $
            VALUES: READ_DATA(gradsfile, ctl_struct)}
  
  RETURN, result

END
  
