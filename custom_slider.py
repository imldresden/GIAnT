import math
import libavg
from libavg import widget, avg, gesture


class IntervalSliderBase(avg.DivNode):
    """
    Curstom SliderBase to modify slider track (don't even create one).
    """
    THUMB_POS_CHANGED = avg.Publisher.genMessageID()
    PRESSED = avg.Publisher.genMessageID()
    RELEASED = avg.Publisher.genMessageID()

    def __init__(self, cfg, width=0, range=(0., 1.), thumbPos=0.0, parent=None, **kwargs):
        super(IntervalSliderBase, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.publish(IntervalSliderBase.THUMB_POS_CHANGED)
        self.publish(IntervalSliderBase.PRESSED)
        self.publish(IntervalSliderBase.RELEASED)

        self._initThumb(cfg)

        self._range = range
        self._thumbPos = thumbPos

        self.subscribe(self.SIZE_CHANGED, lambda newSize: self._positionNodes())
        self.size = (width, 20)

        self.__recognizer = gesture.DragRecognizer(self._thumbNode, friction=-1, detectedHandler=self.__onDragStart,
                                                   moveHandler=self.__onDrag, upHandler=self.__onUp)

    def getRange(self):
        return self._range

    def setRange(self, range):
        self._range = (float(range[0]), float(range[1]))
        self._positionNodes()

    # range[1] > range[0]: Reversed scrollbar.
    range = property(getRange, setRange)

    def getThumbPos(self):
        return self._thumbPos

    def setThumbPos(self, thumbPos):
        self._positionNodes(thumbPos)

    thumbPos = property(getThumbPos, setThumbPos)

    def _positionNodes(self, newSliderPos=None):
        if newSliderPos is not None:
            self._thumbPos = float(newSliderPos)

        self._constrainSliderPos()

        pixelRange = self._getScrollRangeInPixels()
        if self._getSliderRange() == 0:
            thumbPixelPos = 0
        else:
            thumbPixelPos = (((self._thumbPos-self._range[0])/self._getSliderRange())*pixelRange)
        self._thumbNode.x = thumbPixelPos

    def __onDragStart(self):
        self._thumbNode.visibleid = "DOWN"
        self.__dragStartPos = self._thumbPos
        self.notifySubscribers(IntervalScrollBar.PRESSED, [])

    def __onDrag(self, offset):
        pixelRange = self._getScrollRangeInPixels()
        if pixelRange == 0:
            normalizedOffset = 0
        else:
            normalizedOffset = offset.x/pixelRange
        oldThumbPos = self._thumbPos
        self._positionNodes(self.__dragStartPos + normalizedOffset*self._getSliderRange())
        if self._thumbPos != oldThumbPos:
            self.notifySubscribers(IntervalScrollBar.THUMB_POS_CHANGED, [self._thumbPos])

    def __onUp(self, offset):
        self.__onDrag(offset)
        self._thumbNode.visibleid = "UP"
        self.notifySubscribers(IntervalScrollBar.RELEASED, [])


class IntervalScrollBar(IntervalSliderBase):
    """
    Custom ScrollBar as interval slider.
    """
    def __init__(self, thumbExtent=0.1, skinObj=widget.skin.Skin.default, **kwargs):
        self.__thumbExtent = thumbExtent
        cfg = skinObj.defaultSliderCfg["horizontal"]
        super(IntervalScrollBar, self).__init__(cfg=cfg, **kwargs)

    def _initThumb(self, cfg):
        thumbUpBmp = avg.ImageNode(href="images/quad_white.png", size=(128, 128)).getBitmap()
        thumbDownBmp = avg.ImageNode(href="images/quad_white.png", size=(128, 128)).getBitmap()
        thumbDisabledBmp = avg.ImageNode(href="images/quad_white.png", size=(128, 128)).getBitmap()
        endsExtent = 1

        self._thumbNode = IntervalScrollBarThumb(upBmp=thumbUpBmp, downBmp=thumbDownBmp,
                                                 disabledBmp=thumbDisabledBmp, endsExtent=endsExtent)
        self.appendChild(self._thumbNode)

    def getThumbExtent(self):
        return self.__thumbExtent

    def setThumbExtent(self, thumbExtent):
        self.__thumbExtent = float(thumbExtent)
        self._positionNodes()

    thumbExtent = property(getThumbExtent, setThumbExtent)

    def _getScrollRangeInPixels(self):
        return self.size.x - self._thumbNode.width

    def _positionNodes(self, newSliderPos=None):
        effectiveRange = math.fabs(self._range[1] - self._range[0])
        thumbExtent = (self.__thumbExtent/effectiveRange)*self.size.x
        self._thumbNode.width = thumbExtent
        super(IntervalScrollBar, self)._positionNodes(newSliderPos)
        if self._range[1] < self._range[0]:
            # Reversed (upside-down) scrollbar
            self._thumbNode.x -= thumbExtent

    def _getSliderRange(self):
        if self._range[1] > self._range[0]:
            return self._range[1] - self._range[0] - self.__thumbExtent
        else:
            return self._range[1] - self._range[0] + self.__thumbExtent

    def _constrainSliderPos(self):
        rangeMin = min(self._range[0], self._range[1])
        rangeMax = max(self._range[0], self._range[1])
        self._thumbPos = max(rangeMin, self._thumbPos)
        self._thumbPos = min(rangeMax-self.__thumbExtent, self._thumbPos)


class IntervalScrollBarThumb(widget.SwitchNode):
    """
    Custom ScrollBar thumb.
    """
    def __init__(self, upBmp, downBmp, disabledBmp, endsExtent, minExtent=-1, **kwargs):

        super(IntervalScrollBarThumb, self).__init__(nodeMap=None, **kwargs)

        self.__upNode = widget.HStretchNode(src=upBmp, endsExtent=endsExtent, minExtent=minExtent)
        self.__downNode = widget.HStretchNode(src=downBmp, endsExtent=endsExtent, minExtent=minExtent)
        self.__disabledNode = widget.HStretchNode(src=disabledBmp, endsExtent=endsExtent, minExtent=minExtent)

        self.setNodeMap({
            "UP": self.__upNode,
            "DOWN": self.__downNode,
            "DISABLED": self.__disabledNode
        })
        self.visibleid = "UP"


class IntervalSlider(widget.Slider):
    """
    Implements a custom slider for an interval.
    Has two thumbs (interval start and interval end) and a range slider inbetween to move the whole interval.
    """
    def __init__(self, parent=None, **kwargs):
        # pass arguments to super and initialize C++ class
        super(IntervalSlider, self).__init__(**kwargs)
        self.registerInstance(self, parent)

    def _initThumb(self, cfg):
        thumbUpNode = libavg.RectNode(pos=(0, 0), size=(14, 14), color="FF0000", parent=None)
        thumbDownNode = libavg.RectNode(pos=(0, 0), size=(14, 14), color="FF0000", parent=None)
        thumbDisNode = libavg.RectNode(pos=(0, 0), size=(14, 14), color="FF0000", parent=None)
        self._thumbNode = IntervalSliderThumb(upNode=thumbUpNode, downNode=thumbDownNode, disabledNode=thumbDisNode)
        self.appendChild(self._thumbNode)


class IntervalSliderThumb(widget.SwitchNode):
    """
    Custom slider thumbs to allow libavg.RectNode's to be used as thumbs, not bitmaps.
    -> more freedom in adjusting thumb.
    """
    def __init__(self, upNode, downNode, disabledNode, **kwargs):
        nodeMap = {"UP": upNode, "DOWN": downNode, "DISABLED": disabledNode}
        super(IntervalSliderThumb, self).__init__(nodeMap=nodeMap, visibleid="UP", **kwargs)
