import serial
import time
import signal

class PicoPulseGen:
    def __init__(self, port='/dev/ttyACM0'):
        self._pulse_offset = 0
        self._pulse_width = 0
        self._trig_edges = 0
        
        self.pico = serial.Serial(port, 115200)
        time.sleep(0.1)
        self.pico.write(b'S')

        test = self.pico.readline()
        if b'PulseGenerator' not in test:
            raise ConnectionError('Could not connect to the PulseGenerator :(')

        signal.signal(signal.SIGALRM, self.arm_abort)
        

    @property
    def pulse_offset(self):
        return self._pulse_offset

    
    @pulse_offset.setter
    def pulse_offset(self, offset):
        if type(offset) != int or offset < 0 or offset > 0xFFFFFFFF:
            raise ValueError('Offset has to be an int between 0 and 0xFFFFFFFF')
        
        self._pulse_offset = offset
        
        self.pico.flushInput()
        self.pico.write(b'O')
        self.pico.write((self._pulse_offset).to_bytes(4, 'little'))
        ret = self.pico.readline()
        assert int(ret.strip()) == self._pulse_offset, ret

        
    @property
    def pulse_width(self):
        return self._pulse_width

    
    @pulse_width.setter
    def pulse_width(self, width):
        if type(width) != int or width < 0 or width > 0xFFFFFFFF:
            raise ValueError('Width has to be an int between 0 and 0xFFFFFFFF')
        
        self._pulse_width = width

        self.pico.flushInput()
        self.pico.write(b'W')
        self.pico.write((self._pulse_width).to_bytes(4, 'little'))
        ret = self.pico.readline()
        assert int(ret.strip()) == self._pulse_width, ret


    @property
    def trig_edges(self):
        return self._trig_edges

    
    @trig_edges.setter
    def trig_edges(self, edges):
        if type(edges) != int or edges < 0 or edges > 0xFFFFFFFF:
            raise ValueError('Width has to be an int between 0 and 0xFFFFFFFF')
        
        self._trig_edges = edges
        
        self.pico.write(b'E')
        self.pico.write((self._trig_edges).to_bytes(4, 'little'))
        ret = self.pico.readline()
        assert int(ret.strip()) == self._trig_edges, ret
            
        
    def arm(self):
        self.pico.write(b'A')
        ret = self.pico.readline()
        assert b'A' in ret


    def wait_trig(self, timeout=5):
        self.pico.write(b'B')
        signal.alarm(timeout)
        ret = self.pico.readline()
        signal.alarm(0)
        assert b'T' in ret


    def arm_abort(self, signum, frame):
        print('No trigger observed, disarming!')
        self.pico.write(b'D')


    def status(self):
        self.pico.write(b'S')
        ret = self.pico.readline()
        print(ret.decode('utf-8'))
        

    def set_gpio(self, state):
        if type(state) != int or state < 0:
            raise ValueError('State has to be zero (GPIO 0) or a positive value larger than zero (GPIO 1)')

        self.pico.write(b'G')
        self.pico.write(bytes([7])) # For now there is only one GPIO pin used for this functionality
        if state:
            self.pico.write(bytes([1]))
        else:
            self.pico.write(bytes([0]))

        ret = self.pico.readline()
        assert b'G' in ret


    def read_gpios(self):
        self.pico.write(b'R')
        ret = self.pico.readline()
        ret = int(ret.strip())
        return ret

    
    def close(self):
        self.pico.close()


    def __del__(self):
        self.pico.close()