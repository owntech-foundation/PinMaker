from pysvg.parser import *

#Ugly copy paste
class Mask(BaseElement, CoreAttrib, ConditionalAttrib, StyleAttrib, ExternalAttrib, PresentationAttributes_All, GraphicalEventsAttrib):
    """
    Class representing the mask element of an svg doc.
    """
    def __init__(self, **kwargs):
        BaseElement.__init__(self, 'mask')
        self.setKWARGS(**kwargs)
    
    def set_transform(self, transform):
        self._attributes['transform'] = transform
    def get_transform(self):
        return self._attributes.get('transform')   

def build(node_, object):
    attrs = node_.attributes
    if attrs != None:
        setAttributes(attrs, object)
    for child_ in node_.childNodes:
        nodeName_ = child_.nodeName.split(':')[-1]
        if child_.nodeType == Node.ELEMENT_NODE:
            try:
                capitalLetter = nodeName_[0].upper()
                objectinstance=eval(capitalLetter+nodeName_[1:]) ()                
            except:
                print('no class for: '+nodeName_)
                continue
            object.addElement(build(child_,objectinstance))
        elif child_.nodeType == Node.TEXT_NODE:
            #print "TextNode:"+child_.nodeValue
            #if child_.nodeValue.startswith('\n'):
            #    print "TextNode starts with return:"+child_.nodeValue
            #else:
#            print "TextNode is:"+child_.nodeValue
            #object.setTextContent(child_.nodeValue)
            if child_.nodeValue != None and child_.nodeValue.strip() != '':
                # print(len(child_.nodeValue))
                object.appendTextContent(child_.nodeValue)
        elif child_.nodeType == Node.CDATA_SECTION_NODE:  
            object.appendTextContent('<![CDATA['+child_.nodeValue+']]>')          
        elif child_.nodeType == Node.COMMENT_NODE:  
            object.appendTextContent('<!-- '+child_.nodeValue+' -->')          
        else:
            print("Some node:"+nodeName_+" value: "+child_.nodeValue)
    return object

#TODO: packageprefix ?
def parse(inFileName):
    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement
    rootObj = Svg()
    build(rootNode,rootObj)
    # Enable Python to collect the space used by the DOM.
    doc = None
    #print rootObj.getXML()
    return rootObj

