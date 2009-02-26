# coding: utf-8
import subprocess
import time
from pycnic.pycnic import TinyCN

class ReliefShooter(object):

    base = 10 # distance between 2 images in mm
    nb_points = 8 # nb of stereoscopic images (8 for Alioscopy panel)
    camdelay = 0.5 # delay (s) between the burst command and the 1st image
    burst_period = 1.515/7 # delay between 2 images
    # The Nikon D200 took 8 images (7 intervals) in 1.515s
    position = 0 # current position in mm

    def __init__(self, debug=False):
        self.tiny = TinyCN(debug=debug)

        # motor resolution
        self.tiny.motor.res_x = 30

        # speed
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

    def move_to(self, position):
        """Move to specified position in mm using a ramp
        """
        self.position = position
        self.step = self.position 
        self.move_ramp(position)
        
    def move_by(self, distance):
        """Move the camera by the specified distance in mm
        """
        current_position = self.tiny.get_x()
        steps_to_move = distance*10
        self.tiny.move_ramp_x(current_position + steps_to_move)

    def shoot(self):
        """shoot according to the parameters
        """

        # reset to zero
        self.tiny.zero_x()

        assert(self.nb_points > 0)
        # calculate the speed according to the burst rate
        speed = int((self.nb_points-1) * self.base / self.burst_period) # mm/s
        print 'speed %s' % speed

        # get the acceleration
        acceleration = 10.0 / self.tiny.get_speed_acca()

        # calculate the acceleration length (D = Vmax^2 / a)
        reso = 20.0 # factor for acc
        acc_length = speed**2 / acceleration / reso
        print 'acc_length %s' % acc_length

        # move to the left point + acceleration length + a 1cm margin
        half_range = int(self.base/2 + acc_length + 10)
        print 'move to %s' % half_range
        self.tiny.set_speed_max(2500, self.tiny.motor.res_x)
        self.tiny.move_ramp_x(half_range)

        # wait for the first ramp to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.5)

        # set the max speed of the ramp
        self.tiny.set_speed_max(speed, self.tiny.motor.res_x)
        # launch the main ramp
        print 'move to -%s' % half_range
        self.tiny.move_ramp_x(-half_range)

        # launch the burst
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
    
