import sys
from optparse import OptionParser
from reliefcnc.music import MusicPlayer
from reliefcnc.shoot import ReliefShooter

def main():
    parser = OptionParser()
    parser.add_option('-d', '--debug', nargs=0, help=u'set debug mode')
    parser.add_option('', '--music', nargs=0, help=u'play music')
    parser.add_option('-m', '--move', nargs=1, help=u'move by +/-N steps, or move to position N')
    parser.add_option('', '--reset', nargs=0, help=u'reset device')
    parser.add_option('', '--burst', nargs=0, help=u'shoot sequence in burst mode')
    parser.add_option('', '--slow', nargs=0, help=u'shoot sequence slowly')
    parser.add_option('', '--base', type='int', nargs=1, help=u'define the base in mm')
    options, args = parser.parse_args()
    if options.debug is not None:
        debug = True
    else:
        debug = False

    if options.music is not None:
        MusicPlayer().test()
        sys.exit()

    if (options.move is not None
          and (options.move.isdigit()
          or (options.move[0] in ('+','-')
            and options.move[1:].isdigit()))):
        shooter = ReliefShooter(debug=debug)
        shooter.init()
        if options.move[0] in ('+', '-'):
            shooter.move_by(int(options.move))
        else:
            shooter.move_to(int(options.move))
        sys.exit()


    if options.burst is not None:
        shooter = ReliefShooter(debug=debug)
        shooter.init()
        if options.base:
            shooter.base = options.base
        shooter.camdelay = 0.8
        shooter.burst()
        #shooter.shoot()
        sys.exit()

    if options.slow is not None:
        shooter = ReliefShooter(debug=debug)
        shooter.init()
        if options.base:
            shooter.base = options.base
        shooter.camdelay = 0.8
        shooter.slow()
        #shooter.shoot()
        sys.exit()

    if options.reset is not None:
        shooter = ReliefShooter(debug=debug)
        shooter.reset()
        sys.exit()

    print u'doing nothing is boring'
