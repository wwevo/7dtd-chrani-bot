var previousInit = CanvasManipulation.prototype.init
CanvasManipulation.prototype.init = function () {
  previousInit.call(this, arguments)
  this.initMouseListeners()
}

CanvasManipulation.prototype.initMouseListeners = function () {
  var self = this
  var canvas = this.getCanvas()
  canvas.addEventListener('mousedown', function (evt) {
    self.dragStart(self.mouseCoord(evt))
  }, false)
  canvas.addEventListener('mousemove', function (evt) {
    self.drag(self.mouseCoord(evt))
  }, false)
  canvas.addEventListener('mouseup', function (evt) {
    self.dragEnd(evt)
  }, false)
  var handleScroll = function (evt) {
    var delta = evt.wheelDelta ? evt.wheelDelta / 40 : evt.detail ? -evt.detail : 0
    if (delta) {
      self.zoom(self.mouseCoord(evt), delta)
    }
    return evt.preventDefault() && false
  }
  canvas.addEventListener('DOMMouseScroll', handleScroll, false)
  canvas.addEventListener('mousewheel', handleScroll, false)
}

CanvasManipulation.prototype.mouseCoord = function (evt) {
  var ex = evt.offsetX || (evt.pageX - this.getCanvas().offsetLeft)
  var ey = evt.offsetY || (evt.pageY - this.getCanvas().offsetTop)
  return {x: ex, y: ey}
}