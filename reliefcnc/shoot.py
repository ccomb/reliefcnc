# coding: utf-8
import subprocess
import time
from pycnic.pycnic import TinyCN

class ReliefShooter(object):

    base = 10.0 # distance between 2 images in mm
    nb_points = 8 # nb of stereoscopic images (8 for Alioscopy panel)
    camdelay = 1.0 # delay (s) between the burst command and the 1st image
    burst_period = 1.515/7 # delay between 2 images
    margin = 100.0 # move 10mm more to the left and right
    # The Nikon D200 took 8 images (7 intervals) in 1.515s
    position = 0 # current position in mm

    def __init__(self, debug=False):
        self.tiny = TinyCN(debug=debug)

        # motor resolution
        self.tiny.motor.res_x = 30

        # const speed
        self.tiny.tool.speed = 800
        self.tiny.set_speed(self.tiny.tool.speed, self.tiny.motor.res_x)
    
        # set maximum acceleration
        self.tiny.set_speed_acca(3)
        self.tiny.set_speed_accb(1)

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

    def zero(self):    
        self.tiny.zero_x()
        self.position = 0

    def move_to(self, position, ramp=1):
        """Move to specified position in mm using a ramp
        """
        self.position = position
        self.step = self.position
        if ramp:
            self.move_ramp(position)
        else:
            self.move_const(position)
        
    def move_by(self, distance, ramp=0):
        """Move the camera by the specified distance in mm
        """
        current_position = self.tiny.get_x()
        steps_to_move = distance*10
        if ramp:
            self.tiny.move_ramp_x(current_position + steps_to_move)
        else:
            self.tiny.move_const_x(current_position + steps_to_move)

    def shoot(self):
        """shoot according to the parameters
        """

        # reset to zero
        self.tiny.zero_x()

        assert(self.nb_points > 0)
        # calculate the speed according to the burst rate
        speed = self.base / self.burst_period  # mm/s
        print 'speed = %s' % speed
        # set the speed
        self.tiny.set_speed(int(round(10*speed)), self.tiny.motor.res_x)

        # get the acceleration
        #acceleration = 10.0 / self.tiny.get_speed_acca()

        # calculate the acceleration length (D = Vmax^2 / a)
        #reso = 10 # factor for acc
        #acc_length = speed**2 / acceleration / reso
        #print 'acc_length %s' % acc_length

        # move to the left point + a 1cm margin
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
    
        # wait for the buffer to be empty
        #while self.tiny.get_fifo_count() > 0:
        #    time.sleep(0.5)

        print u'finished!'
        #while self.tiny.get_buffer_state() != '\x00\x80':
        #    pass
    
