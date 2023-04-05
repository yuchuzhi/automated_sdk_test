import io
import logging
from pexpect.spawnbase import SpawnBase

LOGGER = logging.getLogger(__name__)


class SerialSpawn(SpawnBase):
    """Due to pyserial not support file descriptor for windows, fdspawn could not be used.
    This class implement a spawn for pyserial, all interfaces are defined from the base
    `SpawnBase`. For more information about the usage, please refer the pexpect documentation.

    Simple example:
        >>> from mcutk.pserial import Serial
        >>> ser = Serial('COM3', 9600)
        >>> spawn = ser.SerialSpawn()
        >>> spawn.write_expect("Waiting for power mode select..", timeout=3)
    """
    def __init__(self, serial, **kwargs):
        """
        Arguments:
            serial: {serial.Serial object}
            open: {boolean} open port if it is not open, default True
        """

        self.log_content = []
        if hasattr(serial, 'reader_isalive'):
            if serial.reader_isalive:
                serial.stop_reader()
                LOGGER.debug('reader thread is stopped!')

        if kwargs.get("encoding") is None:
            kwargs["encoding"] = "utf-8"


        self.auto_open = True
        if "open" in kwargs:
            self.auto_open = kwargs.pop("open")

        if 'codec_errors' not in kwargs:
            kwargs['codec_errors'] = "ignore"

        self.serial = serial
        super().__init__(**kwargs)
        self.log_buffer = io.StringIO()
        
        if self.auto_open:
            self.open()

        self.closed = not self.serial.is_open
        

    def open(self):
        """ Open serial port """

        if not self.serial.is_open:
            LOGGER.info("open port %s, baudrate: %s", self.serial, self.serial.baudrate)
            self.serial.open()

        return self

    def __str__(self):
        return str(self.serial) or f"SerialSpawn(port={self.serial.port})"

    def _log_read_data(self, data):
        """
        Save read data to internal buffers.
        """
        # save to spawn.logfile_read
        self._log(data, 'read')
        self.log_buffer.write(data)
        self.log_buffer.flush()

    def read_nonblocking(self, size=1, timeout=None):
        """This is fake nonblocking, the size is decided by how many data in the buffer,
        rather than specific value, this is because big size will block the serial read,
        small size will effect the performance when many data in buffer. timeout is useless.
        """
        raw = self.serial.read(self.serial.in_waiting or 1)
        str_data = self._decoder.decode(raw, final=False)
        self._log_read_data(str_data)
        return str_data

    def write(self, data):
        return self.serial.write(data)

    def flush(self):
        """
        Flush serial
        """
        self.serial.flush()

    def get_log(self):
        """
        Get the read log.
        """
        if not self.log_buffer:
            return

        self.log_buffer.seek(0)
        return self.log_buffer.read()

    def flush_log(self):
        """
        Flush logfile_read to a readable attribute: SerialSpawn.data
        """
        LOGGER.debug("dump reading log to serial object!")
        self.serial.append_data(self.get_log())

    def close(self):
        """Close serial port, and dump the logfile_read to mcutk.PSerial.data.
        If the serial instance is comes from pyserial, dump action will not take.
        """
        self.serial.close()
        self.flush_log()
        self.closed = True

    def isalive(self):
        """
        Return a boolean the port is open or not
        """
        return self.serial.is_open

    def gether_log(self):
        serial_log = ""
        if self.spawn.before:
            serial_log += self.spawn.before

        if self.spawn.after and isinstance(self.spawn.after, str):
            serial_log += self.spawn.after        

        self.log_content.append(serial_log)

    def test_expect(self, patterns, timeout):
        """ expect all patterns.

        Args:
            patterns ([list]): a list of expect pattern.
            timeout ([int]): timeout value.

        Returns:
            [int]: return result value.
        """
        index = self.expect(patterns, timeout=timeout)
        assert index == (len(patterns) - 1), "Not all patterns are matched. Fail match pattern:{}.".format(patterns[index])

        return 0
