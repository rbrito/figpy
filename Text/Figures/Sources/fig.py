import sys, string, types, re

# object codes
figCustomColor   = 0
figEllipse       = 1
figPolygon       = 2
figText          = 4
figArc           = 5
figCompoundBegin = 6
figCompoundEnd   = -6

# line styles
lineStyleDefault          = -1
lineStyleSolid            = 0
lineStyleDashed           = 1
lineStyleDotted           = 2
lineStyleDashDotted       = 3
lineStyleDashDoubleDotted = 4
lineStyleDashTripleDotted = 5

# polygon types
ptPolyline    = 1
ptBox         = 2
ptPolygon     = 3
ptArcBox      = 4
ptPictureBBox = 5

# arc types
atPie  = 0
atOpen = 1

# fill styles
fillStyleNone    = -1
fillStyleSolid   = 20
fillStyleStripes = 42

# colors
colorDefault = -1
colorBlack   = 0
colorWhite   = 7
colorRed4    = 18
colorRed3    = 19
colorRed2    = 20

# alignments
alignLeft     = 0
alignCentered = 1
alignRight    = 2

# fonts
fontDefault   = 0
fontHelvetica = 16

# font flags
ffRigid      = 1
ffSpecial    = 2
ffPostScript = 4
ffHidden     = 8

def _join(*sequence):
	return string.join([str(item) for item in sequence], " ")

class _Rect:
	def __init__(self):
		self.empty = 1

	def __call__(self, other):
		if type(other) == types.InstanceType:
			if other.__class__ == _Rect:
				self.__call__((other.x1, other.y1))
				self.__call__((other.x2, other.y2))
		else:
			if self.empty:
				self.x1 = other[0]
				self.x2 = other[1]
				self.y1 = other[0]
				self.y2 = other[1]
				self.empty = 0
			else:
				self.x1 = min(self.x1, other[0])
				self.y1 = min(self.y1, other[1])
				self.x2 = max(self.x2, other[0])
				self.y2 = max(self.y2, other[1])

class CustomColor:
	def __init__(self, index, colorCode):
		self.index = index
		self.colorCode = colorCode

	def __repr__(self):
		return _join(figCustomColor, self.index, self.colorCode) + "\n"

	def __str__(self):
		return str(self.index)

class Object:
	def __init__(self):
		self.subType = None
		self.lineStyle = lineStyleDefault
		self.lineWidth = 1
		self.penColor = colorDefault
		self.fillColor = colorDefault
		self.depth = 50
		self.penStyle = 0 # not used
		self.fillStyle = -1
		self.styleValue = 0.0
		self.joinStyle = 0
		self.capStyle = 0
		self.radius = -1
		self.hasForwardArrow = 0
		self.hasBackwardArrow = 0

class Arrow:
	def __init__(self, params):
		self.params = params

	def __str__(self):
		return _join(*self.params) + "\n"

class ArcBase(Object):
	def __init__(self):
		Object.__init__(self)
		self.points = []

	def __str__(self):
		result = _join(figPolygon, self.subType,
					   self.lineStyle, self.lineWidth,
					   self.penColor, self.fillColor,
					   self.depth, self.penStyle,
					   self.fillStyle, self.styleValue,
					   self.capStyle, self.direction,
					   self.hasForwardArrow, self.hasBackwardArrow,
					   self.centerX, self.centerY,
					   self.points[0][0], self.points[0][1],
					   self.points[1][0], self.points[1][1],
					   self.points[2][0], self.points[2][1]) + "\n"

		if self.hasForwardArrow:
			result += "\t" + str(self.forwardArrow)
		if self.hasBackwardArrow:
			result += "\t" + str(self.backwardArrow)
		return result + "\n"

	def bounds(self):
		result = _Rect()
		for point in self.points:
			result(point)
		return result

	def readSub(self, lineIndex, params):
		if not self.hasForwardArrow:
			lineIndex += 1
		if lineIndex == 0:
			self.forwardArrow = Arrow(params)
			return

		if lineIndex == 1:
			self.backwardArrow = Arrow(params)
			return

		sys.stderr.write("Unhandled sublineIndex for arc object: %i!\n" % lineIndex)

def readArcBase(params):
	result = ArcBase()
	result.subType = int(params[0])
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
	result.hasForwardArrow = int(params[11])
	result.hasBackwardArrow = int(params[12])
	result.centerX = float(params[13])
	result.centerY = float(params[14])
	result.points = [(int(params[15]), int(params[16])),
					 (int(params[17]), int(params[18])),
					 (int(params[19]), int(params[20]))]
	# pointCount = int(params[14])
	subLines = 0
	if result.hasForwardArrow:
		subLines += 1
	if result.hasBackwardArrow:
		subLines += 1
	return result, subLines

class EllipseBase(Object):
	def __init__(self):
		Object.__init__(self)
		self.angle = 0.0
		self.center = (0, 0)
		self.radius = (0, 0)
		self.start = (0, 0)
		self.end = (0, 0)

	def __str__(self):
		return _join(figEllipse, self.subType,
					   self.lineStyle, self.lineWidth,
					   self.penColor, self.fillColor,
					   self.depth, self.penStyle,
					   self.fillStyle, self.styleValue,
					   1, # "1" is self.direction
					   self.angle,
					   self.center[0], self.center[1],
					   self.radius[0], self.radius[1],
					   self.start[0], self.start[1],
					   self.end[0], self.end[1]) + "\n"

	def bounds(self):
		result = _Rect()
		result(((self.center[0] - self.radius[0]),
				(self.center[1] - self.radius[1])))
		result(((self.center[0] + self.radius[0]),
				(self.center[1] + self.radius[1])))
		return result

def readEllipseBase(params):
	result = EllipseBase()
	result.subType = int(params[0])
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

class PolylineBase(Object):
	def __init__(self):
		Object.__init__(self)
		self.points = []
		self.closed = 1

	def __str__(self):
		pointCount = len(self.points)
		if self.closed:
			pointCount += 1
		result = _join(figPolygon, self.subType,
					   self.lineStyle, self.lineWidth,
					   self.penColor, self.fillColor,
					   self.depth, self.penStyle,
					   self.fillStyle, self.styleValue,
					   self.joinStyle, self.capStyle, self.radius,
					   self.hasForwardArrow, self.hasBackwardArrow,
					   pointCount) + "\n"

		if self.hasForwardArrow:
			result += "\t" + str(self.forwardArrow)
		if self.hasBackwardArrow:
			result += "\t" + str(self.backwardArrow)
		if self.subType == ptPictureBBox:
			result += "\t" + _join(self.flipped, self.pictureFilename) + "\n"
		result += "\t" + _join(self.points[0][0], self.points[0][1])
		for point in self.points[1:]:
			result += _join("", point[0], point[1])
		if self.closed:
			result += _join("", self.points[0][0], self.points[0][1])
		return result + "\n"

	def bounds(self):
		result = _Rect()
		for point in self.points:
			result(point)
		return result

	def readSub(self, lineIndex, params):
		if not self.hasForwardArrow:
			lineIndex += 1
		if lineIndex == 0:
			self.forwardArrow = Arrow(params)
			return

		if not self.hasBackwardArrow:
			lineIndex += 1
		if lineIndex == 1:
			self.backwardArrow = Arrow(params)
			return

		if not self.subType == ptPictureBBox:
			lineIndex += 1
		if lineIndex == 2:
			self.flipped = int(params[0])
			self.pictureFilename = params[1]
			return

		pointCount = len(params) / 2
		if self.subType == ptPolygon or self.subType == ptBox:
			self.closed = 1
			pointCount -= 1
		else:
			self.closed = 0
		for pointIndex in range(pointCount):
			self.points.append((int(params[pointIndex * 2]),
								int(params[pointIndex * 2 + 1])))

def readPolylineBase(params):
	result = PolylineBase()
	result.subType = int(params[0])
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
	result.hasForwardArrow = int(params[12])
	result.hasBackwardArrow = int(params[13])
	# pointCount = int(params[14])
	subLines = 1 # for the points
	if result.hasForwardArrow:
		subLines += 1
	if result.hasBackwardArrow:
		subLines += 1
	if result.subType == ptPictureBBox:
		subLines += 1
	return result, subLines

class PolyBox(PolylineBase):
	def __init__(self, x1, y1, x2, y2):
		PolylineBase.__init__(self)
		self.subType = ptBox
		self.points.append((x1, y1))
		self.points.append((x2, y1))
		self.points.append((x2, y2))
		self.points.append((x1, y2))
		self.closed = 1

class PolyLine(PolylineBase):
	def __init__(self, *points):
		PolylineBase.__init__(self)
		self.subType = ptPolyline
		self.points = points
		self.closed = 0

class Text(Object):
	def __init__(self, x, y, text, alignment = alignLeft):
		Object.__init__(self)
		self.text = text
		self.font = fontDefault
		self.fontSize = 12.0
		self.fontAngle = 0.0
		self.fontFlags = ffPostScript
		self.height = 136
		self.length = 100 # dummy value
		self.x = x
		self.y = y
		self.subType = alignment

	def bounds(self):
		result = _Rect()
		if self.subType == alignLeft:
			result((self.x,               self.y - self.height))
			result((self.x + self.length, self.y))
		elif self.subType == alignCentered:
			result((self.x - self.length/2, self.y - self.height))
			result((self.x + self.length/2, self.y))
		elif self.subType == alignRight:
			result((self.x,               self.y - self.height))
			result((self.x + self.length, self.y))
		return result

	def __str__(self):
		result = _join(figText, self.subType,
					   self.penColor, self.depth, self.penStyle,
					   self.font, self.fontSize, self.fontAngle, self.fontFlags,
					   self.height, self.length, self.x, self.y,
					   self.text + "\\001") + "\n"

		return result

def readText(params):
	result = Text(int(params[10]), int(params[11]),
				  params[12][:-4], int(params[0]))
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

class Compound:
	def __init__(self, parent = None):
		self.objects = []
		if parent != None:
			parent.append(self)

	def append(self, object):
		self.objects.append(object)

	def __str__(self):
		if len(self.objects) < 1:
			return ""
		bounds = _Rect()
		result = ""
		for o in self.objects:
			result += str(o)
			bounds(o.bounds())
		return _join(figCompoundBegin,
					 int(bounds.x1), int(bounds.y1),
					 int(bounds.x2), int(bounds.y2)) + "\n" + \
			   result + str(figCompoundEnd) + "\n"

class File:
	def __init__(self, filename = None):
		self.objects = []
		self.colors = []

		if filename == None:
			self.landscape = 1
			self.centered = 1
			self.metric = 1
			self.papersize = "A4"
			self.magnification = 100.0
			self.singlePage = 1
			self.transparentColor = -2 # no transparency, -1 = background, else color#
			self.ppi = 1200 # figure units per inch
		else:
			lineIndex = 0
			stack = []
			currentObject = None
			subLinesExpected = 0
			subLineIndex = 0
			for line in file(filename).readlines():
				if line.startswith("#"):
					continue
				line = line.strip()
				#print line
				if lineIndex == 0:
					self.landscape = (line.startswith("Landscape"))
				elif lineIndex == 1:
					self.centered = (line.startswith("Center"))
				elif lineIndex == 2:
					self.metric = (line.startswith("Metric"))
				elif lineIndex == 3:
					self.papersize = line
				elif lineIndex == 4:
					self.magnification = float(line)
				elif lineIndex == 5:
					self.singlePage = (line.startswith("Single"))
				elif lineIndex == 6:
					self.transparentColor = int(line)
				elif lineIndex == 7:
					res, sysDummy = re.split(" +", line)
					self.ppi = int(res)
				else:
					params = re.split(" +", line)
					if subLinesExpected > subLineIndex:
						currentObject.readSub(subLineIndex, params)
						subLineIndex += 1
					else:
						objectType = int(params[0])
						subLineIndex = 0
						subLinesExpected = 0
						if objectType == figCustomColor:
							self.colors.append(
								CustomColor(int(params[1]), params[2]))
						elif objectType == figPolygon:
							currentObject, subLinesExpected = readPolylineBase(params[1:])
						elif objectType == figArc:
							currentObject, subLinesExpected = readArcBase(params[1:])
						elif objectType == figText:
							currentObject, subLinesExpected = readText(params[1:])
						elif objectType == figEllipse:
							currentObject, subLinesExpected = readEllipseBase(params[1:])
						elif objectType == figCompoundBegin:
							stack.append(Compound())
						elif objectType == figCompoundEnd:
							currentObject = stack.pop()
						else:
							sys.stderr.write("Unhandled object type in line %i:\n%s" %
											 (lineIndex, line))
							sys.exit(1)
					if currentObject != None and subLinesExpected == subLineIndex:
						if len(stack) > 0:
							stack[-1].append(currentObject)
						else:
							self.objects.append(currentObject)
						currentObject = None
				lineIndex += 1

	def append(self, object):
		if object.__class__ == CustomColor:
			self.colors.append(object)
		else:
			self.objects.append(object)

	def addColor(self, colorCode):
		result = CustomColor(32 + len(self.colors), colorCode)
		self.colors.append(result)
		return result

	def __str__(self):
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
		result += self.papersize + "\n"
		result += str(self.magnification) + "\n"
		if self.singlePage:
			result += "Single\n"
		else:
			result += "Multiple\n"
		result += str(self.transparentColor) + "\n"
		result += str(self.ppi) + " 2\n" # (2: only used coordinate system)
		for color in self.colors:
			result += repr(color)
		for object in self.objects:
			result += str(object)

		return result
