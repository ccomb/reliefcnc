# coding: utf-8
from optparse import OptionParser
from pycnic import
import ctypes
import subprocess
import sys
import time
import time


class ReliefShooter(object):

    def __init__(self, debug=False):
        self.tiny = TinyCN(debug=debug)

        # motor resolution
        self.tiny.motor.res_x = 30
        self.tiny.motor.res_y = 200
        self.tiny.motor.res_z = 200

        # misc tests and inits
        self.tiny.set_prompt(0)
        self.tiny.read_name()
        self.tiny.set_fifo_depth(255) # 255 pulses
        self.tiny.set_pulse_width(64) # 5µs (?)
        res = self.tiny.get_speed_calc()
        self.tiny.tool.numerateur = ByteToInt(res[4:8])
        self.tiny.tool.denominateur = ByteToInt(res[0:4])
        print('resolution = %s' % ByteToHex(res))
        print('numerateur = %s' % self.tiny.tool.numerateur)
        print('denominateur = %s' % self.tiny.tool.denominateur)

    def test(self):
        # calibrate zero

        # move to the left

        # launch the burst

        # launch the cnc commands

        # return to the left


        # speed
        self.tiny.tool.speed = 700
        self.tiny.set_speed(self.tiny.tool.speed, self.tiny.motor.res_x)
    
        # acceleration
        self.tiny.set_speed_acca(4)
        #self.tiny.set_speed_accb(2)
    
        # launch the burst shoot
        # D200 took 1.515sec for 8 images
    
        self.tiny.move_var_x(4400, 0, 105, 'up')
        self.tiny.move_var_x(5000, 105, 0, 'down')
    
        self.tiny.move_var_x(600, 0, 300, 'up')
        self.tiny.move_var_x(0, 300, 0, 'down')
    
        time.sleep(0.5)
    
        command = ('gphoto2',
                   '--auto-detect',
                   '--set-config',
                   '/main/settings/capturetarget=1',
                   '--set-config',
                   '/main/capturesettings/capturemode=1',
                   '--set-config',
                   '/main/capturesettings/burstnumber=8',
                   '--capture-image')
    
        p = subprocess.Popen(command)
    
        #ramp self.tiny.write('\x14\x08\x10\x00' + 3*'\x00\x00\x01\x10')
        #self.tiny.get_buffer_state()
        #while self.tiny.get_buffer_state() != '\x00\x80':
        #    pass
        #while self.tiny.get_fifo_count() > 0:
        #    time.sleep(0.1)
    
    #    usb.release_interface(self.tiny.handle, 0)
    #    usb.detach_kernel_driver_np(self.tiny.handle,0)
    #    usb.reset(self.tiny.handle)
    #    usb.close(self.tiny.handle)
        #del self.tiny




    

