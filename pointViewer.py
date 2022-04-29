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
# Template s.o.
# bearbeitet von Antonia Eckert (Matr.-Nr.:1175268)

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from OpenGL.arrays import vbo
import math
from numpy import array

tMat = np.eye(4)
sMat = np.eye(4)
rMat = np.eye(4)

# boundingbox
myVBO = None

# rotation
startP = np.array([0, 0, 0])
actOri = np.identity(4)
angle = 0.0
doRotation = False

# bewegungen
doZoom = False
posChange = False
axis = np.array([0, 1, 0])

# projektion
zentrProj = False
orthoProj = True  # da RenderWindow zuerst mit glOrtho

#schatten
schatten = False
lichtQuelle = [2000, 2000, 2000]
# shadow_width = 1024
# shadow_height = 1024

scaleFactor = 2
figColor = [1.0, 1.0, 1.0]


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

        # boundBOX ist Fenstergroesse (?)
        self.boundBox = [np.array(list(map(min, list(zip(*vertices))))),
                         np.array(list(map(max, list(zip(*vertices)))))]

        self.c = (self.boundBox[0] + self.boundBox[1]) / 2
        self.scale = 3

    # set scene dependent OpenGL states
    def setOpenGLStates(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)

    # rotation
    def rotate(self, angle, axis):
        c, mc = math.cos(angle), 1-math.cos(angle)
        s = np.sin(angle)
        l = np.sqrt(np.dot(array(axis), array(axis)))

        if l == 0:
            return np.identity(4)

        x, y, z = array(axis)/l
        r = np.matrix(
            [
                [x*x*mc+c, x*y*mc-z*s, x*z*mc+y*s, 0],
                [x*y*mc+z*s, y*y*mc+c, y*z*mc-x*s, 0],
                [x*z*mc-y*s, y*z*mc+x*s, z*z*mc+c, 0],
                [0, 0, 0, 1]
            ]
        )
        return r.transpose()

    # def display folie 193
    # jetzt hoffentlich mit schatten
    def display(self):
        global schatten, figColor
        # global shadow_width, shadow_height


        ## Shadow Mapping Versuch
        #
        # glViewport(0, 0, shadow_width, shadow_height)
        # glBindFramebuffer(GL_FRAMEBUFFER, glGenFramebuffers(1))
        # glClear(GL_DEPTH_BUFFER_BIT)
        # # ConfigureShaderAndMatrices()
        # # RenderScene()
        # glBindFramebuffer(GL_FRAMEBUFFER, 0);
        # # 2. then render scene as normal with shadow mapping (using depth map)
        # glViewport(0, 0, self.width, self.height)
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # # ConfigureShaderAndMatrices()
        # glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
        # #  RenderScene()
        #
        ## Shadow Mapping Versuch Ende


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        myVBO.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointer(3, GL_FLOAT, 24, myVBO)
        glNormalPointer(GL_FLOAT, 24, myVBO + 12)

        # jetzt mit schatten (vom letzten semester übernommen)
        if schatten:
            schattenPos = np.matrix(
                [
                    [1.0, 0, 0, 0],
                    [0, 1.0, 0, 0],
                    [0, 0, 1.0, 0],
                    [0, 1.0/-lichtQuelle[1], 0, 0]
                ]
            ).transpose()

            glPushMatrix()
            glTranslatef(0, self.boundBox[0][1], 0)
            glTranslatef(lichtQuelle[0], lichtQuelle[1], lichtQuelle[2])
            glMultMatrixf(schattenPos)
            glTranslatef(-lichtQuelle[0], -lichtQuelle[1], -lichtQuelle[2])
            glTranslatef(0, -self.boundBox[0][1], 0)

            glColor(0.2, 0.2, 0.2)
            glDisable(GL_LIGHTING)
            glDrawArrays(GL_TRIANGLES, 0, len(data))
            glEnable(GL_LIGHTING)
            glPopMatrix()
            glColor(figColor[0], figColor[1], figColor[2])

        glLoadIdentity()
        glColor(figColor[0], figColor[1], figColor[2])

        scale = scaleFactor / max(self.boundBox[1] - self.boundBox[0])
        glScale(scale, scale, scale)
        glTranslate(-self.c[0], -self.c[1], -self.c[2])
        glMultMatrixf(actOri * scene.rotate(angle, axis))
        glDrawArrays(GL_TRIANGLES, 0, len(data))

        myVBO.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)


class RenderWindow:
    """GLFW Rendering window class"""

    def __init__(self, scene):
        # global shadow_width, shadow_height
        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

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

        ## Shadow Mapping Versuch
        #
        # depthMapFBO = glGenFramebuffers(1)
        # texture = glGenTextures(1)
        # glGenFramebuffers(1, depthMapFBO)
        #
        # glGenTextures(1, depthMap)
        # glBindTextures81, depthMap)
        #
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, shadow_width, shadow_height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        #
        # glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
        # glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, texture, 0)
        # glDrawBuffer(GL_NONE)
        # glReadBuffer(GL_NONE)
        # glBindFramebuffer(GL_FRAMEBUFFER, 0)
        #
        ## Shadow Mapping Versuch Ende

        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glOrtho(-1.5, 1.5, -1.5 * self.height / self.width, 1.5*self.height/self.width, -10, 10)

        glMatrixMode(GL_MODELVIEW)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        #glfw.set_scroll_callback(self.window, self.zooming)
        glfw.set_cursor_pos_callback(self.window, self.onMouseMotion)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)
        #glfw.set_window_content_scale_callback(self.window, self.winResize)

        # create scene
        self.scene = scene  # Scene(self.width, self.height)
        self.scene.setOpenGLStates()

        # exit flag
        self.exitNow = False

        # animation flags
        self.forward_animation = False
        self.backward_animation = False

    # rotation
    def projectOnSphere(self, x, y, r):
        x, y = x-self.width/2.0, self.height/2.0-y
        a = min(r*r, x**2 + y**2)
        z = math.sqrt(r*r - a)
        l = math.sqrt(x**2 + y**2 + z**2)
        return x/l, y/l, z/l

    # button left: rotation, button right: verschieben, button middle: zoom
    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)

        global startP, actOri, angle, doRotation, doZoom, yStart, posChange

        r = min(self.width, self.height)/2

        if button == glfw.MOUSE_BUTTON_LEFT:
            x, y = glfw.get_cursor_pos(win)
            if action == glfw.PRESS:
                doRotation = True
                startP = self.projectOnSphere(x, y, r)
            if action == glfw.RELEASE:
                doRotation = False
                actOri = actOri * scene.rotate(angle, axis)
                angle = 0

        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                posChange = True
            if action == glfw.RELEASE:
                posChange = False

        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                print("mittlerer Button")
                x, yStart = glfw.get_cursor_pos(win)
                doZoom = True
            if action == glfw.RELEASE:
                self.zooming(win, yStart)
                doZoom = False

    # zoom
    def zooming(self, win, y):
        global scaleFactor
        curX, curY = glfw.get_cursor_pos(win)
        diffY = y - curY
        factor = scaleFactor + float(diffY/15)
        if factor <= 0:
            factor = 0.1
        scaleFactor = factor

    # farben aendern, projektionswechsel, schatten anzeigen
    def onKeyboard(self, win, key, scancode, action, mods):
        global zentrProj, orthoProj, schatten, figColor
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # press ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True

            # Hintergrund Rot
            if key == glfw.KEY_R:
                glClearColor(1, 0, 0, 0)
            # Figur Rot
            if key == glfw.KEY_E:
                figColor = (1, 0, 0, 0)

            # Hintergrund Weiss
            if key == glfw.KEY_W:
                glClearColor(1, 1, 1, 0)
            # Figur Weiss
            if key == glfw.KEY_Q:
                figColor = (1, 1, 1, 0)

            #Hintergrund Blau
            if key == glfw.KEY_B:
                glClearColor(0, 0, 1, 0)
            # Figur Blau
            if key == glfw.KEY_V:
                figColor = (0, 0, 1, 0)

            #Hinergrund Schwarz
            if key == glfw.KEY_S:
                glClearColor(0, 0, 0, 0)
            # Figur Schwarz
            if key == glfw.KEY_A:
                figColor = (0, 0, 0, 0)

            #Hintergrund Gelb
            if key == glfw.KEY_G:
                glClearColor(1, 1, 0, 0)
            # Figur Gelb
            if key == glfw.KEY_F:
                figColor = (1, 1, 0, 0)

            # Projektionswechsel
            # ZentralProjektion
            if key == glfw.KEY_P:
                if zentrProj == False:
                    orthoProj = False
                    zentrProj = True
                    self.projec()

            # OrthogonalProjektion
            if key == glfw.KEY_O:
                if orthoProj == False:
                    zentrProj = False
                    orthoProj = True
                    self.projec()

            # Schattenanzeige
            if key == glfw.KEY_0:
                schatten = True
            if key == glfw.KEY_9:
                schatten = False

    # Projektionswechsel
    def projec(self):
        global orthoProj, zentrProj

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.height < self.width:
            aspect = self.aspect
            if orthoProj:
                glOrtho(-1.5, 1.5, -1.5 * self.height / self.width, 1.5 * self.height / self.width, -10, 10)
            if zentrProj:
                gluPerspective(45, aspect, 1, 10)
                gluLookAt(0, 0, 3, 0, 0, 0, 0, 1, 0)
        else:
            aspect = self.height/self.width
            if orthoProj:
                glOrtho(-1.5 * self.width / self.height, 1.5 * self.width / self.height, -1.5, 1.5, -10, 10)
            if zentrProj:
                gluPerspective(45, aspect, 1, 10)
                gluLookAt(0, 0, 3, 0, 0, 0, 0, 1, 0)

        glMatrixMode(GL_MODELVIEW)

    def winResize(self, win, xScale, yScale):
        if yScale == 0:
            yScale = 1
        glfw.set_interface_scale(xScale, yScale)

    def onSize(self, win, width, height):
        # print("onsize: ", win, width, height)
        if height == 0:
            height = 1
        self.width = width
        self.height = height
        self.aspect = width / float(height)
        glViewport(0, 0, self.width, self.height)
        self.projec()
        # glMatrixMode(GL_PROJECTION)
        # glLoadIdentity()
        # glMatrixMode(GL_MODELVIEW)

    def onMouseMotion(self, win, x, y):
        global angle, axis, scaleFactor, posChange, doRotation
        if doRotation:
            r = min(self.width, self.height)/2.0
            moveP = self.projectOnSphere(x, y, r)
            angle = math.acos(np.dot(startP, moveP))
            axis = np.cross(startP, moveP)

        if posChange:
            self.scene.c[0] = 0.002*((self.width/2) - x)
            self.scene.c[1] = 0.002*(y - (self.height/2))

    def mousebuttonpressend(self, button, state, x, y):
        global startP, actOri, angle, doRotation
        r = min(self.width, self.height)/2.0
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                doRotation = True
                startP = self.projectOnSphere(x, y, r)
            if state == GLUT_UP:
                doRotation = False
                actOri = actOri*self.rotate(angle, axis)
                angle = 0

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
                # self.scene.render()
                self.scene.display()
                # swap front and back buffer
                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()

#obj-Datei Parser
def readobj(path):
    vertices = []
    faces = []
    normals = []
    file = open(path)
    for line in file:
        if line.startswith("#"):
            continue
        if line.startswith("vn"):
            norm = line.split()
            normals.append([float(norm[1]), float(norm[2]), float(norm[3])])
        elif line.startswith("v"):
            koord = line.split()
            vertices.append([float(koord[1]), float(koord[2]), float(koord[3])])
        if line.startswith("f"):
            split = line.split()
            face = split[1:]
            face = [f.split("/") for f in face]
            faces.append(face)

    npData = np.array(vertices), np.array(faces), np.array(normals)
    return npData

# call main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("pointViewer.py pointset.raw")
        sys.exit(-1)

    # Gebrauchsanleitung
    print("Gebrauchsanleitung \n"
          "Maustasten (gedrueckt halten): \n"
          "- rechte Taste: Drehen\n"
          "- mittlere Taste: Zoomen\n"
          "- linke Taste: Verschieben\n"
          "Tastatur:\n"
          "- 0/9: Schatten an/aus\n"
          "- o/p: Wechsel zwischen OrthogonalPojektion/ZentralProjektion\n"
          "- w/q: weisse(r) Hintergrund/Figur\n"
          "- r/e: rote(r) Hintergrund/Figur\n"
          "- s/a: schwarze(r) Hintergrund/Figur\n"
          "- g/f: gelbe(r) Hintergrund/Figur\n"
          "- b/v: blaue(r) Hintergrund/Figur")

    # set size of render viewport
    width, height = 640, 480

    data = []

    #load obj file containing vertices, normals, faces
    vertices, faces, normals = readobj(f"{sys.argv[1]}")

    print("FACE: ", len(faces[0][0]))

    if len(faces[0][0]) == 1:
        for face in faces:
            a_vert = np.array(vertices[int(face[0])-1])
            b_vert = np.array(vertices[int(face[1])-1])
            c_vert = np.array(vertices[int(face[2])-1])
            u = b_vert - a_vert
            v = c_vert - a_vert
            un_normalV = np.cross(np.array(u), np.array(v))
            normalV = un_normalV / np.linalg.norm(un_normalV)

            data.append(a_vert)
            data.append(normalV)
            data.append(b_vert)
            data.append(normalV)
            data.append(c_vert)
            data.append(normalV)
    else:
        for face in faces:
            for vertex in face:
                vn = int(vertex[0])-1
                nn = int(vertex[2])-1
                data.append(vertices[vn])
                data.append(normals[nn])

    myVBO = vbo.VBO(array(data, 'f'))

    # instantiate a scene
    scene = Scene(width, height, vertices, "pointViewer")

    rw = RenderWindow(scene)
    rw.run()
