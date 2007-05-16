"""'fig' module - object-oriented interface to XFig files.

You can read fig files into a `File` object 'f' with::

  import fig
  f = fig.File(filename) # or pass a file-like object

:author: Hans Meine <hans_meine@gmx.net>"""

_version = "$Id$" \
			  .split(" ")[2:-2]

import sys, re, math, types, os, operator

# object codes
figCustomColor   = 0
figEllipse       = 1
figPolygon       = 2
figSpline        = 3
figText          = 4
figArc           = 5
figCompoundBegin = 6
figCompoundEnd   = -6

# polygon types
ptPolyline    = 1
ptBox         = 2
ptPolygon     = 3
ptArcBox      = 4
ptPictureBBox = 5

# ellipse types
etEllipseRadii    = 1
etEllipseDiameter = 2
etCircleRadius    = 3
etCircleDiameter  = 4

# spline types
stOpenApproximated   = 0
stClosedApproximated = 1
stOpenInterpolated   = 2
stClosedInterpolated = 3
stOpenXSpline        = 4
stClosedXSpline      = 5

# arc types
atPie  = 0
atOpen = 1

# arc directions
adClockwise = 0
adCounterClockwise = 1

# fill styles
fillStyleNone    = -1
fillStyleBlack   = 0
fillStyleSolid   = 20
fillStyleStripes = 42 # obsolete
def fillStyleShaded(percent): # 0 = black .. 100 = fillColor (5% steps)
	return int(percent) / 5
def fillStyleTinted(percent): # 0 = fillColor .. 100 = white (5% steps)
	return 20 + int(percent) / 5
fillStyleLeft30    = 41 # 30 degree left diagonal pattern
fillStyleRight30   = 42 # 30 degree right diagonal pattern
fillStyleCrossed30 = 44 # 30 degree cross-hatched pattern
fillStyleLeft45    = 44 # 45 degree left diagonal pattern
fillStyleRight45   = 45 # 45 degree right diagonal pattern
fillStyleCrossed45 = 46 # 45 degree cross-hatched pattern

# line styles
lineStyleDefault          = -1
lineStyleSolid            = 0
lineStyleDashed           = 1
lineStyleDotted           = 2
lineStyleDashDotted       = 3
lineStyleDashDoubleDotted = 4
lineStyleDashTripleDotted = 5

# cap styles
capStyleButt = 0
capStyleRound = 1
capStyleProjecting = 2

standardColors = [
	# pure colors:
	(0, 0, 0),
	(0, 0, 255),
	(0, 255, 0),
	(0, 255, 255),
	(255, 0, 0),
	(255, 0, 255),
	(255, 255, 0),
	(255, 255, 255),
	# four blues:
	(0, 0, 144),
	(0, 0, 176),
	(0, 0, 208),
	(135, 206, 255),
	# three greens:
	(0, 144, 0),
	(0, 176, 0),
	(0, 208, 0),
	# three cyans:
	(0, 144, 144),
	(0, 176, 176),
	(0, 208, 208),
	# three reds:
	(144, 0, 0),
	(176, 0, 0),
	(208, 0, 0),
	# three magentas:
	(144, 0, 144),
	(176, 0, 176),
	(208, 0, 208),
	# three browns:
	(128, 48, 0),
	(160, 64, 0),
	(192, 96, 0),
	# four pinks:
	(255, 128, 128),
	(255, 160, 160),
	(255, 192, 192),
	(255, 224, 224),
	# gold:
	(255, 215, 0),
	]

# colors
colorDefault   = -1
colorBlack     = 0
colorBlue      = 1
colorGreen     = 2
colorCyan      = 3
colorRed       = 4
colorMagenta   = 5
colorYellow    = 6
colorWhite     = 7
colorBlue4     = 8
colorBlue3     = 9
colorBlue2     = 10
colorLightBlue = 11
colorGreen4    = 12
colorGreen3    = 13
colorGreen2    = 14
colorCyan4     = 15
colorCyan3     = 16
colorCyan2     = 17
colorRed4      = 18
colorRed3      = 19
colorRed2      = 20
colorMagenta4  = 21
colorMagenta3  = 22
colorMagenta2  = 23
colorBrown4    = 24
colorBrown3    = 25
colorBrown2    = 26
colorPink4     = 27
colorPink3     = 28
colorPink2     = 29
colorLightPink = 30
colorGold      = 31
colorCustom0   = 32

# join styles
joinStyleMiter = 0
joinStyleBevel = 1
joinStyleRound = 2

# alignments
alignLeft     = 0
alignCentered = 1
alignRight    = 2

# PS fonts (only valid if font flags == 2): # FIXME: PS prefix?
fontDefault                        = -1
fontTimesRoman                     = 0
fontTimesItalic                    = 1
fontTimesBold                      = 2
fontTimesBoldItalic                = 3
fontAvantGardeBook                 = 4
fontAvantGardeBookOblique          = 5
fontAvantGardeDemi                 = 6
fontAvantGardeDemiOblique          = 7
fontBookmanLight                   = 8
fontBookmanLightItalic             = 9
fontBookmanDemi                    = 10
fontBookmanDemiItalic              = 11
fontCourier                        = 12
fontCourierOblique                 = 13
fontCourierBold                    = 14
fontCourierBoldOblique             = 15
fontHelvetica                      = 16
fontHelveticaOblique               = 17
fontHelveticaBold                  = 18
fontHelveticaBoldOblique           = 19
fontHelveticaNarrow                = 20
fontHelveticaNarrowOblique         = 21
fontHelveticaNarrowBold            = 22
fontHelveticaNarrowBoldOblique     = 23
fontNewCenturySchoolbookRoman      = 24
fontNewCenturySchoolbookItalic     = 25
fontNewCenturySchoolbookBold       = 26
fontNewCenturySchoolbookBoldItalic = 27
fontPalatinoRoman                  = 28
fontPalatinoItalic                 = 29
fontPalatinoBold                   = 30
fontPalatinoBoldItalic             = 31
fontSymbol                         = 32
fontZapfChanceryMediumItalic       = 33
fontZapfDingbats                   = 34

# font flags
ffRigid      = 1
ffSpecial    = 2
ffPostScript = 4
ffHidden     = 8

paperSizes = ["Letter", "Legal", "Ledger", "Tabloid",
			  "A", "B", "C", "D", "E",
			  "A4", "A3", "A2", "A1", "A0", "B5"]

# --------------------------------------------------------------------
#                              helpers
# --------------------------------------------------------------------

def _join(*sequence):
	parts = []
	for item in sequence:
		if type(item) == float:
			parts.append(str(int(round(item))))
		elif type(item) == bool:
			parts.append(str(int(item)))
		else:
			parts.append(str(item))
	return " ".join(parts)

_re_size = re.compile("([0-9]+)x([0-9]+)")
_re_geometry = re.compile("([0-9]+)[:,]([0-9]+)([+-:,])([0-9]+)([x:,])([0-9]+)")

def parseSize(sizeStr):
	"""Convenience function for parsing size strings into tuples:
	
	  >>> fig.parseSize('640x480')
	  (640, 480)
	"""
	ma = _re_size.match(sizeStr)
	if ma:
		w = int(ma.group(1))
		h = int(ma.group(2))
		return (w, h)

def parseGeometry(geometryString):
	"""Convenience function for parsing geometry strings of various
	formats.  Example usage:

	>>> import fig
	>>> fig.parseGeometry("320,240-640,480")
	fig.Rect(320,240,640,480)
	>>> fig.parseGeometry("50,50+50,50")
	fig.Rect(50,50,100,100)
	>>> fig.parseGeometry("40,40,320,240")
	fig.Rect(40,40,320,240)
	>>> r = fig.Rect(0,0,320,240)
	>>> fig.parseGeometry(str(r)) == r
	True
	"""
	ma = _re_geometry.match(geometryString)
	if ma:
		x1 = int(ma.group(1))
		y1 = int(ma.group(2))
		vx2 = int(ma.group(4))
		vy2 = int(ma.group(6))
		if ma.group(3) == "+" or ma.group(5) == "x":
			assert ma.group(3) != "-", "invalid geometry string format 'X,Y-WxH': %s (use either x1,y2-x2,y2 *or* x1,y1+WxH)" % geometryString
			return Rect(x1, y1, x1+vx2, y1+vy2)
		else:
			return Rect(x1, y1, vx2, vy2)

class Rect(object):
	"""This is a simple, half-internal helper class for handling
	Rectangles (e.g. used for bounding boxes).  If you are looking for
	a rectangular figure object, `PolyBox` is your friend.

	A Rect object has the properties `x1`, `x2`, `y1`, `y2` carrying the
	coordinates, and accessor functions `width()`, `height()`,
	`upperLeft()`, `lowerRight()`, `size()`.  (The latter return pairs of
	coordinates.)

	A special facility is the __call__ operator for adding
	points/rects (sort of a UNION operation).

	Finally, it is possible to do::
	
	  x1, y1, x2, y2 = someRect"""
	
	def __init__(self, *args):
		assert len(args) in (0, 4), \
			   "Rect.__init__() expecting zero or four parameters!"
		if len(args) == 4:
			self.x1, self.y1, self.x2, self.y2 = args
			self.empty = False
		else:
			self.empty = True
	
	def __call__(self, other):
		if type(other) == Rect:
			self.__call__((other.x1, other.y1))
			self.__call__((other.x2, other.y2))
		else:
			if self.empty:
				self.x1 = other[0]
				self.x2 = other[0]
				self.y1 = other[1]
				self.y2 = other[1]
				self.empty = False
			else:
				self.x1 = min(self.x1, other[0])
				self.y1 = min(self.y1, other[1])
				self.x2 = max(self.x2, other[0])
				self.y2 = max(self.y2, other[1])
	
	def width(self):
		return self.x2 - self.x1
	
	def height(self):
		return self.y2 - self.y1

	def upperLeft(self):
		return self.x1, self.y1
	
	def lowerRight(self):
		return self.x2, self.y2
	
	def center(self):
		return (self.x2 + self.x1) / 2, (self.y2 + self.y1) / 2
	
	def size(self):
		return self.width(), self.height()
	
	def __repr__(self):
		return "fig.Rect(%d,%d,%d,%d)" % (self.x1, self.y1, self.x2, self.y2)
	
	def __str__(self):
		return "%d,%d-%d,%d" % (self.x1, self.y1, self.x2, self.y2)

	def __eq__(self, other):
		if type(other) != Rect:
			return False
		return str(self) == str(other)
	
	def __ne__(self, other):
		if type(other) == Rect:
			return False
		return str(self) != str(other)
	
	def __iter__(self):
		"""Make Rect objects assignable like::
		x1, y1, x2, y2 = someRect"""
		yield self.x1
		yield self.y1
		yield self.x2
		yield self.y2

# --------------------------------------------------------------------
# 							custom colors
# --------------------------------------------------------------------

class CustomColor(object):
	def __init__(self, index, hexCode):
		assert len(hexCode) == 7 and hexCode.startswith("#"), \
			   "invalid hexCode given to CustomColor(), should look like '#fe0d00'"
		self.index = index
		self.hexCode = hexCode
		#sys.stderr.write("CustomColor(%d, '%s') -> %s" % (index, hexCode, repr(self)))

	def __repr__(self):
		return _join(figCustomColor, self.index, self.hexCode) + "\n"

	def __str__(self):
		return str(self.index)

	def __int__(self):
		return self.index

	def __cmp__(self, other):
		if other == None:
			return 1
		if isinstance(other, CustomColor):
			return cmp(self.index, other.index)
		if isinstance(other, str):
			return cmp(self.hexCode, other)
		return cmp(self.index, other)

	def __sub__(self, other):
		"""Returns RGB vector difference as (dr,dg,db) tuple."""
		return map(operator.sub, self, other)

	def __getitem__(self, index):
		if index > 2:
			raise IndexError("CustomColor.__getitem__: Only three components (r,g,b)!")
		return int(self.hexCode[2*index+1:2*index+3], 16)

	def __len__(self):
		return 3
	
	def rgb(self):
		return (self[0], self[1], self[2])

	def setRGB(self, r, g, b):
		self.hexCode = "#%02x%02x%02x" % (r, g, b)

# --------------------------------------------------------------------
# 				Object: base class for all fig objects
# --------------------------------------------------------------------

class Object(object):
	"""Base class of all fig objects.  Handles common properties like
	
	- lineStyle (see `lineStyleXXX` constants)
	- lineWidth (1/80th inch)
	- styleValue (dash length / dot gap ratio), in 1/80th inches
	- penColor, fillColor (see `colorXXX` constants)
	- fillStyle (see `fillStyleXXX` constants)
	- depth (0-999)
	- joinStyle (see `joinStyleXXX` constants)
	- capStyle (see `capStyleXXX` constants)
	- forwardArrow/backwardArrow (`Arrow` objects)"""

	__slots__ = ("lineStyle", "lineWidth", "penColor", "fillColor", "depth",
				 "penStyle", "fillStyle", "styleValue", "joinStyle", "capStyle",
				 "forwardArrow", "backwardArrow")

	def __init__(self):
		self.lineStyle = lineStyleDefault
# Line thicknesses are given in 1/80 inch (0.3175mm) or 1 screen pixel.
# When exporting to EPS, PostScript or any bitmap format (e.g. GIF),  the
# line thickness is reduced to 1/160 inch (0.159mm) to "lighten" the look.
		self.lineWidth = 1
		self.penColor = colorDefault
		self.fillColor = colorDefault
		self.depth = 50
		self.penStyle = 0 # not used
		self.fillStyle = fillStyleNone
		self.styleValue = 3.0
		self.joinStyle = 0
		self.capStyle = 0
		self.forwardArrow = None
		self.backwardArrow = None

class Arrow(object):
	"""Arrow objects store arrow parameters of other objects.
	Instances of this class are usually assigned to the
	`forwardArrow`/`backwardArrow` properties of `fig.Object`.

	FIXME: This class is still a stub that stores all parameters in a
	single attribute 'params'."""
	
	def __init__(self, params):
		self.params = params

	def __str__(self):
		return _join(*self.params) + "\n"

# --------------------------------------------------------------------
#                                arcs
# --------------------------------------------------------------------

class ArcBase(Object):
	"""Base class of Arc-like objects (`PieArc`, `OpenArc`)."""

	__slots__ = ("points", "direction", "center", "_pointCount")
	
	def __init__(self):
		Object.__init__(self)
		self.points = []
		self.center = None
		self.direction = adClockwise

	def changeType(self, arcType):
		"Change type of this Arc. arcType may be one of atPie or atOpen"
		if arcType == atPie:
			self.__class__ = PieArc
		else:
			self.__class__ = OpenArc

	def __str__(self):
		hasForwardArrow = (self.forwardArrow != None and 1 or 0)
		hasBackwardArrow = (self.backwardArrow != None and 1 or 0)
		
		result = _join(figArc, self.arcType(),
					   self.lineStyle, self.lineWidth,
					   self.penColor, self.fillColor,
					   self.depth, self.penStyle,
					   self.fillStyle, str(self.styleValue),
					   self.capStyle, self.direction,
					   hasForwardArrow, hasBackwardArrow,
					   str(self.center[0]), str(self.center[1]),
					   self.points[0][0], self.points[0][1],
					   self.points[1][0], self.points[1][1],
					   self.points[2][0], self.points[2][1]) + "\n"

		if hasForwardArrow:
			result += "\t" + str(self.forwardArrow)
		if hasBackwardArrow:
			result += "\t" + str(self.backwardArrow)
		return result

	def bounds(self):
		result = Rect()
		for point in self.points:
			result(point)
		return result

	def _readSub(self, params):
		if self.forwardArrow == True:
			self.forwardArrow = Arrow(params)
			return self.backwardArrow == True

		if self.backwardArrow == True:
			self.backwardArrow = Arrow(params)
			return False

		sys.stderr.write("Unhandled subline while loading arc object!\n")
		return False

class PieArc(ArcBase):
	"""Represents a closed arc object."""
	
	__slots__ = ()

	def arcType(self):
		"Return type of this Arc (atPie), see `changeType`."
		return atPie

class OpenArc(ArcBase):
	"""Represents an open arc object."""

	__slots__ = ()

	def arcType(self):
		"Return type of this Arc (atOpen), see `changeType`."
		return atOpen

def _readArcBase(params):
	result = ArcBase()
	result.changeType(int(params[0]))
	result.lineStyle = int(params[1])
	result.lineWidth = int(params[2])
	result.penColor = int(params[3])
	result.fillColor = int(params[4])
	result.depth = int(params[5])
	result.penStyle = int(params[6])
	result.fillStyle = int(params[7])
	result.styleValue = float(params[8])
	result.capStyle = int(params[9])
	result.direction = int(params[10])
	subLines = 0
	if int(params[11]):
		result.forwardArrow = True
		subLines += 1
	if int(params[12]):
		result.backwardArrow = True
		subLines += 1
	result.center = (float(params[13]), float(params[14]))
	result.points = [(int(params[15]), int(params[16])),
					 (int(params[17]), int(params[18])),
					 (int(params[19]), int(params[20]))]
	return result, subLines

# --------------------------------------------------------------------
#                              ellipses
# --------------------------------------------------------------------

class EllipseBase(Object):
	"""Base class of Ellipse-like objects (`Ellipse`, `Circle`)."""
	
	__slots__ = ("angle", "center", "radius", "start", "end")

	def __init__(self):
		Object.__init__(self)
		self.angle = 0.0
		self.center = (0, 0)
		self.radius = (0, 0)
		self.start = (0, 0)
		self.end = (0, 0)

	def changeType(self, ellipseType):
		"""Change type of this Ellipse object.  `ellipseType` may be one
		of the `etXXX` constants:

		- etEllipseRadii
		- etEllipseDiameter
		- etCircleRadius
		- etCircleDiameter

		This method may change the type of this object to another
		`EllipseBase`-derived class."""

		if ellipseType in (etEllipseRadii, etEllipseDiameter):
			self.__class__ = Ellipse
		elif ellipseType in (etCircleRadius, etCircleDiameter):
			self.__class__ = Circle
		else:
			raise ValueError("Unknown ellipseType %d!" % ellipseType)

	def __str__(self):
		return _join(figEllipse, self.ellipseType(),
					 self.lineStyle, self.lineWidth,
					 self.penColor, self.fillColor,
					 self.depth, self.penStyle,
					 self.fillStyle, str(self.styleValue),
					 1, # "1" is self.direction
					 str(self.angle),
					 self.center[0], self.center[1],
					 self.radius[0], self.radius[1],
					 self.start[0], self.start[1],
					 self.end[0], self.end[1]) + "\n"

	def bounds(self):
		result = Rect()
		result(((self.center[0] - self.radius[0]),
				(self.center[1] - self.radius[1])))
		result(((self.center[0] + self.radius[0]),
				(self.center[1] + self.radius[1])))
		return result

	def setRadius(self, radius):
		"""Change radius.  `radius` may be either a tuple of x/y
		radii, or a single radius, convertible to float(s)."""
		if not isinstance(radius, tuple):
			assert float(radius) != None, "radius must be either a tuple of x/y radii, or a single radius, convertible to float(s)"
			self.radius = (radius, radius)
		else:
			assert len(radius) == 2 and float(radius[0]) != None and float(radius[1]) != None, "radius must be either a tuple of x/y radii, or a single radius, convertible to float(s)"
			self.radius = radius
		# FIXME: depend on ellipseType (currently, ellipseType may change)
		self.start = self.center
		self.end = (self.center[0] + self.radius[0],
					self.center[1] + self.radius[1])

	def setCenterRadius(self, center, radius):
		"""Set center and radius, see `setRadius`."""
		self.center = center
		self.setRadius(radius)

def _readEllipseBase(params):
	result = EllipseBase()
	result.changeType(int(params[0]))
	result.lineStyle = int(params[1])
	result.lineWidth = int(params[2])
	result.penColor = int(params[3])
	result.fillColor = int(params[4])
	result.depth = int(params[5])
	result.penStyle = int(params[6])
	result.fillStyle = int(params[7])
	result.styleValue = float(params[8])
	result.angle = float(params[10])
	result.center = ((int(params[11]), int(params[12])))
	result.radius = ((int(params[13]), int(params[14])))
	result.start = ((int(params[15]), int(params[16])))
	result.end = ((int(params[17]), int(params[18])))
	return result, 0

class Ellipse(EllipseBase):
	"""Represents an ellipse object.  Ellipse objects have an
	attribute `radius` that is a tuple of two radii in x- and
	y-direction."""
	
	__slots__ = ()

	def __init__(self, center = None, radii = None,
				 start = None, end = None):
		EllipseBase.__init__(self)
		if center != None and radii != None:
			self.setCenterRadius(center, radii)
		else:
			self.setStartEnd(start, end)

	def ellipseType(self):
		"""Returns type of this ellipse (one of etEllipseRadii,
		etEllipseDiameter for `Ellipse` objects), see `changeType`."""

		if self.center == self.start:
			return etEllipseRadii
		else:
			return etEllipseDiameter

	def setStartEnd(self, start, end):
		self.start = start
		self.end = end
		# FIXME: depend on ellipseType
		self.center = ((start[0] + end[0])/2,
					   (start[1] + end[1])/2)
		self.radius = ((end[0] - self.center[0]),
					   (end[1] - self.center[1]))

class Circle(EllipseBase):
	"""Represents a circle object.  Circle objects have an
	attribute `radius` that is a single float."""
	
	__slots__ = ()

	def __init__(self, center = None, radius = None,
				 start = None, end = None):
		EllipseBase.__init__(self)
		if center != None and radius != None:
			self.setCenterRadius(center, (radius, radius))
		else:
			self.setStartEnd(start, end)

	def ellipseType(self):
		"""Returns type of this ellipse (one of etCircleRadius,
		etCircleDiameter for `Circle` objects), see `changeType`."""

		if self.center == self.start:
			return etCircleRadius
		else:
			return etCircleDiameter

	def setStartEnd(self, start, end):
		self.start = start
		self.end = end
		# FIXME: depend on ellipseType
		self.center = ((start[0] + end[0])/2,
					   (start[1] + end[1])/2)
		radius = int(round(math.hypot(end[0] - self.center[0],
									  end[1] - self.center[1])))
		self.radius = (radius, radius)

	def __str__(self):
		assert self.radius[0] == self.radius[1], \
			   "invalid circle (radii %d != %d)" % self.radius
		return EllipseBase.__str__(self)

# --------------------------------------------------------------------
#                             polylines
# --------------------------------------------------------------------

class PolylineBase(Object):
	"""Base class of Polygon-like objects (`Polygon`,
	`Polyline`, `PictureBBox`)."""

	__slots__ = ("points", "pictureFilename", "flipped", "radius", "_pointCount")
	
	def __init__(self):
		Object.__init__(self)
		self.points = []
		self.pictureFilename = None
		self.flipped = False
		self.radius = -1

	def changeType(self, polylineType, retainPoints = False):
		"""Change type of this Polyline object.  `polylineType` may be one
		of the `ptXXX` constants:

		- ptPolyline
		- ptBox
		- ptPolygon
		- ptArcBox
		- ptPictureBBox

		This method may change the type of this object to another
		`PolylineBase`-derived class.

		If `retainPoints` is not set to True, this function will
		add/remove the last point such that closed polygons do not
		have the first point repeated at the end."""

		wasClosed = None
		if type(self) != PolylineBase:
			wasClosed = self.closed()
		if polylineType == ptPolyline:
			self.__class__ = Polyline
		if polylineType == ptBox:
			self.__class__ = PolyBox
		if polylineType == ptPolygon:
			self.__class__ = Polygon
		if polylineType == ptArcBox:
			self.__class__ = ArcBox
		if polylineType == ptPictureBBox:
			self.__class__ = PictureBBox
		if retainPoints or wasClosed == None:
			return
		if wasClosed == self.closed() or len(self.points) < 2:
			return
		if not wasClosed:
			if self.points[-1] == self.points[0]:
				del self.points[-1]
		else:
			self.points.append(self.points[0])

	def __str__(self):
		pointCount = len(self.points)
		if self.closed():
			pointCount += 1
		hasForwardArrow = (self.forwardArrow != None and 1 or 0)
		hasBackwardArrow = (self.backwardArrow != None and 1 or 0)
		
		result = _join(figPolygon, self.polylineType(),
					   self.lineStyle, self.lineWidth,
					   self.penColor, self.fillColor,
					   self.depth, self.penStyle,
					   self.fillStyle, str(self.styleValue),
					   self.joinStyle, self.capStyle, self.radius,
					   hasForwardArrow, hasBackwardArrow,
					   pointCount) + "\n"

		if hasForwardArrow:
			result += "\t" + str(self.forwardArrow)
		if hasBackwardArrow:
			result += "\t" + str(self.backwardArrow)
		if type(self) == PictureBBox:
			result += "\t" + _join(self.flipped, self.pictureFilename) + "\n"
		i = self._savePointIter()
		for linePoints in map(None, *(i, )*12):
			result += "\t" + _join(*[p for p in linePoints if p != None]) + "\n"
		return result

	def _savePointIter(self):
		for p in self.points:
			yield p[0]
			yield p[1]
		if self.closed():
			yield self.points[0][0]
			yield self.points[0][1]

	def bounds(self):
		result = Rect()
		for point in self.points:
			result(point)
		return result

	def _readSub(self, params):
		if self.forwardArrow == True:
			self.forwardArrow = Arrow(params)
			return True

		if self.backwardArrow == True:
			self.backwardArrow = Arrow(params)
			return True

		if type(self) == PictureBBox and self.pictureFilename == None:
			self.flipped = int(params[0])
			self.pictureFilename = params[1]
			return True

		pointCount = len(params) / 2
		for pointIndex in range(pointCount):
			self.points.append((int(params[pointIndex * 2]),
								int(params[pointIndex * 2 + 1])))

		expectedPoints = (self._pointCount + (self.closed() and 1 or 0))
		moreToCome = len(self.points) < expectedPoints
		if len(self.points) > self._pointCount:
			if len(self.points) > expectedPoints:
				sys.stderr.write("WARNING: read too many points?!\n")
			del self.points[self._pointCount:]

		return moreToCome

def _readPolylineBase(params):
	result = PolylineBase()
	# retainPoints is not actually necessary for PolylineBase objects:
	result.changeType(int(params[0]), retainPoints = True)
	result.lineStyle = int(params[1])
	result.lineWidth = int(params[2])
	result.penColor = int(params[3])
	result.fillColor = int(params[4])
	result.depth = int(params[5])
	result.penStyle = int(params[6])
	result.fillStyle = int(params[7])
	result.styleValue = float(params[8])
	result.joinStyle = int(params[9])
	result.capStyle = int(params[10])
	result.radius = int(params[11])
	subLines = 0
	if int(params[12]):
		result.forwardArrow = True
		subLines += 1
	if int(params[13]):
		result.backwardArrow = True
		subLines += 1
	result._pointCount = int(params[14])
	subLines += (result._pointCount+5)/6 # sublines to read for the points
	if result.closed():
		result._pointCount -= 1
	if type(result) == PictureBBox:
		subLines += 1
	return result, subLines

class PolyBox(PolylineBase):
	"""Represents a rectangular closed box object."""
	
	__slots__ = ()

	def __init__(self, x1, y1, x2, y2):
		PolylineBase.__init__(self)
		self.points.append((x1, y1))
		self.points.append((x2, y1))
		self.points.append((x2, y2))
		self.points.append((x1, y2))

	def polylineType(self):
		"""Returns type of this polygon (ptBox for all `PolyBox` objects),
		see `changeType`."""

		return ptBox

	def closed(self):
		"""Returns whether this polygon is closed (True for all
		`PolyBox` objects.)"""
		return True

	def center(self):
		"""Returns (x, y) coordinate tuple of the midpoint of this box."""
		return ((self.points[0][0] + self.points[2][0])/2,
				(self.points[0][1] + self.points[2][1])/2)

	def width(self):
		"""Returns width of this box."""
		return abs(self.points[2][0] - self.points[0][0])

	def height(self):
		"""Returns height of this box."""
		return abs(self.points[2][1] - self.points[0][1])

class ArcBox(PolyBox):
	"""Represents a rectangular box with rounded corners."""
	
	__slots__ = ()

	def polylineType(self):
		"""Returns type of this polygon (ptArcBox for all `ArcBox` objects),
		see `changeType`."""

		return ptArcBox

class Polygon(PolylineBase):
	"""Represents a closed polygon object."""
	
	__slots__ = ()

	def __init__(self, points, closed = True):
		PolylineBase.__init__(self)
		self.points = points
		if not closed:
			self.changeType(ptPolyline, retainPoints = True)

	def polylineType(self):
		"""Returns type of this polygon (ptPolygon for all `Polygon` objects),
		see `changeType`."""

		return ptPolygon

	def closed(self):
		"""Returns whether this polygon is closed (True for all
		`Polygon` objects.)"""
		return True

class Polyline(PolylineBase):
	"""Represents an open polygon object."""
	
	__slots__ = ()

	def __init__(self, *points):
		PolylineBase.__init__(self)
		self.points = points

	def polylineType(self):
		"""Returns type of this polygon (ptPolyline for all `Polyline`
		objects), see `changeType`."""

		return ptPolyline

	def closed(self):
		"""Returns whether this polygon is closed (False for all
		`Polygon` objects.)"""

		return False

class PictureBBox(PolyBox):
	"""Represents a picture embedded in an XFig file.  The filename is
	stored in the `pictureFilename` attribute."""
	
	__slots__ = ()

	def __init__(self, x1, y1, x2, y2, filename, flipped = False):
		PolyBox.__init__(self, x1, y1, x2, y2)
		self.pictureFilename = filename
		self.flipped = flipped

	def polylineType(self):
		"""Returns type of this polygon (ptPictureBBox for all
		`PictureBBox` objects), see `changeType`."""

		return ptPictureBBox

	def closed(self):
		"""Returns whether this polygon is closed (True for all
		`PictureBBox` objects.)"""
		return True

# --------------------------------------------------------------------
#                              splines
# --------------------------------------------------------------------

class SplineBase(Object):
	"""Base class of Spline objects (`ApproximatedSpline`,
	`InterpolatedSpline`, `XSpline`)."""
	
	__slots__ = ("points", "shapeFactors", "_closed", "_pointCount")

	def __init__(self, points = None, shapeFactors = None):
		Object.__init__(self)
		self.points = points or []
		self.shapeFactors = shapeFactors or []
		self._closed = None

	def closed(self):
		"""Returns whether this spline curve is closed."""
		assert self._closed != None, "SplineBase.closed(): _closed not initialized!"
		return self._closed

	def changeType(self, splineType):
		"""Change type of this Spline object.  `splineType` may be one
		of the `stXXX` constants:

		- stOpenApproximated
		- stClosedApproximated
		- stOpenInterpolated
		- stClosedInterpolated
		- stOpenXSpline
		- stClosedXSpline

		This method may change the type of this object to another
		`SplineBase`-derived class."""

		if splineType == stOpenApproximated:
			self.__class__ = ApproximatedSpline
			self._closed = False
		elif splineType == stClosedApproximated:
			self.__class__ = ApproximatedSpline
			self._closed = True
		elif splineType == stOpenInterpolated:
			self.__class__ = InterpolatedSpline
			self._closed = False
		elif splineType == stClosedInterpolated:
			self.__class__ = InterpolatedSpline
			self._closed = True
		elif splineType == stOpenXSpline:
			self.__class__ = XSpline
			self._closed = False
		elif splineType == stClosedXSpline:
			self.__class__ = XSpline
			self._closed = True

	def __str__(self):
		pointCount = len(self.points)

		hasForwardArrow = (self.forwardArrow != None and 1 or 0)
		hasBackwardArrow = (self.backwardArrow != None and 1 or 0)

		result = _join(figSpline, self.splineType(),
					   self.lineStyle, self.lineWidth,
					   self.penColor, self.fillColor,
					   self.depth, self.penStyle,
					   self.fillStyle, str(self.styleValue), self.capStyle,
					   hasForwardArrow, hasBackwardArrow,
					   pointCount) + "\n"

		if hasForwardArrow:
			result += "\t" + str(self.forwardArrow)
		if hasBackwardArrow:
			result += "\t" + str(self.backwardArrow)
		i = self._savePointIter()
		for linePoints in map(None, *(i, )*12):
			result += "\t" + _join(*[p for p in linePoints if p != None]) + "\n"
		i = iter(self.shapeFactors)
		for lineSF in map(None, *(i, )*8):
			result += "\t" + _join(*[str(sf) for sf in lineSF if sf != None]) + "\n"
		return result

	def _savePointIter(self):
		for p in self.points:
			yield p[0]
			yield p[1]

	def bounds(self):
		"""Returns the bounds of this object.  This is not accurate at
		all, since it simply returns the bounding box of the support
		points, but the curve may well run outside of that box."""
		# FIXME
		result = Rect()
		for point in self.points:
			result(point)
		return result

	def _readSub(self, params):
		if self.forwardArrow == True:
			self.forwardArrow = Arrow(params)
			return True

		if self.backwardArrow == True:
			self.backwardArrow = Arrow(params)
			return True

		expectedPoints = self._pointCount

		if len(self.points) < expectedPoints:
			pointCount = len(params) / 2
			for pointIndex in range(pointCount):
				self.points.append((int(params[pointIndex * 2]),
									int(params[pointIndex * 2 + 1])))
			if len(self.points) > expectedPoints:
				sys.stderr.write("WARNING: read too many points?!\n")
				del self.points[expectedPoints:]
			return True

		if len(self.shapeFactors) < expectedPoints:
			sfCount = len(params)
			for sfIndex in range(sfCount):
				self.shapeFactors.append(float(params[sfIndex]))
			moreToCome = len(self.shapeFactors) < expectedPoints
			if len(self.shapeFactors) > expectedPoints:
				sys.stderr.write("WARNING: read too many shapeFactors?!\n")
				del self.shapeFactors[expectedPoints:]
			if moreToCome:
				return True

		return False

class ApproximatedSpline(SplineBase):
	"""Represents an open or closed approximated spline object."""
	
	__slots__ = ()

	def splineType(self):
		return self._closed and stClosedApproximated or stOpenApproximated

class InterpolatedSpline(SplineBase):
	"""Represents an open or closed interpolated spline object."""
	
	__slots__ = ()

	def splineType(self):
		return self._closed and stClosedInterpolated or stOpenInterpolated

class XSpline(SplineBase):
	"""Represents an open or closed 'x-spline' object."""
	
	__slots__ = ()

	def splineType(self):
		return self._closed and stClosedXSpline or stOpenXSpline

def _readSplineBase(params):
	result = SplineBase()
	result.changeType(int(params[0]))
	result.lineStyle = int(params[1])
	result.lineWidth = int(params[2])
	result.penColor = int(params[3])
	result.fillColor = int(params[4])
	result.depth = int(params[5])
	result.penStyle = int(params[6])
	result.fillStyle = int(params[7])
	result.styleValue = float(params[8])
	result.capStyle = int(params[9])
	subLines = 0
	if int(params[10]):
		result.forwardArrow = True
		subLines += 1
	if int(params[11]):
		result.backwardArrow = True
		subLines += 1
	result._pointCount = int(params[12])
	subLines += (result._pointCount+5)/6 # sublines to read for the points
	return result, subLines

# --------------------------------------------------------------------
#                            text objects
# --------------------------------------------------------------------

class Text(Object):
	"""Represents a text object.  Text instances have a number of
	extra attributes:

	- text (the string)
	- x, y (position)
	- alignment (cf. `alignXXX` constants)
	- font (cf. fontXXX constants)
	- fontSize (defailt: 12)
	- fontAngle (default: 0.0)
	- fontFlags (cf. `ffXXX` constants, default: ffPostScript)
	- length, height (dummy values, no guarantee about correctness)
	"""

	__slots__ = ("text", "x", "y", "alignment",
				 "font", "fontSize", "fontAngle", "fontFlags",
				 "length", "height")

	def __init__(self, x, y, text, alignment = alignLeft):
		Object.__init__(self)
		self.text = text
		self.font = fontDefault
		self.fontSize = 12
		self.fontAngle = 0.0
		self.fontFlags = ffPostScript
		self.height = 136
		self.length = 100 # dummy value
		self.x = x
		self.y = y
		self.alignment = alignment

	def bounds(self):
		result = Rect()
		if self.alignment == alignLeft:
			result((self.x,               self.y - self.height))
			result((self.x + self.length, self.y))
		elif self.alignment == alignCentered:
			result((self.x - self.length/2, self.y - self.height))
			result((self.x + self.length/2, self.y))
		elif self.alignment == alignRight:
			result((self.x,               self.y - self.height))
			result((self.x + self.length, self.y))
		return result

	def __str__(self):
		result = _join(figText, self.alignment,
					   self.penColor, self.depth, self.penStyle,
					   self.font, self.fontSize, str(self.fontAngle), self.fontFlags,
					   self.height, self.length, self.x, self.y,
					   self.text + "\\001") + "\n"

		return result

def _readText(params, text):
	result = Text(int(params[10]), int(params[11]),
				  text, int(params[0]))
	result.penColor = int(params[1])
	result.depth = int(params[2])
	result.penStyle = int(params[3])
	result.font = int(params[4])
	result.fontSize = float(params[5])
	result.fontAngle = float(params[6])
	result.fontFlags = int(params[7])
	result.height = float(params[8])
	result.length = float(params[9])
	return result, 0

# --------------------------------------------------------------------
#              Container and ObjectProxy utility classes
# --------------------------------------------------------------------

class _AllObjectIter(object):
	"helper class, see `Container.allObjects`"
	
	def __init__(self, container, includeCompounds):
		self.file = file
		self.iters = [iter(container)]
		self.includeCompounds = includeCompounds

	def __iter__(self):
		return self

	def next(self):
		if not self.iters:
			raise StopIteration
		try:
			next = self.iters[-1].next()
			if type(next) == Compound:
				self.iters.append(iter(next))
				if self.includeCompounds:
					return next
			else:
				return next
		except StopIteration:
			del self.iters[-1]
		return self.next()

class Container(list):
	"""Container for fig objects, derived from the standard python
	list.  This is the common superclass of `File` (for the whole
	document), `Compound`, and `ObjectProxy` (for search results, see
	`findObjects()` or `layer()`."""
	
	def allObjects(self, includeCompounds = False):
		"""container.allObjects(includeCompounds = False) -> iterator

		Returns an iterator iterating over all objects in this
		container, recursively entering compound objects.  You can use
		the optional parameter includeCompounds (default: False) to
		get the compound objects themselves returned, too."""
		
		return _AllObjectIter(self, includeCompounds)

	def findObjects(self, **kwargs):
		"""Returns a list of objects which have attribute/value pairs
		matching the given keyword parameters.  The key "type" is
		treated special, see these useful examples::

		  figFile.findObjects(depth = 40)
		  figFile.findObjects(type = fig.Polygon)
		  # all conditions must be fulfilled:
		  figFile.findObjects(lineWidth = 10, depth = 100)
		  # for disjunctive conditions, use list concatenation:
		  figFile.findObjects(depth = 10) + figFile.findObjects(depth = 20)

		The returned object is actually an `ObjectProxy`, which is a
		special `Container` (which is a special python list) and allows
		to quickly change properties on all contained objects.  See
		the `Container` and `ObjectProxy` classes."""

		result = ObjectProxy()
		result.__dict__["parent"] = self
		for o in self.allObjects("type" in kwargs and kwargs["type"] == Compound):
			match = True
			for key in kwargs:
				if key == "type":
					if not isinstance(o, kwargs[key]):
						match = False
						continue
				elif getattr(o, key, "attribNotPresent") != kwargs[key]:
					match = False
					continue
			if match:
				result.append(o)
		return result

	def layer(self, layer):
		"""container.layer(layer) -> `ObjectProxy`

		Returns an `ObjectProxy` for all objects within this container
		that have the given depth; convenience shortcut for
		``findObjects(depth = layer)``."""
		
		return self.findObjects(depth = layer)

	def layers(self):
		"""container.layers() -> list

		Returns the list of all integer depths that are assigned to at
		least one object within this container."""
		
		result = dict.fromkeys([ob.depth for ob in self.allObjects()]).keys()
		result.sort()
		return result

	def remove(self, obj):
		"""container.remove(obj)

		Removes the given object from this `Container`.  Also works
		recursively for objects within `Compound` objects within this
		`Container`.  Raises a ValueError if `obj` is not
		contained."""
		
		try:
			list.remove(self, obj)
		except ValueError:
			for o in self:
				if type(o) == Compound:
					try:
						o.remove(obj)
						return
					except ValueError:
						pass
			raise ValueError("remove(): Given object not found in Container.")

class ObjectProxy(Container):
	"""An ObjectProxy is a special `Container` that is used for search
	results (see `Container.findObjects`) which offers two additional
	features:

	remove():
	  Use like ``foo.findObjects(type = fig.Polyline).remove()``

	  Removes all objects within this object proxy from the parent
	  container (the one `findObjects` was called on).

	setting attributes:
	  ``foo.findObjects(type = fig.Polyline).lineWidth = 4``

	  Setting an attribute is promoted to all contained objects which
	  have that attribute.  (E.g. setting fontAngle will affect only
	  Text objects.)"""
	
	def __setattr__(self, key, value):
		for ob in self:
			if hasattr(ob, key):
				setattr(ob, key, value)

	def __getattr__(self, key):
		found = False
		for ob in self:
			if hasattr(ob, key):
				if found:
					if getattr(ob, key) != result:
						return None
				else:
					result = getattr(ob, key)
					found = True
		if not found:
			raise AttributeError("No Object within ObjectProxy has a '%s' attribute!" % key)
		return result

	def remove(self, *args):
		"""When no arguments are given, remove all objects from parent
		container.  Else, remove given object from this container."""
		
		if not args:
			assert self.parent, "ObjectProxy.remove() needs access to the parent"
			for ob in self:
				self.parent.remove(ob)
		else:
			Container.remove(self, *args)

	def __add__(self, other):
		if isinstance(other, list):
			return ObjectProxy(list.__add__(self, other))

# --------------------------------------------------------------------
#                             compounds
# --------------------------------------------------------------------

class Compound(Container):
	"""Represents a group of XFig objects."""
	
	def __init__(self, parent = None):
		self._bounds = Rect()
		if parent != None:
			parent.append(self)

	def bounds(self):
		return self._bounds

	def append(self, object):
		super(Compound, self).append(object)
		self._bounds(object.bounds())

	def __str__(self):
		if len(self) < 1:
			return ""
		result = ""
		for o in self:
			result += str(o)
		return _join(figCompoundBegin,
					 int(self._bounds.x1), int(self._bounds.y1),
					 int(self._bounds.x2), int(self._bounds.y2)) + "\n" + \
			   result + str(figCompoundEnd) + "\n"

def _readCompound(params):
	result = Compound()
	result._bounds.x1 = int(params[0])
	result._bounds.y1 = int(params[1])
	result._bounds.x2 = int(params[2])
	result._bounds.y2 = int(params[3])
	return result

# --------------------------------------------------------------------
#                                file
# --------------------------------------------------------------------

class File(Container):
	"""Main class of the `fig` module, represents an XFig document."""
	
	def __init__(self, inputFile = None):
		Container.__init__(self)
		self.colors = []
		self.colorhash = {}
		self.filename = None

		if inputFile == None:
			self.landscape = False
			self.centered = True
			self.metric = True
			self.paperSize = "A4"
			self.magnification = 100.0
			self.singlePage = True
			self.transparentColor = -2 # no transparency, -1 = background, else color#
			self.ppi = 1200 # figure units per inch
		else:
			lineIndex = 0
			commentCount = 0
			stack = []
			currentObject = None
			subLineExpected = 0
			if type(inputFile) == str:
				self.filename = inputFile
				inputFile = file(inputFile).readlines()
			elif hasattr(inputFile, "readlines"):
				if hasattr(inputFile, "name"):
					self.filename = inputFile.name
				inputFile = inputFile.readlines()
			# for error messages:
			filename = self.filename and "'%s'" % self.filename or "<unnamed>"
			for line in inputFile:
				line = line.strip()
				if line.startswith("#") or not line:
					commentCount += 1
					continue
				#print line
				if lineIndex == 0:
					self.landscape = (line.lower().startswith("landscape"))
				elif lineIndex == 1:
					self.centered = (line.lower().startswith("center"))
				elif lineIndex == 2:
					self.metric = (line.lower().startswith("metric"))
				elif lineIndex == 3:
					self.paperSize = line
				elif lineIndex == 4:
					self.magnification = float(line)
				elif lineIndex == 5:
					self.singlePage = (line.lower().startswith("single"))
				elif lineIndex == 6:
					self.transparentColor = int(line)
				elif lineIndex == 7:
					res, sysDummy = re.split(" +", line)
					self.ppi = int(res)
				else:
				  try:
					params = re.split(" +", line)
					if subLineExpected:
						subLineExpected = currentObject._readSub(params)
					else:
						objectType = int(params[0])
						subLineExpected = 0
						if objectType == figCustomColor:
							self.addColor(CustomColor(int(params[1]), params[2]))
						elif objectType == figPolygon:
							currentObject, subLineExpected = _readPolylineBase(params[1:])
						elif objectType == figArc:
							currentObject, subLineExpected = _readArcBase(params[1:])
						elif objectType == figSpline:
							currentObject, subLineExpected = _readSplineBase(params[1:])
						elif objectType == figText:
							assert line[-4:] == "\\001"
							currentObject, subLineExpected = _readText(
								params[1:], line.split(" ", 13)[-1][:-4])
						elif objectType == figEllipse:
							currentObject, subLineExpected = _readEllipseBase(params[1:])
						elif objectType == figCompoundBegin:
							stack.append(_readCompound(params[1:]))
						elif objectType == figCompoundEnd:
							currentObject = stack.pop()
						else:
							raise ValueError(
								"Unhandled object type %s!" % (objectType, ))
					if currentObject != None and not subLineExpected:
						if stack:
							stack[-1].append(currentObject)
						else:
							self.append(currentObject)
						currentObject = None
				  except ValueError:
					  sys.stderr.write("Parse error in %s, line %i:\n%s\n\n" %
									   (filename, lineIndex + commentCount + 1, line))
					  raise
				lineIndex += 1

	def append(self, object):
		"""Adds the object to this document.  `object` is supposed to
		be a `fig.Object`-derived object.  `CustomColor` objects are
		appended to self.colors as if `addColor()` was called."""

		if type(object) == CustomColor:
			self.addColor(object)
		else:
			Container.append(self, object)

	def addColor(self, hexCode):
		"""Adds a custom color to this document.  hexCode may be
		either a hex code like #ffee00 or a CustomColor instance."""
		
		if isinstance(hexCode, str):
			result = CustomColor(colorCustom0 + len(self.colors), hexCode)
		elif isinstance(hexCode, CustomColor):
			result = hexCode
			hexCode = result.hexCode
		else:
			raise TypeError("addColor() should be called with a hexCode (e.g. #ffee00) or a CustomColor instance")
		self.colors.append(result)
		self.colorhash[hexCode] = result
		return result

	def getColor(self, color, similarity = None):
		"""Returns a color object for the given color, adding a new
		custom color to this document if it does not yet exist.  The
		color can be given as tuple of R,G,B values or as hex string
		(e.g. (0, 255, 0) or '#00ff00' for green).  The range of valid
		R,G,B values depends on the type: integer values are expected
		to be in the range 0..255, while float values are interpreted
		as percentage values in the closed interval [0.0, 1.0].

		If a `CustomColor` object with the given color is already
		present, it will be returned.  Otherwise, `addColor` will be
		called, and the new object is returned.

		If the optional parameter `similarity` is > 0.0, getColor()
		will return the first color found whose RGB difference's
		magnitude is < `similarity`, if any (otherwise, it will call
		`addColor()`, exactly as if similarity was not used).  This is
		useful if you expect many thousands of slightly different
		colors, which are not supported by XFig.

		If `similarity` is given, but not > 0.0, `addColor()` will not be
		called, but a `KeyError` will be raised, if the exact color
		cannot be returned."""

		inputGiven = color
		if type(color) == float: # accept grayvalues as float (0..1)
			color = int(round(color*255))
		if type(color) == int: # accept grayvalues as int (0..255)
			color = (color, color, color)
		if type(color) == types.TupleType: # accept colors as 3-tuple of (0..255)
			if type(color[0]) == float:
				color = (int(round((color[0]*255))),
						 int(round((color[1]*255))),
						 int(round((color[2]*255))))
			color = "#%02x%02x%02x" % color
		if type(color) != types.StringType: # accept RGB color objects
			color = "#%02x%02x%02x" % tuple(color)
		assert len(color) == 7, \
			   "too large values given for red, green, or blue: %s" % (inputGiven, )
		try:
			return self.colorhash[color]
		except KeyError:
			if similarity != None:
				if not similarity > 0.0:
					raise # if similarity <= 0.0, don't add color

				if self.colors: # don't choke when there are no colors yet
					def rgbDiffSortTuple(otherRGB,
										 searchRGB = CustomColor(None, color)):
						return sum(map(lambda x: x*x, searchRGB-otherRGB)), otherRGB
					matches = map(rgbDiffSortTuple, self.colors)
					matches.sort()
					bestSqDiff, bestColor = matches[0]
					if bestSqDiff < similarity*similarity:
						return bestColor
			return self.addColor(color)

	def colorRGB(self, colorIndex):
		"""Returns a the R,G,B tuple for the given color index."""
		
		assert colorIndex >= 0 and colorIndex < colorCustom0 + len(self.colors), \
			   "invalid color index"
		if colorIndex < colorCustom0:
			return standardColors[colorIndex]
		else:
			return self.colors[colorIndex - colorCustom0].rgb()

	def gray(self, grayLevel):
		"""Returns a color representing the given graylevel (see
		getColor).  grayLevel can be a float in the range 0.0 - 1.0 or
		a 0 - 255 integer."""
		
		return self.getColor((grayLevel, grayLevel, grayLevel))

	def headerStr(self):
		"""Returns the first lines of the XFig file output, which contain
		global document information like orientation / units / ..."""
		
		result = "#FIG 3.2\n"
		if self.landscape:
			result += "Landscape\n"
		else:
			result += "Portrait\n"
		if self.centered:
			result += "Center\n"
		else:
			result += "Flush Left\n"
		if self.metric:
			result += "Metric\n"
		else:
			result += "Inches\n"
		result += self.paperSize + "\n"
		result += str(self.magnification) + "\n"
		if self.singlePage:
			result += "Single\n"
		else:
			result += "Multiple\n"
		result += str(self.transparentColor) + "\n"
		result += str(self.ppi) + " 2\n" # (2: only used coordinate system)
		return result

	def objectsStr(self):
		"""figfile.objectsStr()

		Returns the part of the XFig file containing all objects
		(but not the custom colors).  This is the same as str(object)
		concatenated for each object in `figfile`."""
		
		return "".join(map(str, self))

	def __str__(self):
		"""Returns the contents of this file in the XFig file format as string.
		See save()."""
		
		result = self.headerStr() + \
				 "".join(map(repr, self.colors)) + \
				 self.objectsStr()
		return result

	def save(self, filename = None, fig2dev = None):
		"""figfile.save(filename = None)

		Saves the contents of this file in the XFig file format to
		the file 'filename'.  Equivalent to::
		
		  file(filename, "w").write(str(figfile))

		If filename is not given, and figfile was constructed from an
		existing file, that one is overwritten (-> figfile.filename).
		(The filename becomes the new figfile.filename.)"""

		if filename != None:
			self.filename = filename
		assert self.filename, "figfile.save() needs a filename!"
		file(self.filename, "w").write(str(self))

		if fig2dev:
			self.fig2dev(lang = fig2dev)

		return self.filename

	def fig2dev(self, input = None, output = None, lang = "eps"):
		"""figfile.fig2dev(input = None, output = None, lang = "eps")
		
		Calls fig2dev on the file `input` to produce the file `output`.
		(Both default to the current figfile's filename and the same
		filename with the extension changed to `lang`.)
		Note that `output` must be a path *relative to the `input` path*!
		Returns the filename of the resulting file.

		Usually, you just call sth. like ::

		   figfile = fig.File("myfigfile.fig")
		   ...
		   figfile.save()
		   figfile.fig2dev(lang = "pdf")

		to produce myfigfile.pdf.  It is now even easier to use the
		following convenience shortcut::

		   figfile.save(fig2dev = "pdf")
		"""
		
		if input == None:
			input = self.filename

		path, basename = os.path.split(input)

		if not output:
			output = basename
			if output.endswith(".fig"):
				output = output[:-4]
			output += "." + lang
		
		oldcwd = None
		if path:
			oldcwd = os.path.abspath(".")
			os.chdir(path)

		try:
			cin, cout = os.popen4("fig2dev -L %s '%s' '%s'" % (
				lang, basename, output))
			cin.close()
			sys.stdout.write(cout.read())
			cout.close()
		finally:
			if oldcwd:
				os.chdir(oldcwd)

		return os.path.normpath(os.path.join(path, output))

	def saveEPS(self, basename = None):
		"""Saves the contents of this file to [basename].fig and calls
		fig2dev to create a [basename].eps, too.  The basename
		(without either .fig or .eps!) is returned, so that you can
		use expressions like::

		  resultBasename = figFile.saveEPS(namePrefix + "_%d" % index)

		Furthermore, the basename defaults to figFile.filename without
		the .fig."""

		if basename == None:
			assert self.filename, "figfile.save[EPS]() needs a filename!"
			basename = self.filename
		if basename.endswith(".fig") or basename.endswith(".eps"):
			basename = basename[:-4]

		self.save(basename + ".fig", fig2dev = "eps")

		return basename

# --------------------------------------------------------------------
#                              TESTING:
# --------------------------------------------------------------------

if __name__ == "__main__":
	if len(sys.argv) > 1:
		def normalize(text):
			result = []
			for line in text.split("\n"):
				if line and line[0] == "#": continue
				# canonical float representation:
				result.append(re.sub(r"(\.[0-9]+?)0*\b", r"\1", line.strip()))
			return result
		
		import difflib, re
		for fn in sys.argv[1:]:
			input = normalize(file(fn).read())
			output = normalize(str(File(fn)))
#           for line in difflib.unified_diff(input, output):
#               print line
			sm = difflib.SequenceMatcher(None, input, output)
			for code, b1, e1, b2, e2 in sm.get_opcodes():
				if code == 'equal':
					continue
				for li in range(b1, e1):
					print "-", input[li]
				for li in range(b2, e2):
					print "+", output[li]
			
	else:
		import doctest
		doctest.testfile('index.rst')

# FIGPY=../Diplomarbeit/Text/Figures/Sources/fig.py
# SED='sed s,\.0\+,,g'; for i in *.fig; do python $FIGPY $i | $SED > /tmp/foo && $SED $i | diff -ubd - /tmp/foo; done

# ATM, what's changing when loading/saving as above is:
# - the bounding boxes of splines
# - the bounding boxes of compounds
# - some spacing (XFig starts lines with "\t ", I am purposely leaving the " " out)
# - the display of floating point values (number of trailing zeros)

# TODO:
# - pull common code from SplineBase and PolylineBase into common base class
# - clean up reading code (File could group lines based on whitespace prefixes)
# - check shape factors of ApproximatedSpline / InterpolatedSpline
