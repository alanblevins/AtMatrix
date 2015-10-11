"""
Copyright (c) 2015 Alan Blevins

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""
AtMatrix utility functions and simple demo that renders a small
rigidy body simulation by applying externally-generated transforms.
"""

import sys, os

# Substitute the path to your Arnold SDK install
sys.path.append("C:\\lib\\arnold\\4.2.10.0\\python")

from arnold import *

START = 1
END = 140

def set_node_xform(node, transform):
    """Set an AtNode matrix from one or more transform arrays.
    
    Set a node transform from a 16-entry python array,
    or an array of several transform arrays if you want
    motion blur (max 15 samples)
    
    Args:
        node (AtNode): Node to set 'matrix' attribute
        transform (list(float), or list(list(float))): List, or list of lists
            containing 16 entries representating a transform matrix.
    """
    list_size = len(transform)
    if list_size < 16:
        xform_array = AiArrayAllocate(1, list_size, AI_TYPE_MATRIX)
        for i in range(list_size):
            AiArraySetMtx(xform_array, i, xform_to_matrix(transform[i]))
        AiNodeSetArray(node, "matrix", xform_array)      
        AiMsgInfo(b"Setting {0} time samples for {1}".format(
            list_size,
            AiNodeGetName(node)
            ))
    else:
        AiNodeSetMatrix(node, "matrix", xform_to_matrix(transform))

        
def xform_to_matrix(transform16):
    """Make a new AtMatrix from an array
    
    Create an AtMatrix and set its values from 
    a transform array of 16 entries.
    
    Args:
        transform16 (list(float)): 16-entry python array
        
    Returns:
        AtMatrix: New, initialized matrix
    """
    transform = AtMatrix()
    for y in range(4):
        for x in range(4):
            transform.__setattr__("a%d%d"%(y, x), transform16[y*4+x])    
    return transform

if __name__ == "__main__":
    # Read the transforms dumped from Maya
    mats_file = open("mats.txt", "r")
    as_txt = mats_file.read()
    mats_file.close()

    lines = as_txt.split("\n")
    mats = []
    for line in lines:
        mats.append([float(i) for i in line.split()])

    # Warm up Arnold
    AiBegin()

    # Show EVERYTING in the log
    AiMsgSetConsoleFlags(AI_LOG_ALL)
    
    # Read in the scene file
    AiASSLoad("cube_bounce.ass")

    cube = AiNodeLookUpByName("cube")
    driver = AiNodeLookUpByName("exr")

    for frame in range(START, END):
        # Set the file output name per-frame
        # Renders in place in 'renders' subdir
        fileName = "renders/bounce.%03d.exr" % frame
        AiNodeSetStr(driver, "filename", fileName)
        
        # Apply the transform to the cube for this frame (w/ mblur)
        xforms = [mats[frame], mats[frame+1]]
        set_node_xform(cube, xforms)
        
        # Render this frame
        result = AiRender()
        if result != AI_SUCCESS:
            AiMsgError(b"Quitting because I failed somehow")
            break

    # All done, tell Arnold to quit
    AiEnd()
