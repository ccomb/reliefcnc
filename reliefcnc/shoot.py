# coding: utf-8
import subprocess
import time, sys, os
from pycnic.soprolec import InterpCNC
import signal
import logging

logger = logging.getLogger('ReliefCNC')
logging.basicConfig(level=logging.INFO)

class ReliefShooter(object):

    base = 10.0 # distance between 2 images in mm
    nb_points = 8 # nb of stereoscopic images (8 for Alioscopy panel)
    camdelay = 0.135 # delay (s) between the burst command and the 1st image
    # The Nikon D200 took 8 images (7 intervals) in 1.515s
    burst_period = 1.515/7 # delay between 2 images
    position = 0 # current position in our unit
    resolution = None # each move will be multiplied by the resolution
    maxrange = None # the max range in our unit
    _calibrated = False
    speed = None # speed in our unit/s

    def __init__(self, maxrange=None, resolution=1.0, speed=None, debug=False):
        self.on()
        self.resolution = float(resolution)
        self.position = float(self.cnc.x) / self.resolution
        if resolution == 1:
            logger.info('You did not provide a resolution! Use --calibrate to know it')
        self.maxrange = maxrange
        self.debug = debug
        if not self.resolution:
            self.resolution = 1.0
        self.speed = (speed or 0)/self.resolution or int(800 / (self.resolution or 1)) # arbitrary default speed
        self.cnc.speed = round(self.speed*self.resolution)
        logger.debug('speed=%s' % self.speed)

    def calibrate(self, steps=None, distance=None, limit=False):
        """compute and store the resolution,
        given a distance and a number of steps
        If limit = False, the maxrange is infinite. (tournette)
        If limit = True, the given distance is the maxrange.
        """
        assert(not self._calibrated)
        try:
            self.resolution = float(steps)/float(distance)
        except:
            self.resolution = 1.0
        self.maxrange = None
        if limit:
            self.maxrange = float(distance)
        self.position = float(self.cnc.x) / self.resolution
        self.speed = self.speed / self.resolution
        self._calibrated = True
        return self.resolution

    def on(self):
        """switch on the controller
        """
        self.cnc = InterpCNC(speed=self.speed)

    def off(self):
        """switch off the controller
        """
        self.cnc.disconnect()

    def reset(self):
        """reset all axis
        """
        self.cnc.reset_all_axis()

    def move_to(self, position, ramp=1, speed=None, duration=None):
        """Move to specified position in our unit using a ramp
        """
        # speed or duration, but not both
        if speed is not None:
            assert(duration is None)
        else:
            if duration is None:
                speed = self.speed
            else:
                speed = abs(position - (float(self.cnc.x) / self.resolution)) / duration

        if (self.maxrange is not None
            and (position > self.maxrange or position < 0)
        ):
            raise ValueError("The wanted position is outside the max range")
        self.cnc.speed = round(speed * self.resolution)
        logger.info(u'moving to %s' % position)
        self.cnc.move(x=position*self.resolution, ramp=ramp)
        self.cnc.wait()
        self.position = float(self.cnc.x) / self.resolution
        # restore the default speed
        self.cnc.speed = round(self.speed * self.resolution)

    def move_by(self, distance, ramp=1, speed=None, duration=None):
        """Move the camera by the specified distance in mm
        """
        # speed or duration, but not both
        if speed is not None:
            assert(duration is None)
        else:
            if duration is not None:
                # compute the speed based on the duration
                speed = abs(distance)/duration
            else:
                # fail back on the default speed
                speed = self.speed

        steps_to_move = distance*self.resolution
        new_motor_position = self.cnc.x + steps_to_move
        if (self.maxrange is not None
            and (new_motor_position > self.maxrange*self.resolution
                 or new_motor_position < 0)
        ):
            raise ValueError("The wanted position is outside the max range")
        self.cnc.speed = round(speed * self.resolution)
        logger.info(u'moving by %s' % distance)
        self.cnc.move(x=round(new_motor_position), ramp=ramp)
        self.cnc.wait()
        self.position = float(self.cnc.x) / self.resolution
        # restore the default speed
        self.cnc.speed = round(self.speed * self.resolution)

    def burst(self):
        """shoot according to the parameters
        """
        subprocess.Popen(('killall', 'gphoto2'))
        self.cam_command = (
            'gphoto2',
            '--auto-detect',
            '--set-config',
            '/main/settings/capturetarget=1',
            '--set-config',
            '/main/capturesettings/capturemode=1',
            '--set-config',
            '/main/capturesettings/burstnumber=%s' % self.nb_points,
            '--capture-image',
            '-I', '-1')

        logger.info(u'base = %s' % self.base)

        # assume we are in the middle of the rail
        self.cnc.x = 0

        assert(self.nb_points > 0)

        self.cnc.speed = self.speed

        # store initial position
        zero = self.position

        # calculate the speed according to the camera burst rate
        speed = self.base / self.burst_period  # mm/s
        logger.info('speed = %s mm/s' % speed)

        # compute the margin corresponding to the camdelay
        margin = speed * self.camdelay
        logger.info(u'margin = %s' % margin)

        # take a first photo and move to the left point + the margin
        logger.info('Launch gphoto...')
        p = subprocess.Popen(self.cam_command)

        # signal that the next photo is the last one
        time.sleep(2)
        os.kill(p.pid, signal.SIGUSR2)
        os.kill(p.pid, signal.SIGUSR1)
        time.sleep(3)

        half_range = (self.nb_points-1)*self.base/2.0 + margin
        self.move_by(half_range)

        # set the speed (in steps/s)
        self.cnc.speed = round(speed*self.resolution)

        logger.info('Ok, ready to shoot')
        # launch the shooting and the main const move
        os.kill(p.pid, signal.SIGUSR2)
        os.kill(p.pid, signal.SIGUSR1)
        self.move_by(-half_range, ramp=0)

        # return to zero
        self.cnc.speed = self.speed
        self.move_to(zero)

        p.wait()
        logger.info(u'finished!')

    def slow(self):
        """shoot slowly according to the parameters
        """
        subprocess.Popen(('killall', 'gphoto2'))
        self.cam_command = (
            'gphoto2',
            '--set-config',
            '/main/settings/capturetarget=1',
            '--capture-image')

        logger.info(u'base = %s' % self.base)

        assert(self.nb_points > 0)
        # set the speed
        self.cnc.speed = round(self.speed * self.resolution)

        # store initial position
        zero = self.position

        # move to the left point
        half_range = (self.nb_points-1)*self.base/2.0
        self.move_by(half_range)

        # shoot the first image and let gphoto wait
        p = subprocess.Popen(self.cam_command, close_fds=True)
        p.wait()

        # loop over each stop point
        for i in range(self.nb_points-1):
            # move to the next point
            self.move_by(-self.base)
            #time.sleep(1)
            # shoot the next image
            p = subprocess.Popen(self.cam_command, close_fds=True)
            p.wait()

        # return to zero
        self.cnc.speed=round(self.speed * self.resolution)
        self.move_to(zero)

        logger.info(u'finished!')

    def manual(self):
        """shoot slowly and just wait between photos
        """
        logger.info(u'base = %s' % self.base)

        assert(self.nb_points > 0)
        # set the speed
        self.cnc.speed=round(self.speed * self.resolution)

        # store initial position
        zero = self.position

        # move to the left point
        half_range = (self.nb_points-1)*self.base/2.0
        self.move_by(-half_range)

        # shoot the first image
        time.sleep(2)

        # loop over each stop point
        for i in range(self.nb_points-1):
            # move to the next point
            self.move_by(self.base)
            # shoot the next image
            time.sleep(2)

        # return to zero
        self.cnc.speed=round(self.speed * self.resolution)
        self.move_to(zero)

        logger.info(u'finished!')










