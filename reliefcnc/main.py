import sys
import ctypes
import time
import subprocess
from optparse import OptionParser
from pycnic.music import MusicPlayer
from pycnic.shoot import ReliefShooter

if __name__ =='__main__':
    parser = OptionParser()
    parser.add_option('-d', '--debug', nargs=0, help='set debug mode')
    parser.add_option('', '--music', nargs=0, help='play music')
    parser.add_option('', '--test', nargs=0, help='test')
    (options, args) = parser.parse_args()
    if options.debug is not None:
        debug = True
    else debug = False

    if options.music is not None:
        MusicPlayer().play()
    
    if options.test is not None:
        ReliefShooter().test()


