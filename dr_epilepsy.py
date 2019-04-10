# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    'name': 'Dr. Epilepsy',
    'author': 'Nathan Craddock, Bassam Kurdali, Dalai Felinto, Nathan Letwory, inspired by Bastian Salmela',
    'version': (1, 1, 0),
    "blender": (2, 80, 0),
    "api": 39104,
    'location': 'View3D > OSKey-D',
    'description': 'Dr. Epililepsy will melt your brain',
    'wiki_url': '',
    'tracker_url': '',
    'category': '3D View'
}

import bpy
import time
from random import random
from mathutils import Color
from math import sin
import aud
import math
import bgl


def parseNotes(notes, bpm, basefreq, rate = 44100,
               notechars = "XXXCXDXEFXGXAXHcXdXefXgXaXhp"):
    pos = 0
    sound = None
    fadelength = 60/bpm/10
    halfchars = "#b"
    durationchars = "2345678"
 
    while pos < len(notes):
        char = notes[pos]
        mod = None
        dur = 1
        pos += 1
        while pos < len(notes) and notes[pos] not in notechars:
            if notes[pos] in halfchars:
                mod = notes[pos]
            elif notes[pos] in durationchars:
                dur = notes[pos]
            pos += 1
 
        freq = notechars.find(char)
        if mod == '#':
            freq += 1
        elif mod == 'b':
            freq -= 1
 
        freq = math.pow(2, freq/12)*basefreq
        length = float(dur)*60/bpm
 
        snd = aud.Sound.sine(freq, rate)
        if char == 'p':
            snd = snd.volume(0)
        else:
            snd = snd.square(freq)
        snd = snd.limit(0, length)
        snd = snd.fadein(0, fadelength)
        snd = snd.fadeout(length - fadelength, fadelength)
 
        if sound:
            sound = sound.join(snd)
        else:
            sound = snd
    return sound
 
def tetris(bpm = 300, freq = 220, rate = 44100):
    notes = "e2Hcd2cH A2Ace2dc H3cd2e2 c2A2A4 pd2fa2gf e3ce2dc H2Hcd2e2 c2A2A2p2"
    s11 = parseNotes(notes, bpm, freq, rate)
 
    notes = "e4c4 d4H4 c4A4 G#4p4 e4c4 d4H4 A2c2a4 g#4p4"
    s12 = parseNotes(notes, bpm, freq, rate)
 
    notes = "EeEeEeEe AaAaAaAa AbabAbabAbabAbab AaAaAAHC DdDdDdDd CcCcCcCc HhHhHhHh AaAaA2p2"
    s21 = parseNotes(notes, bpm, freq, rate, notechars = "AXHCXDXEFXGXaXhcXdXefXgXp")
 
    notes = "aeaeaeae g#dg#dg#dg#d aeaeaeae g#dg#dg#2p2 aeaeaeae g#dg#dg#dg#d aeaeaeae g#dg#dg#2p2"
    s22 = parseNotes(notes, bpm, freq/2, rate)
 
    return s11.join(s12).join(s11).volume(0.5).mix(s21.join(s22).join(s21).volume(0.3))
 
def play(bpm = 300, freq = 220):
    dev = aud.Device()
    h= dev.play(tetris(bpm, freq, dev.rate))
    h.loop_count = -1
    return h

class BLENDER_OT_dr_epilepsy(bpy.types.Operator):
    '''Makes the UI beautiful while singing a delightful tune to increase productivity.'''
    bl_idname = "wm.drepilepsy"
    bl_label = "Dr Epilepsy"

    _timer = None
    _handle = None
    _pattern =  0b0011001110011001

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            for area in context.window_manager.windows[0].screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.overlay.grid_scale = 3 + 2*sin(4*time.time())
            
            # change theme color, silly!
            theme = context.preferences.themes[0]
            for buttin in dir(theme.user_interface):
                button = getattr(theme.user_interface,buttin)
                if type(button) == bpy.types.ThemeWidgetColors:
                    for element in dir(button):
                        if element in ['outline','item','inner','inner_sel']:
                            elem = getattr(button,element)
                            elem[0] = random()
                            elem[1] = random()
                            elem[2] = random()
            context.preferences.view.ui_scale = 1 + random()*2
            for vb in dir(theme):
                bov = getattr(theme,vb)
                cols = [thing for thing in dir(bov) if type(getattr(bov,thing))==Color]
                for col in cols:
                    color = getattr(bov,col)
                    
                    color.r = random()
                    color.g = random()
                    color.b = random()
                
                if hasattr(bov, "space"):
                    space = bov.space
                    
                    # Color the back of each area
                    if hasattr(space, "back"):
                        back = space.back
                        back.r = random()
                        back.g = random()
                        back.b = random()
                    
                    # Color each part of the space
                    parts = [part for part in dir(space) if type(getattr(space, part)) is bpy.types.bpy_prop_array]
                    for part in parts:
                        color = getattr(space, part)
                        color[0] = random()
                        color[1] = random()
                        color[2] = random()
                    
                    # Color the panels
                    if hasattr(space, "panelcolors"):
                        panel = bov.space.panelcolors
                        parts = [part for part in dir(panel) if type(getattr(panel, part)) is bpy.types.bpy_prop_array]
                        for part in parts:
                            color = getattr(panel, part)
                            color[0] = random()
                            color[1] = random()
                            color[2] = random()

            # Color the 3D View background (an exception)
            background_color = bpy.context.preferences.themes[0].view_3d.space.gradients.high_gradient
            background_color[0] = random()
            background_color[1] = random()
            background_color[2] = random()
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.001, window=context.window)
        self._handle = play()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self._handle.stop()
        return {'CANCELLED'}


def register():
    bpy.utils.register_class(BLENDER_OT_dr_epilepsy)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new('wm.drepilepsy', 'D', 'PRESS', oskey=True)

def unregister():
    bpy.utils.unregister_class(BLENDER_OT_dr_epilepsy)
    km = bpy.context.window_manager.keyconfigs.addon.keymaps["3D View"]
    for kmi in km.keymap_items:
        km.keymap_items.remove(kmi)

if __name__ == "__main__":
    register()
