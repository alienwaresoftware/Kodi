
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_SELECT_ITEM = 7

class SpinControl(object):
    options = [];
    upBtn = None;
    downBtn = None;
    label = None;
    window = None;
    selectedIndex = 0;
    previousSelectedIndex = 0;
    
    def __init__(self, window, containerId, labelId, selectionChanged, onUpCallback, onDownCallback, options, leftArrowId, rightArrowId, leftArrowFocusId, rightArrowFocusId,isRotate=False):
        self.options = options;
        self.window = window;
        self.selectionChangedcallback = selectionChanged
        self.container = window.getControl(containerId);
        self.label = window.getControl(labelId);
        self.isRotate = isRotate;
        self.leftArrow = window.getControl(leftArrowId)
        self.rightArrow = window.getControl(rightArrowId)
        self.leftArrowFocus = window.getControl(leftArrowFocusId)
        self.rightArrowFocus = window.getControl(rightArrowFocusId)
        self.leftArrowFocusWidth = self.leftArrowFocus.getWidth()
        self.rightArrowFocusWidth = self.rightArrowFocus.getWidth()
        self.onUpCallback = onUpCallback
        self.onDownCallback = onDownCallback
        self.leftArrowEnabled = True;
        self.rightArrowEnabled = True;
        
        self.setSelected();
        
        return;
    
    def setSelected(self, setFocus=False):
        length = self.options.__len__();
        if self.selectedIndex < 0:
            self.selectedIndex = length - 1;
            self.previousSelectedIndex = 0;
        if self.selectedIndex > length - 1:
            self.selectedIndex = 0;
            self.previousSelectedIndex = length - 1;

        self.label.setLabel(unicode(self.options[self.selectedIndex]));

        #print "length {0}, selectedIndex  {1}".format(length,  self.selectedIndex)

        self.leftArrowEnabled = True;
        self.leftArrowFocus.setWidth(self.leftArrowFocusWidth);
        self.rightArrowEnabled = True;
        self.rightArrowFocus.setWidth(self.rightArrowFocusWidth);
        self.container.setEnabled(True);
        
        if length == 1:
            self.leftArrow.setEnabled(False);
            self.rightArrow.setEnabled(False);
            self.leftArrowEnabled = False;
            self.leftArrowFocus.setWidth(self.leftArrowFocusWidth + 30);
            self.rightArrowEnabled = False;
            self.rightArrowFocus.setWidth(self.rightArrowFocusWidth + 30);
            self.container.setEnabled(False);
        elif self.selectedIndex == 0:
            if setFocus:
                self.window.setFocus(self.rightArrow);
            self.leftArrow.setEnabled(False);
            self.rightArrow.setEnabled(True);
            self.leftArrowEnabled = False;
            self.leftArrowFocus.setWidth(self.leftArrowFocusWidth + 30);
        elif self.selectedIndex == length - 1:
            if setFocus:
                self.window.setFocus(self.leftArrow);
            self.leftArrow.setEnabled(True);
            self.rightArrow.setEnabled(False);
            self.rightArrowEnabled = False;
            self.rightArrowFocus.setWidth(self.rightArrowFocusWidth + 30);
        else:
            self.leftArrow.setEnabled(True);
            self.rightArrow.setEnabled(True);

        if self.selectionChangedcallback is not None:
            self.selectionChangedcallback(self.selectedIndex,self.options[self.selectedIndex],self.previousSelectedIndex,self.options[self.previousSelectedIndex])
        return;
    
    def forwardInput(self, actionid, controlId):
        if actionid == ACTION_SELECT_ITEM:
            length = self.options.__len__();
            if controlId == 0:
                focusedItem = self.window.getFocus();
            else:
                focusedItem = self.window.getControl(controlId)

            if focusedItem == self.leftArrow:
                if not self.isRotate and self.selectedIndex == 0:
                    return True;
                self.previousSelectedIndex = self.selectedIndex;
                self.selectedIndex -= 1;
                self.setSelected(True);
            elif focusedItem == self.rightArrow:
                #print "downBtn selcted"
                if not self.isRotate and self.selectedIndex == length - 1:
                    return True;
                self.previousSelectedIndex = self.selectedIndex;
                self.selectedIndex += 1;
                self.setSelected(True);
        elif actionid == ACTION_MOVE_UP:
            focusedItem = self.window.getFocus();
            if focusedItem == self.leftArrow or focusedItem == self.rightArrow:
                if self.onUpCallback is not None:
                    #print "calling upCallback {0}".format(focusedItem.getId())
                    self.onUpCallback(focusedItem)
                    return True;
        elif actionid == ACTION_MOVE_DOWN:
            focusedItem = self.window.getFocus();
            if focusedItem == self.leftArrow or focusedItem == self.rightArrow:
                if self.onDownCallback is not None:
                    #print "calling DownCallback"
                    self.onDownCallback(focusedItem)
                    return True;
        return False

    def setFocus(self, isLeft):
        if isLeft:
            #print 0
            if self.leftArrowEnabled:
                self.window.setFocus(self.leftArrow)
            elif self.rightArrowEnabled:
                self.window.setFocus(self.rightArrow)
        else:
            #print 1
            if self.rightArrowEnabled:
                self.window.setFocus(self.rightArrow)
            elif self.leftArrowEnabled:
                self.window.setFocus(self.leftArrow)

    def updateItems(self, items):
        self.options = items;
        self.previousSelectedIndex = 0;
        self.selectedIndex = 0;
        self.setSelected();

    def selectText(self, selelectedText):
        self.selectedIndex = self.options.index(selelectedText)
        self.setSelected();

    def selectSelectedIndex(self, selectedIndex):
        self.selectedIndex = selectedIndex
        self.setSelected();
    
    def getText(self):
        return self.options[self.selectedIndex];

    def setState(self, isenable):
        self.container.setEnabled(isenable)
        pass

    def getSelectedIndex(self):
        return self.selectedIndex;
