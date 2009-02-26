import sys
from optparse import OptionParser
from reliefcnc.music import MusicPlayer
from reliefcnc.shoot import ReliefShooter

def main():
    parser = OptionParser()
    parser.add_option('-d', '--debug', nargs=0, help='set debug mode')
    parser.add_option('', '--music', nargs=0, help='play music')
    parser.add_option('-t', '--test', nargs=0, help='test')
    parser.add_option('-m', '--moveby', nargs=1, help='move by N steps')
    parser.add_option('-s', '--shoot', nargs=0, help='shoot sequence')
    parser.add_option('-b', '--base', nargs=1, help='define the base in mm')
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
        
    
    if options.shoot is not None:
        shooter = ReliefShooter(debug=debug)
        shooter.base = 5
        if options.base.isdigit():
            shooter.base = int(options.base)
        shooter.camdelay = 1
        shooter.shoot()
        #shooter.shoot()
        sys.exit()

    print u'doing nothing is boring'
