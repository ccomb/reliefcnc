import sys
from optparse import OptionParser
from reliefcnc.music import MusicPlayer
from reliefcnc.shoot import ReliefShooter

def main():
    parser = OptionParser()
    parser.add_option('-d', '--debug', nargs=0, help='set debug mode')
    parser.add_option('-m', '--music', nargs=0, help='play music')
    parser.add_option('-t', '--test', nargs=0, help='test')
    parser.add_option('-b', '--moveby', nargs=0, help='move by N steps')
    (options, args) = parser.parse_args()
    if options.debug is not None:
        debug = True
    else:
        debug = False

    if options.music is not None:
        MusicPlayer().test()
        sys.exit()

    if options.moveby.isdigit():
        shooter = ReliefShooter(debug=debug)
        shooter.move_by(options.moveby)
        sys.exit()
        
    
    if options.test is not None:
        shooter = ReliefShooter(debug=debug)
        shooter.base = 1600
        shooter.camdelay = 1
        shooter.zero()
        shooter.test()
        #shooter.shoot()
        sys.exit()

    print u'doing nothing is boring'
