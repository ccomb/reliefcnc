# coding: utf-8
import subprocess
import time
from pycnic.soprolec import InterpCNC
import os
import signal
import logging

logger = logging.getLogger('ReliefCNC')
logging.basicConfig(level=logging.INFO)

class ReliefShooter(object):

    base = 10.0 # distance between 2 images in mm
    nb_points = 8 # nb of stereoscopic images (8 for Alioscopy panel)
    camdelay = 1.0 # delay (s) between the burst command and the 1st image
    # The Nikon D200 took 8 images (7 intervals) in 1.515s
    burst_period = 1.515/7 # delay between 2 images
    margin = 50.0 # move 50mm more to the left and right
    position = 0 # current position in mm
    resolution = None # each move will be multiplied by the resolution
    maxrange = None

    def __init__(self, debug=False, resolution=None, maxrange=None):
        self.on()
        self.resolution = resolution
        self.maxrange = maxrange

    def calibrate(self, steps=None, distance=None, restart=False):
        """This method allows to define the resolution and the max range.
        The resolution is the conversion between our unit and the motor steps.
        The max range is the rail length, expressed in our unit.
        You have to run it three times :
        - run it once to move to the zero
        - run several times by providing a steps argument until the maximum
          distance is reached.
          Then measure the new position in mm or in your own unit.
        - run it a third time by providing the measured distance.
        - That's it. Now you can use the ReliefShooter with your own units.
        - if you want to restart the calibration, run it with 'restart=True'
        """
        if restart:
            self.resolution = None
            self.maxrange = None

        if self.maxrange is not None and self.resolution not in (None, 'step1'):
            logger.info('Calibration is already done. run with restart=True to restart it')
            logger.info('resolution: 1 unit = %s steps\nmaxrange = %s units'
                        % (self.resolution, self.maxrange))

            return

        if self.maxrange is None and self.resolution is None:
            logger.info('1st step of resolution calibration. Moving to zero.')
            self.cnc.x = None
            self.resolution = 'step1'
            logger.info('Now rerun with steps=<your chosen amount>, until you reach the max range')
            return

        if self.resolution == 'step1' and distance is None:
            if steps == None:
                logger.warning('You should now provide a number of steps')
                return
            logger.info('2nd step of resolution calibration. Moving to step %s.' % steps)
            self.cnc.move(x=steps)
            self.maxrange = steps
            logger.info('Now rerun with distance=<the mesured distance>')
            return

        if type(self.maxrange) == int:
            logger.info('3rd step of resolution calibration. Computing resolution.')
            if distance == None:
                logger.warning('You should now provide a distance')
                return
            self.resolution = float(self.maxrange)/float(distance)
            self.maxrange = self.maxrange / self.resolution
            logger.info('Calibration finished:\nresolution: 1 unit = %s steps\nmaxrange = %s units'
                        % (self.resolution, self.maxrange))
            self.cnc.move(x=0)


    def on(self):
        """switch on the controller
        """
        self.cnc = InterpCNC(speed=800)

    def off(self):
        """switch off the controller
        """
        self.cnc.disconnect()

    def move_to(self, position):
        """Move to specified position in mm using a ramp
        """
        position = position*self.resolution
        if position > self.maxrange*self.resolution:
            logger.error("just don't do that")
            return
        self.position = position
        self.cnc.move(x=position)
        self.cnc.wait()

    def move_by(self, distance, ramp=1):
        """Move the camera by the specified distance in mm
        """
        steps_to_move = distance*self.resolution
        current_position = self.cnc.x
        new_position = current_position + steps_to_move
        if new_position > self.maxrange*self.resolution:
            logger.error("just don't do that")
            return
        self.cnc.move(x=new_position, ramp=ramp)
        self.cnc.wait()

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

        logger.info(u'base = %s' % self.base)
        logger.info(u'margin = %s' % self.margin)

        # reset to zero
        self.tiny.zero_x()

        assert(self.nb_points > 0)
        # calculate the speed according to the burst rate
        speed = self.base / self.burst_period  # mm/s
        logger.info('speed = %s' % speed)
        # set the speed
        self.tiny.set_speed(int(round(10*speed)), self.tiny.motor.res_x)

        # move to the left point + a margin
        half_range = int((self.nb_points-1)*self.base/2 + self.margin)
        logger.info('move to %s' % half_range)
        self.tiny.set_speed_max(2500, self.tiny.motor.res_x)
        self.tiny.move_ramp_x(10*half_range)

        # wait for the first ramp to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.5)

        # compute the burst delay
        sleep = self.camdelay - (self.margin/speed)
        logger.info('sleep %s...' % sleep)

        # launch the burst
        if sleep >= 0:
            p = subprocess.Popen(self.cam_command)
            time.sleep(sleep)
            # launch the main const move
            logger.info('move to -%s' % half_range)
            self.tiny.move_const_x(-10*half_range)
        # launch the burst
        if sleep < 0:
            # launch the main const move
            logger.info('move to -%s' % half_range)
            self.tiny.move_const_x(-10*half_range)
            time.sleep(-sleep)
            p = subprocess.Popen(self.cam_command)

        # return to zero
        self.tiny.set_speed_max(2500, self.tiny.motor.res_x)
        self.tiny.move_ramp_x(0)

        # wait for the first ramp to finish
        while self.tiny.get_fifo_count() > 0:
            time.sleep(0.5)

        logger.info(u'finished!')

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

        logger.info(u'base = %s' % self.base)
        logger.info(u'margin = %s' % self.margin)

        assert(self.nb_points > 0)
        # set the speed
        self.cnc.speed = 2500

        # move to the left point
        half_range = int((self.nb_points-1)*self.base/2.0)
        logger.info('move to %s' % half_range)
        self.move_by(half_range)

        # shoot the first image and let gphoto wait
        p = subprocess.Popen(self.cam_command)
        time.sleep(7)

        # loop over each stop point
        for i in range(self.nb_points-1):
            # move to the next point
            logger.info(u'moving by %s' % -self.base)
            self.move_by(-self.base)
            time.sleep(2)
            # shoot the next image
            os.kill(p.pid, signal.SIGUSR1)
            time.sleep(3)

        # return to zero
        self.cnc.speed=2500
        self.move_to(0)

        # kill gphoto2
        os.kill(p.pid, signal.SIGQUIT)

        logger.info(u'finished!')


    def manual(self):
        """shoot slowly and just wait between photos
        """
        logger.info(u'base = %s' % self.base)
        logger.info(u'margin = %s' % self.margin)

        assert(self.nb_points > 0)
        # set the speed
        self.cnc.speed = 2500

        # move to the left point
        half_range = int((self.nb_points-1)*self.base/2.0)
        logger.info('move to %s' % half_range)
        self.move_by(-half_range)

        # shoot the first image
        time.sleep(3)

        # loop over each stop point
        for i in range(self.nb_points-1):
            # move to the next point
            logger.info(u'moving by %s' % -self.base)
            self.move_by(self.base)
            # shoot the next image
            time.sleep(3)

        # return to zero
        self.cnc.speed=2500
        self.move_to(0)

        logger.info(u'finished!')

