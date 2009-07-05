# coding: utf-8
import subprocess
import time
from pycnic.pycnic import TinyCN
import os
import signal

class ReliefShooter(object):

    base = 10.0 # distance between 2 images in mm
    nb_points = 8 # nb of stereoscopic images (8 for Alioscopy panel)
    camdelay = 1.0 # delay (s) between the burst command and the 1st image
    burst_period = 1.515/7 # delay between 2 images
    margin = 50.0 # move 50mm more to the left and right
    # The Nikon D200 took 8 images (7 intervals) in 1.515s
    position = 0 # current position in mm

    def __init__(self, debug=False):
        self.on(debug)

    def on(self, debug=False):
        """switch on the controller
        """
        self.tiny = TinyCN(debug=debug)

    def init(self):
        # motor resolution
        self.tiny.motor.res_x = 2

        # const speed
        self.tiny.tool.speed = 800
        self.tiny.set_speed(self.tiny.tool.speed, self.tiny.motor.res_x)

        # set maximum acceleration
        self.tiny.set_speed_acca(3)
        self.tiny.set_speed_accb(1)

    def off(self):
        """switch off the controller
        """
        self.tiny.off()

    def zero(self):
        self.tiny.zero_x()
        self.position = 0

    def reset(self):
        pass
        #self.tiny.handle.clearHalt(0x01)
        #self.tiny.handle.clearHalt(0x02)
        #self.tiny.handle.clearHalt(0x81)
        #self.tiny.handle.clearHalt(0x82)
        #self.tiny.handle.reset()
        #self.tiny.handle.resetEndpoint(0x01)
        #self.tiny.handle.resetEndpoint(0x02)
        #self.tiny.handle.resetEndpoint(0x81)
        #self.tiny.handle.resetEndpoint(0x82)
        #self.tiny.restart()

    def move_to(self, position, ramp=1):
        """Move to specified position in mm using a ramp
        """
        self.position = position
        if ramp:
            self.tiny.move_ramp_x(position)
        else:
            self.tiny.move_const_x(position)
        # wait for the move to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.5)

    def move_by(self, distance, ramp=1):
        """Move the camera by the specified distance in mm
        """
        current_position = self.tiny.get_x()
        steps_to_move = distance*10
        if ramp:
            self.tiny.move_ramp_x(current_position + steps_to_move)
        else:
            self.tiny.move_const_x(current_position + steps_to_move)
        # wait for the move to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.5)
        #while self.tiny.get_buffer_state() != 0x8000:
        #    time.sleep(0.5)

    def burst(self):
        """shoot according to the parameters
        """
        self.cam_command = (
            'gphoto2',
            '--auto-detect',
            '--set-config',
            '/main/settings/capturetarget=1',
            '--set-config',
            '/main/capturesettings/capturemode=1',
            '--set-config',
            '/main/capturesettings/burstnumber=%s' % self.nb_points,
            '--capture-image')

        print(u'base = %s' % self.base)
        print(u'margin = %s' % self.margin)

        # reset to zero
        self.tiny.zero_x()

        assert(self.nb_points > 0)
        # calculate the speed according to the burst rate
        speed = self.base / self.burst_period  # mm/s
        print 'speed = %s' % speed
        # set the speed
        self.tiny.set_speed(int(round(10*speed)), self.tiny.motor.res_x)

        # move to the left point + a margin
        half_range = int((self.nb_points-1)*self.base/2 + self.margin)
        print 'move to %s' % half_range
        self.tiny.set_speed_max(2500, self.tiny.motor.res_x)
        self.tiny.move_ramp_x(10*half_range)

        # wait for the first ramp to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.5)

        # compute the burst delay
        sleep = self.camdelay - (self.margin/speed)
        print 'sleep %s...' % sleep

        # launch the burst
        if sleep >= 0:
            p = subprocess.Popen(self.cam_command)
            time.sleep(sleep)
            # launch the main const move
            print 'move to -%s' % half_range
            self.tiny.move_const_x(-10*half_range)
        # launch the burst
        if sleep < 0:
            # launch the main const move
            print 'move to -%s' % half_range
            self.tiny.move_const_x(-10*half_range)
            time.sleep(-sleep)
            p = subprocess.Popen(self.cam_command)

        # return to zero
        self.tiny.set_speed_max(2500, self.tiny.motor.res_x)
        self.tiny.move_ramp_x(0)

        # wait for the first ramp to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.5)

        print u'finished!'
        #while self.tiny.get_buffer_state() != '\x00\x80':
        #    time.sleep(0.5)

    def slow(self):
        """shoot slowly according to the parameters
        """
        self.cam_command = (
            'gphoto2',
            '--auto-detect',
            '--set-config',
            '/main/settings/capturetarget=1',
            '--set-config',
            '/main/capturesettings/capturemode=0',
            '--set-config',
            '/main/capturesettings/burstnumber=1',
            '--capture-image',
            '-I', '-1')

        print(u'base = %s' % self.base)
        print(u'margin = %s' % self.margin)

        # reset to zero
        self.tiny.zero_x()

        assert(self.nb_points > 0)
        # set the speed
        self.tiny.set_speed(2500, self.tiny.motor.res_x)

        # move to the left point
        half_range = int((self.nb_points-1)*self.base/2)
        print 'move to %s' % half_range
        self.tiny.set_speed_max(2500, self.tiny.motor.res_x)
        self.tiny.move_ramp_x(10*half_range)

        # wait for the first ramp to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.1)

        # shoot the first image and let gphoto wait
        p = subprocess.Popen(self.cam_command)
        time.sleep(7)

        # loop over each stop point
        for i in range(self.nb_points-1, 0, -1):
            # move to the next point
            nextpoint = int(10*(-half_range + float(i)*2*half_range/self.nb_points))
            print(u'move to %s' % nextpoint)
            self.tiny.move_ramp_x(nextpoint)
            # wait for the ramp to finish
            while self.tiny.get_fifo_count() > 0:
                time.sleep(0.1)
            time.sleep(2)
            # shoot the next image
            os.kill(p.pid, signal.SIGUSR1)
            time.sleep(3)

        # return to zero
        self.tiny.set_speed_max(2500, self.tiny.motor.res_x)
        self.tiny.move_ramp_x(0)

        # wait for the ramp to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.5)

        # kill gphoto2
        os.kill(p.pid, signal.SIGQUIT)

        print u'finished!'
        #while self.tiny.get_buffer_state() != '\x00\x80':
        #    time.sleep(0.5)

