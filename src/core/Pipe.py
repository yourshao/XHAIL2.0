import sys
import logging as Logger



class Pipe(object):
    def __init__(self, source, target):
        if source is None:
            raise ValueError("Illegal 'source' argument in Pipe.__init__(Process, Process): " + str(source))
        if target is None:
            raise ValueError("Illegal 'target' argument in Pipe.__init__(Process, Process): " + str(target))
        self.input = source.stdin
        self.output = target.stdout

    def run(self):
        sys.stderr.write("I'm in!\n")
        try:
            buffer = bytearray(512)
            while True:
                sys.stderr.write(".")
                read_bytes = self.input.readinto(buffer)
                if read_bytes > 0:
                    self.output.write(buffer[:read_bytes])
                else:
                    break
            sys.stderr.write("\nI'm done.\n")
        except IOError as e:
            Logger.error("broken pipe between Gringo and Clasp")
        finally:
            try:
                self.input.close()
            except IOError as e:
                Logger.warning(False, "cannot close the pipe from Gringo")
                print(e)
            try:
                self.output.close()
            except IOError as e:
                Logger.warning(False, "cannot close the pipe to Clasp")
        sys.stderr.write("I'm leaving...\n")
