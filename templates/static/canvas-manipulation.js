/*!
 canvas-manipulation - v0.3.0 - 2013-09-22
 ssh://git@bitbucket.org/vogdb/canvas-manipulation.git
 Copyright (c) 2013 Sanin Aleksey aka vogdb; Licensed MIT
*/
/**
 * Created: vogdb Date: 9/8/13 Time: 1:44 PM
 */
function Matrix(values) {
  if (!Array.isArray(values)) {
    throw new Error('Array must be passed')
  }
  if (values.length !== Matrix.rowLen) {
    throw new Error('Matrix must have 3 rows')
  }
  this._values = []
  for (var rowIndex = 0; rowIndex < Matrix.rowLen; rowIndex++) {
    var row = values[rowIndex]
    if (values.length !== Matrix.colLen) {
      throw new Error('Matrix must have 3 cols on row: ' + rowIndex)
    }
    this._values[rowIndex] = []
    for (var colIndex = 0; colIndex < Matrix.colLen; colIndex++) {
      this._values[rowIndex][colIndex] = values[rowIndex][colIndex];
    }
  }
}

Matrix.rowLen = 3;
Matrix.colLen = 3;

Matrix.prototype.multiply = function (matrix) {
  if (Array.isArray(matrix)) {
    matrix = new Matrix(matrix);
  }

  if (!matrix instanceof Matrix) {
    throw new Error('Argument passed is not a valid Matrix object');
  }

  var product = new Matrix([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
  ])

  var leftM = this._values
  var rightM = matrix._values
  for (var rowIndex = 0; rowIndex < Matrix.rowLen; rowIndex++) {
    for (var colIndex = 0; colIndex < Matrix.colLen; colIndex++) {
      var square = 0
      for (var i = 0; i < Matrix.colLen; i++) {
        square += leftM[rowIndex][i] * rightM[i][colIndex]
      }
      product._values[rowIndex][colIndex] = square
    }
  }
  delete this._values
  this._values = product._values
  product._values = null
  return this
}

Matrix.prototype.clone = function () {
  return new Matrix(this._values)
}

Matrix.prototype.inverse = function () {
  // Declare variables
  var ratio
  var a
  var rowLen = Matrix.rowLen
  var values = this._values

  // Put an identity matrix to the right of matrix
  for (var i = 0; i < rowLen; i++) {
    for (var j = rowLen; j < 2 * Matrix.colLen; j++) {
      if (i === (j - rowLen)) {
        values[i][j] = 1
      }
      else {
        values[i][j] = 0
      }
    }
  }

  for (var i = 0; i < rowLen; i++) {
    for (var j = 0; j < rowLen; j++) {
      if (i !== j) {
        ratio = values[j][i] / values[i][i]
        for (var k = 0; k < 2 * rowLen; k++) {
          values[j][k] -= ratio * values[i][k]
        }
      }
    }
  }

  for (var i = 0; i < rowLen; i++) {
    a = values[i][i]
    for (var j = 0; j < 2 * rowLen; j++) {
      values[i][j] /= a
    }
  }

  // Remove the left-hand identity matrix
  for (var i = 0; i < rowLen; i++) {
    values[i].splice(0, rowLen)
  }

  return this
}
/**
 * Offers restricted functionality of svg for the part of transformations.
 * By svg means "document.createElementNS("http://www.w3.org/2000/svg", 'svg')"
 */
var SvgTransformSub = function () {
  //TODO if svg exists use it else substitute it
}

SvgTransformSub.prototype.createSVGMatrix = function () {
  return new SvgMatrixSub()
}

SvgTransformSub.prototype.createSVGPoint = function () {
  return new SvgPointSub()
}

/**
 * Offers restricted functionality of <a href="http://www.w3.org/TR/SVG11/coords.html#InterfaceSVGMatrix">SVGMatrix</a>
 * @param matrix Matrix @see <a href="https://github.com/angusgibbs/matrix">https://github.com/angusgibbs/matrix</a>
 */
var SvgMatrixSub = function (matrix) {
  if (matrix) {
    this.matrix = matrix
  } else {
    this.matrix = new Matrix([
       [1, 0, 0]
      ,[0, 1, 0]
      ,[0, 0, 1]
    ])
  }
}

SvgMatrixSub.prototype.setTransformFromArray = function (a, b, c, d, e, f) {
  var values = this.matrix._values
  values[0][0] = a
  values[1][0] = b
  values[0][1] = c
  values[1][1] = d
  values[0][2] = e
  values[1][2] = f
}

SvgMatrixSub.prototype.getTransformAsArray = function () {
  var values = this.matrix._values
  return [
     values[0][0]
    ,values[1][0]
    ,values[0][1]
    ,values[1][1]
    ,values[0][2]
    ,values[1][2]
  ]
}

SvgMatrixSub.prototype.translate = function (tx, ty) {
  return this._multiply([
     [1, 0, tx]
    ,[0, 1, ty]
    ,[0, 0, 1]
  ])
}

SvgMatrixSub.prototype.scaleNonUniform = function (sx, sy) {
  return this._multiply([
     [sx, 0, 0]
    ,[0, sy, 0]
    ,[0, 0, 1]
  ])
}

SvgMatrixSub.prototype.rotate = function (a) {
  return this._multiply([
     [Math.cos(a), -Math.sin(a), 0]
    ,[Math.sin(a), Math.cos(a), 0]
    ,[0, 0, 1]
  ])
}

SvgMatrixSub.prototype._multiply = function (matrix) {
  var result = new SvgMatrixSub(this.matrix.clone())
  result.matrix.multiply(new Matrix(matrix))
  return result
}

SvgMatrixSub.prototype.inverse = function () {
  var result = new SvgMatrixSub(this.matrix.clone())
  result.matrix.inverse()
  return result
}


/**
 * Offers restricted functionality of SVGMatrix {@url http://www.w3.org/TR/SVG11/coords.html#InterfaceSVGMatrix}
 */
var SvgPointSub = function () {
  this.x
  this.y
}

SvgPointSub.prototype.matrixTransform = function (matrix) {
  var resultMatrix = matrix.matrix.clone().multiply(new Matrix([
     [this.x]
    ,[this.y]
    ,[1]
  ]))
  var result = new SvgPointSub()
  result.x = resultMatrix._values[0][0]
  result.y = resultMatrix._values[1][0]
  return result
}

/**
 * Mixin which enables canvas context to save applied transformations.
 * @param canvasContext canvas.getContext('2d')
 */
var TrackTransform = function (canvasContext) {
  var svg = new SvgTransformSub()
  var transformMatrix = svg.createSVGMatrix()

  canvasContext.getTransformMatrix = function () {
    return transformMatrix
  }


  var savedTransforms = []
  var save = canvasContext.save
  canvasContext.save = function () {
    savedTransforms.push(transformMatrix.translate(0, 0))
    return save.call(canvasContext)
  }
  var restore = canvasContext.restore
  canvasContext.restore = function () {
    transformMatrix = savedTransforms.pop()
    return restore.call(canvasContext)
  }


  var scale = canvasContext.scale
  canvasContext.scale = function (sx, sy) {
    transformMatrix = transformMatrix.scaleNonUniform(sx, sy)
    return scale.call(canvasContext, sx, sy)
  }

  var rotate = canvasContext.rotate
  canvasContext.rotate = function (radians) {
    transformMatrix = transformMatrix.rotate(radians)
    return rotate.call(canvasContext, radians)
  }

  var translate = canvasContext.translate
  canvasContext.translate = function (dx, dy) {
    transformMatrix = transformMatrix.translate(dx, dy)
    return translate.call(canvasContext, dx, dy)
  }

  var transform = canvasContext.transform
  canvasContext.transform = function (a, b, c, d, e, f) {
    var matrix = svg.createSVGMatrix()
    matrix.setTransformFromArray(a, b, c, d, e, f)
    transformMatrix = transformMatrix.multiply(matrix)
    return transform.call(canvasContext, a, b, c, d, e, f)
  }

  var setTransform = canvasContext.setTransform
  canvasContext.setTransform = function (a, b, c, d, e, f) {
    transformMatrix.setTransformFromArray(a, b, c, d, e, f)
    return setTransform.call(canvasContext, a, b, c, d, e, f)
  }

  canvasContext.setTransformMatrix = function (matrix) {
    transformMatrix = matrix
    setTransform.apply(canvasContext, matrix.getTransformAsArray())
  }


  var pt = svg.createSVGPoint()
  canvasContext.transformedPoint = function (x, y) {
    pt.x = x
    pt.y = y
    return pt.matrixTransform(transformMatrix.inverse())
  }


  canvasContext.clearTransformedRect = function (x, y, w, h) {
    var p1 = canvasContext.transformedPoint(x, y)
    var p2 = canvasContext.transformedPoint(x + w, y + h)
    canvasContext.clearRect(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y)
  }

  canvasContext.clearCanvas = function () {
    canvasContext.save()
    // Use the identity matrix while clearing the canvas
    canvasContext.setTransform(1, 0, 0, 1, 0, 0)
    canvasContext.clearRect(0, 0, canvasContext.canvas.width, canvasContext.canvas.height)
    canvasContext.restore()
  }

}
/**
 * @param canvas canvas to manipulate
 * @param {Function} draw user function that does main drawing
 * @param dragBounds boundaries in which drag can be done.
 * @param {Number} dragBounds.leftTop.x x coordinate. 0 by default.
 * @param {Number} dragBounds.leftTop.y y coordinate. 0 by default.
 * @param {Number} dragBounds.rightBottom.x x coordinate. canvas.width by default.
 * @param {Number} dragBounds.rightBottom.y y coordinate. canvas.height by default.
 * @constructor
 */
var CanvasManipulation = function (canvas, draw, dragBounds) {
  this._draw = draw
  this._canvas = canvas
  this._initDragBounds(dragBounds)
  this._dragStartPoint = null
}

CanvasManipulation.prototype.init = function () {
  this._initCanvasContext()
}

/**
 * Sets canvas size by its bounds.
 * <code>canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight</code>
 * If canvas has inner elements such as zoom buttons then
 * they positioning and sizing better be done in this method. This method
 * useful for the mobile applications. If monitor changes orientation then you
 * can call this method and canvas will adapt new size accordingly.
 */
CanvasManipulation.prototype.layout = function () {
  this._calculateCanvasSize()
}

CanvasManipulation.prototype._calculateCanvasSize = function () {
  this._canvas.width = $("#player_location_radar_widget").width()
  this._canvas.height = $("#player_location_radar_widget").height()
}

CanvasManipulation.prototype._initCanvasContext = function () {
  this._ctx = this._canvas.getContext('2d')
  TrackTransform(this._ctx)
}

CanvasManipulation.prototype._initDragBounds = function (dragBounds) {
  dragBounds = dragBounds || {}
  this._dragBounds = {}
  if (!dragBounds['leftTop']) {
    this._dragBounds.leftTop = {x: 0, y: 0}
  } else {
    this._dragBounds.leftTop = dragBounds['leftTop']
  }
  if (!dragBounds['rightBottom']) {
    this._dragBounds.rightBottom = {x: this._canvas.width, y: this._canvas.height}
  } else {
    this._dragBounds.rightBottom = dragBounds['rightBottom']
  }
  //extending bounds so rotating of canvas will fit in
//  this._dragBounds.leftTop.x = this._dragBounds.leftTop.x - this._dragBounds.rightBottom.x
//  this._dragBounds.leftTop.y = this._dragBounds.leftTop.y - this._dragBounds.rightBottom.y

//  this._dragBounds.rightBottom.x = 2 * this._dragBounds.rightBottom.x
//  this._dragBounds.rightBottom.y = 2 * this._dragBounds.rightBottom.y
}

/*
 CanvasManipulation.prototype._inDragBounds = function (point) {
 var leftTop = this._dragBounds.leftTop
 var rightBottom = this._dragBounds.rightBottom
 return (point.x >= leftTop.x && point.y >= leftTop.y) && (point.x <= rightBottom.x && point.y <= rightBottom.y)
 }
 */

CanvasManipulation.prototype._canDrag = function (value, min, max, dragValue) {
  return (value >= min || (value < min && dragValue < 0)) && (value <= max || (value > max && dragValue > 0))
}

CanvasManipulation.prototype._dragDistance = function (startPoint, endPoint) {
  var leftTop = this._dragBounds.leftTop
  var rightBottom = this._dragBounds.rightBottom
  var pt0 = this._ctx.transformedPoint(0, 0)
  var distanceX = endPoint.x - startPoint.x
  if (!this._canDrag(pt0.x, leftTop.x, rightBottom.x, distanceX)) {
    distanceX = 0
  }
  var distanceY = endPoint.y - startPoint.y
  if (!this._canDrag(pt0.y, leftTop.y, rightBottom.y, distanceY)) {
    distanceY = 0
  }
  return {x: distanceX, y: distanceY}
}

/**
 * @param onPoint drag start point
 * @param {Number} onPoint.x x coordinate
 * @param {Number} onPoint.y y coordinate
 */
CanvasManipulation.prototype.dragStart = function (onPoint) {
  var pt = this._ctx.transformedPoint(onPoint.x, onPoint.y)
  //if (this._inDragBounds(pt)) {
  this._dragStartPoint = pt
  //}
}

/**
 * @param onPoint point where to drag. Drag won't work if dragStart method hasn't been called.
 * @param {Number} onPoint.x x coordinate
 * @param {Number} onPoint.y y coordinate
 */
CanvasManipulation.prototype.drag = function (onPoint) {
  if (this._dragStartPoint) {
    var pt = this._ctx.transformedPoint(onPoint.x, onPoint.y)
    var distance = this._dragDistance(this._dragStartPoint, pt)
    this._ctx.translate(distance.x, distance.y)
    this._draw()
  }
}

CanvasManipulation.prototype.dragEnd = function () {
  this._dragStartPoint = null
}

CanvasManipulation.prototype.zoomFactor = 1.1
CanvasManipulation.prototype.zoomMax = 10
CanvasManipulation.prototype.zoomMin = -100
CanvasManipulation.prototype.zoomCurrent = 1

/**
 * @param onPoint zoom center
 * @param {Number} onPoint.x x coordinate
 * @param {Number} onPoint.y y coordinate
 * @param {Number} value zoom value. Max is 10. Min is -10.
 * Zoom factor formula is <code>Math.pow(1.1, value)</code>
 */
CanvasManipulation.prototype.zoom = function (onPoint, value) {
  var pt = this._ctx.transformedPoint(onPoint.x, onPoint.y)
  this._ctx.translate(pt.x, pt.y)
  if (this.zoomCurrent + value > this.zoomMax) {
    value = this.zoomMax - this.zoomCurrent
  }
  if (this.zoomCurrent + value < this.zoomMin) {
    value = this.zoomMin - this.zoomCurrent
  }
  this.zoomCurrent = this.zoomCurrent + value
  var factor = Math.pow(this.zoomFactor, value)
  this._ctx.scale(factor, factor)
  //this.updateBoundsScale(factor)
  this._ctx.translate(-pt.x, -pt.y)
  this._draw()
}

/**
 * @param center rotation center
 * @param {Number} center.x x coordinate
 * @param {Number} center.y y coordinate
 * @param {Number} radians rotation angle in radians
 */
CanvasManipulation.prototype.rotate = function (center, radians) {
  var pt = this._ctx.transformedPoint(center.x, center.y)
  this._ctx.translate(pt.x, pt.y)
  this._ctx.rotate(radians)
  //this.updateBoundsRotate(angle)
  this._ctx.translate(-pt.x, -pt.y)
  this._draw()
}

CanvasManipulation.prototype.getCanvas = function () {
  return this._canvas
}

/*
 TODO more careful implementation of dragBounds
 CanvasManipulation.prototype.updateBoundsScale = function (scale) {
 var matrix = new SvgMatrixSub()
 this.updateBounds(matrix.scaleNonUniform(scale, scale).inverse())
 }

 CanvasManipulation.prototype.updateBoundsRotate = function (angle) {
 var matrix = new SvgMatrixSub()
 this.updateBounds(matrix.rotate(angle))
 }

 CanvasManipulation.prototype.updateBounds = function (matrix) {
 this._dragBounds.leftTop = this._ctx.matrixTransformPoint(this._dragBounds.leftTop.x, this._dragBounds.leftTop.y, matrix)
 this._dragBounds.rightBottom = this._ctx.matrixTransformPoint(this._dragBounds.rightBottom.x, this._dragBounds.rightBottom.y, matrix)
 }
 */