import sys
import time
import logging
from bluepy import btle
from threading import Thread
from multiprocessing import Process, Queue
from gateway_brain import GatewayBrain
import struct

imu_prefix = b"\x00"
ir_sensor_prefix = b"\x01"
ir_emitter_prefix = b"\x02"

syn = b"\x65"
syn_ack = b'\x66'
syn_ack_ack = b"\x67"
data_ack = b"\x68"

handshake_timeout = 5
to_plot = False

beetle_service = "0000dfb0-0000-1000-8000-00805f9b34fb"
beetle_characteristic = "0000dfb1-0000-1000-8000-00805f9b34fb"

imu_beetle_address = ["30:E2:83:86:5C:6B", "30:E2:83:86:5C:6B"]
ir_sensor_beetle_address = ["30:E2:83:AE:52:B4", "B0:B1:13:2D:D4:8C"]
ir_emitter_beetle_address = ["50:F1:4A:DA:C8:38", "30:E2:83:AE:55:2C"]

beetle_reconnect_wait_time = 2

imu_log_file_name = "imu.process.log"
ir_sensor_log_file_name = "ir_sensor.process.log"
ir_emitter_log_file_name = "ir_emitter.process.log"

"""
HELPERS
"""


def split_even(item, split_num):
    return [item[i:i+split_num] for i in range(0, len(item), split_num)]


def connect(address, logger):
    try:
        p = btle.Peripheral(address)
        svc = p.getServiceByUUID(beetle_service)
        ch = svc.getCharacteristics(beetle_characteristic)[0]
    except:
        logger.warning("Couldn't find device. Retrying!")
        time.sleep(beetle_reconnect_wait_time)
        return connect(address, logger)
    return [p, svc, ch]


"""
HANDSHAKE
"""


class HandshakeHandler(btle.DefaultDelegate):
    data = b""

    def __init__(self, logger):
        btle.DefaultDelegate.__init__(self)
        self.logger = logger

    def handleNotification(self, cHandle, data):
        self.data = data
        self.logger.debug("Got response {}".format(data))


def send_syn(p, ch, handshake_handler, logger):
    logger.debug("Sending SYN")
    ch.write(syn)

    if p.waitForNotifications(handshake_timeout):
        if (handshake_handler.data == syn_ack):
            logger.debug("SYN acknowledged")
        else:
            logger.debug("SYN not acknowledged")
            send_syn(p, ch, handshake_handler, logger)
    else:
        send_syn(p, ch, handshake_handler, logger)


def handshake(p, ch, business_logic_handler, logger):
    handshake_handler = HandshakeHandler(logger)
    p.setDelegate(handshake_handler)
    send_syn(p, ch, handshake_handler, logger)

    logger.debug("Sending ACK")
    ch.write(syn_ack_ack)

    p.setDelegate(business_logic_handler)


"""
IMU PROCESS (UDT)
"""


def imu_process_function(q, team_num):
    logging.basicConfig(
        filename=imu_log_file_name,
        level=logging.DEBUG, filemode='w',
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    logger = logging.getLogger("IMULogger")
    # stdOutHandler = logging.StreamHandler(sys.stdout)
    # logger.addHandler(stdOutHandler)

    address = imu_beetle_address[team_num]
    session_timeout = 5

    [p, svc, ch] = connect(address, logger)

    class BusinessLogicHandler(btle.DefaultDelegate):
        remnants = b""

        def __init__(self):
            btle.DefaultDelegate.__init__(self)

        def handleNotification(self, cHandle, data):
            formatStr = ">" + "b"*len(data)
            # print(struct.unpack(formatStr, data))
            q.put(imu_prefix + self.remnants + data[:3 - len(self.remnants)])
            rest = data[3 - len(self.remnants):]
            split = split_even(rest, 3)

            if len(split) != 0:
                self.remnants = split.pop(-1)

            for packet in split:
                q.put(imu_prefix + packet)

    handshake(p, ch, BusinessLogicHandler(), logger)

    try:
        while True:
            if p.waitForNotifications(session_timeout):
                continue
            else:
                logger.warning("Session ended. Reconnnecting!")
                handshake(p, ch, BusinessLogicHandler(), logger)
    except:
        logger.error("Beetle Disconnected. Retrying connection!")
        time.sleep(beetle_reconnect_wait_time)
        return imu_process_function(q, team_num)


"""
IR PROCESS (RDT)
"""


def ir_process_function(is_sensor, q, team_num):
    logger = None

    address = ""
    if is_sensor:
        address = ir_sensor_beetle_address[team_num]
        logging.basicConfig(
            filename=ir_sensor_log_file_name,
            level=logging.DEBUG, filemode='w',
            format='%(asctime)s:%(levelname)s:%(message)s'
        )
        logger = logging.getLogger("IRSensorLogger")
    else:
        address = ir_emitter_beetle_address[team_num]
        logging.basicConfig(
            filename=ir_emitter_log_file_name,
            level=logging.DEBUG, filemode='w',
            format='%(asctime)s:%(levelname)s:%(message)s'
        )
        logger = logging.getLogger("IREmitterLogger")

    # stdOutHandler = logging.StreamHandler(sys.stdout)
    # logger.addHandler(stdOutHandler)

    session_timeout = 30

    [p, svc, ch] = connect(address, logger)

    class BusinessLogicHandler(btle.DefaultDelegate):
        data = b""

        def __init__(self):
            btle.DefaultDelegate.__init__(self)

        def handleNotification(self, cHandle, data):
            formatStr = ">" + "b"*len(data)
            print(struct.unpack(formatStr, data))
            if self.data == data:
                logger.warning("Duplicate detected. Previous ACK was lost")
            else:
                self.data = data
                if is_sensor:
                    q.put(ir_sensor_prefix + data)
                else:
                    q.put(ir_emitter_prefix + data)

            ch.write(data_ack)
    handshake(p, ch, BusinessLogicHandler(), logger)

    while True:
        try:
            if p.waitForNotifications(session_timeout):
                continue
            else:
                logger.warning("Session ended. Reconnnecting!")
                handshake(p, ch, BusinessLogicHandler(), logger)
        except:
            logger.warning("Beetle Disconnected. Retrying connection!")
            time.sleep(beetle_reconnect_wait_time)
            return ir_process_function(is_sensor, q, team_num)


"""
Queue Consumption Process
"""


def queue_consumption_process_function(send_external, q):
    def send_external_fn():
        gateway_brain = GatewayBrain()
        active_threads = []
        listener_thread = Thread(target=gateway_brain.listen_to_ultra_loop)
        active_threads.append(listener_thread)
        listener_thread.setDaemon(True)
        listener_thread.start()
        time.sleep(1)

        try:
            while True:
                gateway_brain.send_to_Ultra(
                    q.get(True),
                    to_plot
                    )
                time.sleep(0.001)
        except:
            gateway_brain.send_to_Ultra("bye")
            time.sleep(1)
            gateway_brain.terminate()

    if send_external:
        send_external_fn()
    else:
        while True:
            print(q.get(True))


if __name__ == '__main__':
    q = Queue()

    args = sys.argv

    team_num = int(args[1])
    if "--debug" in args or "-d" in args:
        stdOutHandler = logging.StreamHandler(sys.stdout)
        root = logging.getLogger()
        root.addHandler(stdOutHandler)

    if "imu" in args:
        imu_process = Process(target=imu_process_function, args=(q, team_num))
        imu_process.start()

    if "ir_sensor" in args:
        ir_sensor_process = Process(
            target=ir_process_function, args=(True, q, team_num))
        ir_sensor_process.start()

    if "ir_emitter" in args:
        ir_sensor_process = Process(
            target=ir_process_function, args=(False, q, team_num))
        ir_sensor_process.start()

    if "accelgyroviz" in args:
        to_plot = True

    send_external = False

    if "external" in args:
        send_external = True

    queue_consumption_process = Process(
        target=queue_consumption_process_function, args=(send_external, q))
    queue_consumption_process.start()
    queue_consumption_process.join()
