"""
graph for correspondence analysis
"""

BROWSE_RECTANGLE = 4
BROWSE_CIRCLE= 5


from OWGraph import *
from math import sqrt
from numpy import arange, sign
import operator

class OWCorrAnalysisGraph(OWGraph):
    def __init__(self, parent = None, name = "None"):
        OWGraph.__init__(self, parent, name)
        
        self.browseKey = None
        self.browseCurve = None
        
        self.radius  = 0.5
        self.pointWidth = 5
        
        self.showAxisScale = 1
        self.showXaxisTitle= 1
        self.showYLaxisTitle = 1
        self.showLegend = 1
##        self.showClusters = 0
        self.showFilledSymbols = 1
        self.labelSize = 12
        self.showRowLabels = 1
        self.showColumnLabels = 1
        self.maxPoints = 10
        
##        self.tooltipKind = 1
        
        self.markLines = []
        
        self.connect(self, SIGNAL("plotMouseMoved(const QMouseEvent &)"), self.onMouseMoved)
        self.connect(self, SIGNAL('plotMousePressed(const QMouseEvent&)'), self.onMousePressed)
        self.connect(self, SIGNAL('plotMouseReleased(const QMouseEvent&)'),self.onMouseReleased)        
        
    def activateBrowsing(self, activate):
        if activate:
            self.removeBrowsingCurve()
            self.markLines = []
            self.state = BROWSE_RECTANGLE
            self.browseCurve = SelectionCurve(self, pen = Qt.DashLine)
            self.browseKey = self.insertCurve(self.browseCurve)    
            
            self.__fixAxes()
        else:
            self.__backToZoom()
            
    def activateBrowsingCircle(self, activate):
        if activate:
            self.removeBrowsingCurve()
            self.markLines = []
            self.state = BROWSE_CIRCLE
            self.browseCurve = SelectionCurve(self, pen = Qt.DashLine)
            self.browseKey = self.insertCurve(self.browseCurve)      
     
            self.__fixAxes()
        else:
            self.__backToZoom()
    
    def __backToZoom(self):
        self.state = ZOOMING
        self.removeBrowsingCurve()
        for line in self.markLines:
            self.removeCurve(line)    
        self.markLines = []
        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.xTop)
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.setAxisAutoScale(QwtPlot.yRight)
        self.replot()        
        
    def __fixAxes(self):
        self.setAxisScale(QwtPlot.xBottom, self.axisScale(QwtPlot.xBottom).lBound(), self.axisScale(QwtPlot.xBottom).hBound())
        self.setAxisScale(QwtPlot.xTop, self.axisScale(QwtPlot.xTop).lBound(), self.axisScale(QwtPlot.xTop).hBound())
        self.setAxisScale(QwtPlot.yLeft, self.axisScale(QwtPlot.yLeft).lBound(), self.axisScale(QwtPlot.yLeft).hBound())
        self.setAxisScale(QwtPlot.yRight, self.axisScale(QwtPlot.yRight).lBound(), self.axisScale(QwtPlot.yRight).hBound())         
            
    def removeBrowsingCurve(self):
        if self.browseKey: self.removeCurve(self.browseKey)
        self.browseCurve = None
        self.browseKey = None
     
    def onMouseMoved(self, e):
        if self.state == BROWSE_RECTANGLE:
            xFloat = self.invTransform(QwtPlot.xBottom, e.x())
            yFloat = self.invTransform(QwtPlot.yLeft, e.y())  
            
            self.createCurve(xFloat, yFloat, 0)
            
            ##
            self.removeMarkers()
            for line in self.markLines:
                self.removeCurve(line)
            self.markLines = []
##            print self.tips.positions
            
            cor = [(x, y, self.tips.texts[i]) for (i,(x,y, cx, cy)) in enumerate(self.tips.positions) if abs(xFloat - x)  <= self.radius and abs(yFloat - y) <= self.radius]
            self.addMarkers(cor, xFloat, yFloat, self.radius)
##            for x, y, text in cor:
##                self.addMarker(text, x, y)
            
            ##
            
            self.replot()

            self.event(e)            
        elif self.state == BROWSE_CIRCLE:
            xFloat = self.invTransform(QwtPlot.xBottom, e.x())
            yFloat = self.invTransform(QwtPlot.yLeft, e.y())     
            self.createCurve(xFloat, yFloat, 1)
                
            #
            self.removeMarkers()
            for line in self.markLines:
                self.removeCurve(line)
            self.markLines = []            
            cor = [(x, y, self.tips.texts[i]) for (i,(x,y, cx, cy)) in enumerate(self.tips.positions) if ((xFloat - x)*(xFloat - x) + (yFloat - y)*(yFloat - y) <= self.radius * self.radius)]
            self.addMarkers(cor, xFloat, yFloat, self.radius)
##            for x, y, text in cor:
##                self.addMarker(text, x, y)
    
            #
            self.replot()   
            
            self.event(e) 
        else:   
            OWGraph.onMouseMoved(self, e)
            
            
    def onMousePressed(self, e):        
        if self.state == BROWSE_RECTANGLE or self.state == BROWSE_CIRCLE:   
            self.event(e)            
        else:
            OWGraph.onMousePressed(self, e)
            
    def onMouseReleased(self, e):
        
        if self.state == BROWSE_RECTANGLE or self.state == BROWSE_CIRCLE:            
            self.event(e)            
        else:
            OWGraph.onMouseReleased(self, e)
            
    def createCurve(self, x, y, circle = 0):
        if not circle:
            self.browseCurve.setData([x - self.radius, x + self.radius, x + self.radius, x - self.radius, x - self.radius], [y - self.radius, y - self.radius, y + self.radius, y + self.radius, y - self.radius])
        else:
            xDataU = arange(x - self.radius + 0.0002, x + self.radius - 0.0002, 0.0001).tolist()
            xDataD = xDataU[:]
            xDataD.reverse()
            yDataU = [(y  + sqrt(self.radius*self.radius - (t - x)*(t - x))) for t in xDataU]
            yDataD = [(y  - sqrt(self.radius*self.radius - (t - x)*(t - x))) for t in xDataD]
            xDataU.extend(xDataD)
            yDataU.extend(yDataD)
            self.browseCurve.setData(xDataU, yDataU)
            
    def activateZooming(self):
##        self.browseButton.setOn(0)
##        self.browseButtonCircle.setOn(0)
        self.__backToZoom()
        self.state = ZOOMING
        if self.tempSelectionCurve: self.removeLastSelection()

    def activateRectangleSelection(self):
##        self.browseButton.setOn(0)
##        self.browseButtonCircle.setOn(0)
        self.__backToZoom()
        self.state = SELECT_RECTANGLE
        if self.tempSelectionCurve: self.removeLastSelection()

    def activatePolygonSelection(self):
##        self.browseButton.setOn(0)
##        self.browseButtonCircle.setOn(0)
        self.__backToZoom()
        self.state = SELECT_POLYGON
        if self.tempSelectionCurve: self.removeLastSelection()       

    def _sort(self, x, y):
        return int(sign((y[1] - x[1] and [y[1] - x[1]] or [x[0] - y[0]])[0]))
    def addMarkers(self, cor, x, y, r, bold = 0):
        if not len(cor):
            return

        cor.sort(self._sort)
        
        top = y + r
        top = self.transform(QwtPlot.yLeft, top)
        left = x - r
##        left = self.transform(QwtPlot.xBottom, left) - 35
##        left = self.invTransform(QwtPlot.xBottom, left) 
        right = x + r
##        right = self.transform(QwtPlot.xBottom, right) + 20
##        right = self.invTransform(QwtPlot.xBottom, right)
        posX = x
        posY = y
        topR = topL = top
        
        newMark = []
        points = zip(range(len(cor)), cor)
        #sort using height
        points.sort(cmp = lambda x,y: -cmp(x[1][1], y[1][1]))
        prevY = points[0][1][1]
        i = 1

#        while i <= len(points) - 1:
#            y = points[i][1][1]
#            if prevY - y < 10 and points[i-1][1][0] < points[i][1][0]:
#                t = points[i]
#                points[i] = points[i-1]
#                points[i-1] = t            
#            i = i + 1                
                
        
        for i, (x, y, text) in points:
            side = left
            if not text: continue
            print right, left
            if x < posX:
                #pokusaj lijevo
                #if self.checkPerc(left, len(text)) > 0:
                if self.place(left, len(text), 'left') == True:
                    newMark.append((left, self.invTransform(QwtPlot.yLeft, topL), text, Qt.AlignLeft, x, y))
                    topL = topL + self.labelSize
                else:
                    newMark.append((right, self.invTransform(QwtPlot.yLeft, topR), text, Qt.AlignRight, x, y))
                    topR = topR + self.labelSize
            else:
                #pokusaj desno
                #if self.checkPerc(right, len(text)) < 70:
                if self.place(right, len(text), 'right') == True:
                    newMark.append((right, self.invTransform(QwtPlot.yLeft, topR), text, Qt.AlignRight, x, y))
                    topR = topR + self.labelSize
                else:                    
                    newMark.append((left, self.invTransform(QwtPlot.yLeft, topL), text, Qt.AlignLeft, x, y))
                    topL = topL + self.labelSize
                
#            if not (i & 1):
#                if self.checkPerc(left) > 0:
#                        newMark.append((left, self.invTransform(QwtPlot.yLeft, top), text, Qt.AlignLeft, x, y))
#                else:
#                    newMark.append((right, self.invTransform(QwtPlot.yLeft, top), text, Qt.AlignRight, x, y))
#                    top = top + 10                    
#            else:
#                if self.checkPerc(right) < 70:
#                    newMark.append((right, self.invTransform(QwtPlot.yLeft, top), text, Qt.AlignRight, x, y))
#                else:
#                    top = top + 10
#                    newMark.append((left, self.invTransform(QwtPlot.yLeft, top), text, Qt.AlignLeft, x, y))
#                top = top + 10
        again = True
        swapCounter = 0
        while again:
            #don't take too long
            if swapCounter > 100:
                break
            again = False
            prevIndL = prevIndR = -1
            topR = topL = top
            #prevXL = prevXR = 0
            i = 0

            while i <= len(newMark) - 1:
                if newMark[i][3] == Qt.AlignLeft:                    
                    #compute line parameters
                    if prevIndL == -1:
                        prevIndL = i
                        #topL += self.labelSize
                        i += 1
                        continue
                    #print 'looking %s and %s' %(newMark[i][2], newMark[prevIndL][2])
                    k1 = (newMark[i][1] - newMark[i][5]) / (newMark[i][0] - newMark[i][4])
                    l1 = -k1 * newMark[i][4] + newMark[i][5]
                    k2 = (newMark[prevIndL][1] - newMark[prevIndL][5]) / (newMark[prevIndL][0] - newMark[prevIndL][4])
                    l2 = -k2 * newMark[prevIndL][4] + newMark[prevIndL][5]                                    
                    if k1 == k2:
                        i += 1
                        continue
                    intersection = (l2 - l1) / (k2 - k1)
                    intersection = -intersection
                    #print intersection, left, min(newMark[i][4], newMark[prevIndL][4])
                    if intersection > left and intersection < min(newMark[i][4], newMark[prevIndL][4]):
                        #swap labels
                        #print "swapping %s and %s " %(newMark[i][2], newMark[prevIndL][2])
                        #t = (left, self.invTransform(QwtPlot.yLeft, topL + self.labelSize), newMark[i][2], newMark[i][3], newMark[i][4], newMark[i][5])
                        t = (left, newMark[prevIndL][1], newMark[i][2], newMark[i][3], newMark[i][4], newMark[i][5])
                        #newMark[i] = (left, self.invTransform(QwtPlot.yLeft, topL), newMark[prevIndL][2], newMark[prevIndL][3], newMark[prevIndL][4], newMark[prevIndL][5])
                        newMark[i] = (left, newMark[i][1], newMark[prevIndL][2], newMark[prevIndL][3], newMark[prevIndL][4], newMark[prevIndL][5])
                        newMark[prevIndL] = t
                        again = True
                        swapCounter += 1
                    prevIndL = i
                    topL += self.labelSize
                        
                if newMark[i][3] == Qt.AlignRight:
                    #compute line parameters
                    if prevIndR == -1:
                        prevIndR = i
                        #topR += self.labelSize
                        i += 1
                        continue
                    #print 'looking %s and %s' %(newMark[i][2], newMark[prevIndR][2])
                    k1 = (newMark[i][1] - newMark[i][5]) / (newMark[i][0] - newMark[i][4])
                    l1 = -k1 * newMark[i][4] + newMark[i][5]
                    k2 = (newMark[prevIndR][1] - newMark[prevIndR][5]) / (newMark[prevIndR][0] - newMark[prevIndR][4])
                    l2 = -k2 * newMark[prevIndR][4] + newMark[prevIndR][5]                                    
                    if k1 == k2 or newMark[i][4] == newMark[prevIndR][4]:
                        i += 1
                        continue
                    intersection = (l2 - l1) / (k2 - k1)
                    #print intersection, right, min(newMark[i][4], newMark[prevIndR][4])
                    intersection = -intersection
                    if intersection < right and intersection > max(newMark[i][4], newMark[prevIndR][4]):
                        #swap labels
                        t = (right, newMark[prevIndR][1], newMark[i][2], newMark[i][3], newMark[i][4], newMark[i][5])
                        newMark[i] = (right, newMark[i][1], newMark[prevIndR][2], newMark[prevIndR][3], newMark[prevIndR][4], newMark[prevIndR][5])
                        newMark[prevIndR] = t
                        again = True
                        swapCounter += 1
                    prevIndR = i
                    topR += self.labelSize
                i = i + 1


##        while i <= len(newMark) - 1:
##            y = newMark[i][1]
##            if newMark[i][3] == Qt.AlignLeft:
##                if abs(prevYL - y) < abs(prevXL - newMark[i][0]):
##                    t = newMark[i]
##                    newMark[i] = newMark[prevIndL]
##                    newMark[prevIndL] = t
##                prevYL = y
##                prevXL = newMark[i][0]
##                prevIndL = i
##            if  newMark[i][3] == Qt.AlignRight:
##                if abs(prevYR - y) < abs(prevXR - newMark[i][0]):
##                    t = newMark[i]
##                    newMark[i] = newMark[prevIndR]
##                    newMark[prevIndR] = t
##                prevYR = y
##                prevXR = newMark[i][0]
##                prevIndR = i                
##            i = i + 1  
    

            
        for x, y, text, al, x1, y1 in newMark:
            self.addMarker(text, x, y, alignment = al, color = QColor(255,0,0), size = self.labelSize)
            self.markLines.append(self.addCurve("", QColor("black"), QColor("black"), 1, QwtCurve.Lines, xData = [x, x1], yData = [y, y1] ))

            
##    def checkPerc(self, x, textLen):
##        div = self.axisScale(QwtPlot.xBottom)
##        if x - textLen < div.lBound():
##            return -1
##        elif x + textLen > div.hBound():
##            return 101
##        else:
##            return (x - div.lBound()) / (div.hBound() - div.lBound())

    def place(self, x, textLen, prefered):
        """Tries to determine where to place the label. Returns True or False."""
        div = self.axisScale(QwtPlot.xBottom)
        textLen = textLen / 16.
        if prefered == 'left':
            if x - textLen < div.lBound():
                return False
            return True
        else:
            if x + textLen > div.hBound():
                return False
            return True
        
        