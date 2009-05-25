import sys
from optparse import OptionParser
from reliefcnc.music import MusicPlayer
from reliefcnc.shoot import ReliefShooter

def main():
    parser = OptionParser()
    parser.add_option('-d', '--debug', nargs=0, help='set debug mode')
    parser.add_option('', '--music', nargs=0, help='play music')
    parser.add_option('-m', '--moveby', nargs=1, help='move by N steps')
    parser.add_option('', '--burst', nargs=0, help='shoot sequence in burst mode')
    parser.add_option('', '--slow', nargs=0, help='shoot sequence slowly')
    parser.add_option('', '--base', nargs=1, help='define the base in mm')
    (options, args) = parser.parse_args()
    if options.debug is not None:
        debug = True
    else:
        debug = False

    if options.music is not None:
        MusicPlayer().test()
        sys.exit()

    if (options.moveby is not None
          and (options.moveby.isdigit()
          or (options.moveby[0] == '-'
            and options.moveby[1:].isdigit()))):
        shooter = ReliefShooter(debug=debug)
        shooter.move_by(int(options.moveby))
        sys.exit()


    if options.burst is not None:
        shooter = ReliefShooter(debug=debug)
        if options.base and options.base.isdigit():
            shooter.base = int(options.base)
        shooter.camdelay = 0.8
        shooter.burst()
        #shooter.shoot()
        sys.exit()

    if options.slow is not None:
        shooter = ReliefShooter(debug=debug)
        if options.base and options.base.isdigit():
            shooter.base = int(options.base)
        shooter.camdelay = 0.8
        shooter.slow()
        #shooter.shoot()
        sys.exit()

    print u'doing nothing is boring'
