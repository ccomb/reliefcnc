import sys
from pycnic.pycnic import TinyCN

class MusicPlayer(object):
    """music player with a stepper motor
    """
    freqs = [ int(220*(2**(1.0/12))**i) for i in range(44) ]
    notes = [
     'A',  'A#',  'B',  'C',  'C#',  'D',  'D#',  'E',  'F',  'F#',  'G',  'G#',
     'A2', 'A2#', 'B2', 'C2', 'C2#', 'D2', 'D2#', 'E2', 'F2', 'F2#', 'G2', 'G2#',
     'A3', 'A3#', 'B3', 'C3', 'C3#', 'D3', 'D3#', 'E3', 'F3', 'F3#', 'G3', 'G3#',
     'A4', 'A4#', 'B4', 'C4', 'C4#', 'D4', 'D4#', 'E4', 'F4', 'F4#', 'G4', 'G4#',
            ]

    current_position = 0
    way = 1 # forward = 1, backward = -1

    def __init__(self, debug=False):
        self.tiny = TinyCN(debug=debug)
        self.tiny.motor.res_x = 30
        self.tiny.tool.speed = 700
        #self.tiny.set_speed(self.tiny.tool.speed, self.tiny.motor.res_x)

    def reset(self):
        # return to zero
        self.tiny.move_var_x(0, 0, 400, 'up')

    def play(self, note, duration, reverse=1):
        notfreqs = dict(zip(self.notes, self.freqs))
        #duration = 5*duration # microstep resolution
        self.way = reverse * self.way
        # set note with speed
        if type(note) is not int:
            speed = notfreqs[note]
        else:
            speed = note
        self.tiny.set_speed(speed, self.tiny.motor.res_x)
        # set final position
        steps_to_move = self.way * speed * duration
        final_position = self.current_position + steps_to_move
        if final_position > 10000 or final_position < 0:
            # if cannot move forward, change our way
            self.way = -self.way
            steps_to_move = self.way * speed * duration
            final_position = self.current_position + steps_to_move
    
        if final_position > 10000 or final_position < 0:
            raise('range too large')
    
        self.current_position = final_position
        self.tiny.move_const_x(final_position)

    def test(self):
        # Also sprach Python
        player = MusicPlayer()
        player.play('C', 1)
        player.play('G', 1)
        player.play('C2', 1.7)
        player.play('E2', 0.3)
        player.play('D2#', 1)
        player.play('C', 0.3)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 1, -1)
    
        player.play('C', 1)
        player.play('G', 1)
        player.play('C2', 1.7)
        player.play('D2#', 0.3)
        player.play('E2', 1)
        player.play('C', 0.3)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 0.3, -1)
        player.play('C', 1, -1)
    
        player.play('C', 1)
        player.play('G', 1)
        player.play('C2', 1.7)
        player.play('G2', 0.3)
        player.play('A2', 2)
    
    
        player.play('A2', 0.33, -1)
        player.play('B3', 0.33)
        player.play('C3', 1)
        player.play('D3', 1)
    
        player.play('E3', 0.5)
        player.play('F3', 0.5)
        player.play('G3', 1)
    
        player.play('E3', 0.5)
        player.play('C3', 0.5)
        player.play('G2', 0.5)
        player.play('E2', 0.5)
    
        player.play('E3', 0.5)
        player.play('F3', 0.5)
        player.play('G3', 1)
    
        player.play('A4', 1)
        player.play('B4', 1)
        player.play('C4', 2)
    
        sys.exit()
