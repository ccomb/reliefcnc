# coding: utf-8
import sys
from optparse import OptionParser
from reliefcnc.music import MusicPlayer
from reliefcnc.shoot import ReliefShooter

def main():
    parser = OptionParser()
    parser.add_option('', '--debug', nargs=0, help=u'set debug mode')
    parser.add_option('', '--music', nargs=0, help=u'play music')
    parser.add_option('-m', '--move', nargs=1, help=u'move by +/-N steps, or move to step N')
    parser.add_option('', '--reset', nargs=0, help=u'reset device')
    parser.add_option('', '--burst', nargs=0, help=u'shoot sequence in burst mode')
    parser.add_option('', '--slow', nargs=0, help=u'shoot sequence with stops')
    parser.add_option('', '--manual', nargs=0, help=u'just move without shooting')
    parser.add_option('-b', '--base', type='float', nargs=1, help=u'distance between shoots')
    parser.add_option('-r', '--resolution', type='float', nargs=1, help=u'nb of steps per unit (actually *your* unit)')
    parser.add_option('-L', '--left', type='float', nargs=1, help=u'the max left position in your unit)')
    parser.add_option('-R', '--right', type='float', nargs=1, help=u'the max right position in your unit)')
    parser.add_option('-d', '--duration', type='float', nargs=1, help=u'total duration in seconds')
    parser.add_option('-s', '--speed', type='float', nargs=1, help=u'wanted speed')
    parser.add_option('-p', '--points', type='int', nargs=1, help=u'nb of points')
    parser.add_option('', '--sensor', nargs=0, help=u'return to sensor')
    parser.add_option('', '--calibrate', nargs=0, help=u'Perform a calibration to know the resolution')
    options, args = parser.parse_args()
    if options.debug is not None:
        debug = True
    else:
        debug = False

    # PLAY MUSIC
    if options.music is not None:
        MusicPlayer().test()
        sys.exit()

    # CALIBRATION
    if options.calibrate is not None:
        speed=options.speed or 2000
        shooter = ReliefShooter(debug=debug, left_position=None, right_position=None, speed=speed)

        if len(parser.largs) == 3:
            # to be able to run tests without questions
            steps, distance, limit = map(float, parser.largs)
        else:
            # ask questions
            print("Starting calibration with speed=%s" % speed)
            has_sensor = None
            while has_sensor not in ('y', 'n'):
                has_sensor = raw_input(u'Do you have a home sensor? (y/n) : ')
            print('Moving to the origin point...')
            if has_sensor == 'y':
                shooter.cnc.x = None
            else:
                while True:
                    move = raw_input((u"Please enter a positive or negative number until you reach the origin.\n"
                                      u"When you are satisfied with the position, hit Enter\n\n"
                                      u"Number of motor steps to move = "))
                    if move == '':
                        break
                    else:
                        shooter.right_position = sys.maxint
                        shooter.left_position = 0
                        shooter.move_by(int(move), ramp=0)
                shooter.cnc.x = 0
            # try to reach the right position manually
            while True:
                value = raw_input((u'\nWe are now at position %s.\n'
                   u'Please enter a different number (+/-), until you reach the maximum range.\n'
                   u'When you are at the maximum range, simply hit the Enter key.\n\n'
                   u'Number of motor steps to move = ') % shooter.cnc.x)
                if value == '':
                    break
                try:
                    value = int(value)
                except:
                    continue
                shooter.move_by(value, ramp=0)

            # compute the resolution
            steps = shooter.cnc.x
            distance = raw_input(u"Now please give the corresponding distance in your unit :")
            shooter.right_position = distance
            limit = 'y' == raw_input(u"Do you want to limit the moves to this range ? (y/n): ")
        resolution = shooter.calibrate(steps=steps,
                                       distance=distance,
                                       limit=bool(limit))
        print "The resolution is %s (steps/unit)" % resolution
        sys.exit()



    # JUST MOVE
    if options.move is not None:
        move = float(options.move)
        if options.speed is not None and options.duration is not None:
            parser.error(u"You cannot specify both a speed and a duration")

        shooter = ReliefShooter(debug=debug,
                                resolution=options.resolution,
                                left_position=options.left_position,
                                right_position=options.right_position)
        if options.move[0] in ('+', '-'):
            shooter.move_by(move,
                            speed=options.speed,
                            duration=options.duration)
        else:
            shooter.move_to(move,
                            speed=options.speed,
                            duration=options.duration)
        sys.exit()

    # GO TO SENSOR
    if options.sensor is not None:
        shooter = ReliefShooter(debug=debug,
                                speed=options.speed,
                                resolution=options.resolution)
        shooter.cnc.x = None
        sys.exit()

    # SHOOTING SEQUENCE
    if (options.burst, options.slow, options.manual) != (None, None, None):
        shooter = ReliefShooter(debug=debug,
                                resolution=options.resolution,
                                left_position=options.left_position,
                                right_position=options.right_position,
                                speed=options.speed)
        if options.base:
            shooter.base = options.base
        if options.points:
            shooter.nb_points = options.points

        if options.burst is not None:
            shooter.burst()
        elif options.slow is not None:
            shooter.slow()
        elif options.manual is not None:
            shooter.manual()
        sys.exit()

    # RESET
    if options.reset is not None:
        shooter = ReliefShooter(debug=debug)
        shooter.reset()
        sys.exit()

    parser.error(u'doing nothing is boring')

