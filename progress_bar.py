import sys
import time

class ProgressBar():
    def __init__(self, amount, width=3, length=80, padding=8):
        self.amount  = amount
        self.width   = width
        self.length  = length
        self.padding = padding

        self.display(0)

    def display(self, current, message=None):
        if current == 0:
            self.begin_time = time.time()
            self.last_time = self.begin_time
            current_len = 0
            rest_len = self.length
        elif (current == self.amount):
            current_len = self.length
            rest_len = -1
        else:
            current_len = self.length * current // self.amount
            rest_len = self.length - current_len

        sys.stdout.write(''.rjust(self.padding))
        sys.stdout.write(' {:>{width}}/{:>{width}}'.format(current, self.amount, width=self.width))
        sys.stdout.write(' [')
        for i in range(current_len):
            sys.stdout.write('=')
        if rest_len > 0:
            sys.stdout.write('>')
        for i in range(rest_len - 1):
            sys.stdout.write('.')
        sys.stdout.write(']')

        current_time = time.time()
        step_time = current_time - self.last_time
        self.last_time = current_time
        total_time = current_time - self.begin_time

        info = '  Step: {:} | Total: {}{}'.format(
            self.__time_format( step_time, minute=True, second=True, millisecond=True),
            self.__time_format(total_time, minute=True, second=True, millisecond=True, padding_zero_ms=True),
            (' | ' + message) if message else ''
        )

        sys.stdout.write(info + ('\r' if current < self.amount else '\n'))
        sys.stdout.flush()

    def __time_format(self, seconds_float, day=False, hour=False, minute=False, second=False, millisecond=False, padding_zero_ms=False):

        days = int(seconds_float / 3600 / 24)
        seconds_float = seconds_float - days * 3600 * 24

        hours = int(seconds_float / 3600)
        seconds_float = seconds_float - hours * 3600

        minutes = int(seconds_float / 60)
        seconds_float = seconds_float - minutes * 60

        seconds = int(seconds_float)
        milliseconds = int((seconds_float - seconds) * 1000)

        f = ''
        i = 1
        if day or (days > 0):
            f += '{:>2d}d'.format(days)
            i += 1
        if hour or (hours > 0 and i <= 2):
            f += '{:>2d}h'.format(hours)
            i += 1
        if minute or (minutes > 0 and i <= 2):
            f += '{:>2d}m'.format(minutes)
            i += 1
        if second or (seconds > 0 and i <= 2):
            f += '{:>2d}s'.format(seconds)
            i += 1
        if millisecond or (milliseconds > 0 and i <= 2):
            if not padding_zero_ms:
                f += '{:>3d}ms'.format(milliseconds)
            else:
                f += '{:0>3d}ms'.format(milliseconds)
            i += 1

        return f