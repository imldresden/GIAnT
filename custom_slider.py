import libavg
from libavg import widget, avg


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


class IntervalScrollBar(widget.ScrollBar):
    """
    Custom ScrollBar as interval slider.
    """
    def __init__(self, thumbExtent=0.1, **kwargs):
        self.__thumbExtent = thumbExtent
        super(IntervalScrollBar, self).__init__(**kwargs)

    def _initThumb(self, cfg):
        thumbUpBmp = avg.ImageNode(href="images/hor_grey.png", size=(1024, 1024)).getBitmap()
        thumbDownBmp = avg.ImageNode(href="images/hor_grey.png", size=(1024, 1024)).getBitmap()
        thumbDisabledBmp = avg.ImageNode(href="images/hor_grey.png", size=(1024, 1024)).getBitmap()
        endsExtent = cfg["thumbEndsExtent"]

        print "{}".format(type(thumbUpBmp))

        self._thumbNode = IntervalScrollBarThumb(upBmp=thumbUpBmp, downBmp=thumbDownBmp,
                                                 disabledBmp=thumbDisabledBmp, endsExtent=endsExtent)
        self.appendChild(self._thumbNode)


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
