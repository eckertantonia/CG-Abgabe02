"""
/*******************************************************************************
 *
 *            #, #,         CCCCCC  VV    VV MM      MM RRRRRRR
 *           %  %(  #%%#   CC    CC VV    VV MMM    MMM RR    RR
 *           %    %## #    CC        V    V  MM M  M MM RR    RR
 *            ,%      %    CC        VV  VV  MM  MM  MM RRRRRR
 *            (%      %,   CC    CC   VVVV   MM      MM RR   RR
 *              #%    %*    CCCCCC     VV    MM      MM RR    RR
 *             .%    %/
 *                (%.      Computer Vision & Mixed Reality Group
 *
 ******************************************************************************/
/**          @copyright:   Hochschule RheinMain,
 *                         University of Applied Sciences
 *              @author:   Prof. Dr. Ulrich Schwanecke
 *             @version:   0.9
 *                @date:   03.06.2019
 ******************************************************************************/
/**         RenderWindow.py
 *
 *          Simple Python OpenGL program that uses PyOpenGL + GLFW to get an
 *          OpenGL 3.2 context and display some 2D animation.
 ****
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

tMat = np.eye(4)
sMat = np.eye(4)
rMat = np.eye(4)


class Scene:
    """ OpenGL 2D scene class """

    # initialization
    def __init__(self, width, height,
                 points=[np.array([0, 0, 0, 1])],
                 scenetitle="2D Scene"):
        # time
        self.t = 0
        self.dt = 0.001
        self.scenetitle = scenetitle
        self.pointsize = 7
        self.linewidth = 3
        self.width = width
        self.height = height
        self.points = points
        self.animate = False
        self.alpha = 0  # rotation angle around x-axis
        self.beta = 0  # rotation angle around y-axis
        self.gamma = 0  # rotation angle around z-axis

    # set scene dependent OpenGL states
    def setOpenGLStates(self):
        glPointSize(self.pointsize)
        glLineWidth(self.linewidth)

    # animation
    def animation(self):
        if self.animate:
            self.beta += 10
            if self.beta > 360:
                self.beta = 0

                # render

    def render(self):
        # maybe animate    
        self.animation()

        # TODO : 
        # - define model view transformation matrices
        # - define projection matrix
        # - combine matrices to model view projection matrix

        # set color to blue
        glColor(0.0, 0.0, 1.0)

        # render points
        glBegin(GL_POINTS)
        for p in self.points:
            # TODO : 
            # - apply model view projection matrix to each point
            # - transform from homogeneous to euclidian point coordinates
            # - perform view port transformation

            # render point
            glVertex4fv(p)
        glEnd()


class RenderWindow:
    """GLFW Rendering window class"""

    def __init__(self, scene):

        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        # version hints
        # glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        # glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 100

        # make a window
        self.width, self.height = scene.width, scene.height
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, scene.scenetitle, None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glOrtho(0, width, 0, height, -1000, 1000)

        glMatrixMode(GL_MODELVIEW)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)

        # create scene
        self.scene = scene  # Scene(self.width, self.height)
        self.scene.setOpenGLStates()

        # exit flag
        self.exitNow = False

        # animation flags
        self.forward_animation = False
        self.backward_animation = False

    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)

    def onKeyboard(self, win, key, scancode, action, mods):
        # print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # press ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            # press 'A' to toggle animation
            if key == glfw.KEY_A:
                self.scene.animate = not self.scene.animate
            if mods == glfw.MOD_SHIFT:  # upper case keys
                if key == 88:  # glfw.KEY_X:
                    # increase angle alpha (rotation around x-axis)
                    self.scene.alpha += 10
                if key == 90:  # glfw.KEY_Y:
                    # increase angle beta (rotation around y-axis)
                    self.scene.beta += 10
                if key == 89:  # glfw.KEY_Z:
                    # increase angle gamma (rotation around z-axis)
                    self.scene.gamma += 10
            else:  # lower case keys
                if key == 88:  # glfw.KEY_X:
                    # decrease angle alpha (rotation around x-axis)
                    self.scene.alpha -= 10
                if key == 90:  # glfw.KEY_Y:
                    # decrease angle beta (rotation around y-axis)
                    self.scene.beta -= 10
                if key == 89:  # glfw.KEY_Z:
                    # decrease angle gamma (rotation around z-axis)
                    self.scene.gamma -= 10

    def onSize(self, win, width, height):
        print("onsize: ", win, width, height)
        self.width = width
        self.height = height
        self.aspect = width / float(height)
        glViewport(0, 0, self.width, self.height)

    def run(self):
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0 / self.frame_rate:
                # update time
                t = currT
                # clear viewport
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                # render scene
                self.scene.render()
                # swap front and back buffer
                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()


# call main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("pointViewer.py pointset.raw")
        print("'A' or 'a' to toggle animation")
        print("'ESC' to quit")
        print("'x' : rotate the pointset clockwise around the x-axis ")
        print("'X' : rotate the pointset counter clockwise around the x-axis ")
        print("'y' : rotate the pointset clockwise around the y-axis ")
        print("'Y' : rotate the pointset counter clockwise around the y-axis ")
        print("'z' : rotate the pointset clockwise around the z-axis ")
        print("'Z' : rotate the pointset counter clockwise around the z-axis ")
        sys.exit(-1)

    # set size of render viewport
    width, height = 640, 480

    vertices = []
    # TODO :
    # - read in points

    # TODO :
    # - calculate bounding box of point set
    # - determine matrix for translation of center of bounding box to origin
    # - determine matrix to scale to [-1,1]^2

    # instantiate a scene
    scene = Scene(width, height, vertices, "pointViewer Template")

    rw = RenderWindow(scene)
    rw.run()