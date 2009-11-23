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
    camdelay = 0.135 # delay (s) between the burst command and the 1st image
    # The Nikon D200 took 8 images (7 intervals) in 1.515s
    burst_period = 1.515/7 # delay between 2 images
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

    def move_to(self, position, ramp=1):
        """Move to specified position in mm using a ramp
        """
        position = position*self.resolution
        if position > self.maxrange*self.resolution:
            logger.error("just don't do that")
            return
        self.position = position
        self.cnc.move(x=position, ramp=ramp)
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
            '/main/capturesettings/burstnumber=1',
            '--capture-image',
            '--set-config',
            '/main/capturesettings/burstnumber=%s' % self.nb_points,
            '--capture-image',
            '-I', '-1')

        logger.info(u'base = %s' % self.base)

        # assume we are in the middle of the rail
        self.cnc.x = 0

        assert(self.nb_points > 0)

        self.cnc.speed = 2000

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
        time.sleep(2)

        half_range = int((self.nb_points-1)*self.base/2.0 + margin)
        logger.info('move to %s mm' % half_range)
        self.move_to(half_range)

        # set the speed (in steps/s)
        self.cnc.speed = round(speed*self.resolution)

        logger.info('Ok, ready to shoot')
        # launch the shooting and the main const move
        logger.info('move to -%s mm' % half_range)
        os.kill(p.pid, signal.SIGUSR2)
        os.kill(p.pid, signal.SIGUSR1)
        self.move_to(-half_range, ramp=0)

        # return to zero
        self.cnc.speed = 2000
        self.move_to(0)

        p.wait()
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
            '--capture-image')

        logger.info(u'base = %s' % self.base)

        assert(self.nb_points > 0)
        # set the speed
        self.cnc.speed = 2500

        # move to the left point
        half_range = int((self.nb_points-1)*self.base/2.0)
        logger.info('move to %s' % half_range)
        self.move_by(half_range)

        # shoot the first image and let gphoto wait
        p = subprocess.Popen(self.cam_command, close_fds=True)
        p.wait()

        # loop over each stop point
        for i in range(self.nb_points-1):
            # move to the next point
            logger.info(u'moving by %s' % -self.base)
            self.move_by(-self.base)
            time.sleep(1)
            # shoot the next image
            p = subprocess.Popen(self.cam_command, close_fds=True)
            p.wait()

        # return to zero
        self.cnc.speed=2500
        self.move_to(0)

        logger.info(u'finished!')


    def manual(self):
        """shoot slowly and just wait between photos
        """
        logger.info(u'base = %s' % self.base)

        assert(self.nb_points > 0)
        # set the speed
        self.cnc.speed = 2500

        # move to the left point
        half_range = int((self.nb_points-1)*self.base/2.0)
        logger.info('move to %s' % half_range)
        self.move_by(-half_range)

        # shoot the first image
        time.sleep(2)

        # loop over each stop point
        for i in range(self.nb_points-1):
            # move to the next point
            logger.info(u'moving by %s' % -self.base)
            self.move_by(self.base)
            # shoot the next image
            time.sleep(2)

        # return to zero
        self.cnc.speed=2500
        self.move_to(0)

        logger.info(u'finished!')

