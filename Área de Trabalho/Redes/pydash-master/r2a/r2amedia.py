from player import player
from player.parser import *
from r2a.ir2a import IR2A
import time
from statistics import mean

class r2amedia(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.time_request = 0
        self.throughputs = []
        self.qi = []
        pass

    def handle_xml_request(self, msg):

        self.request_time = time.perf_counter()

        self.send_down(msg)

    def handle_xml_response(self, msg):

        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        # Calcula a vazao
        self.response_time = time.perf_counter()
        t = self.response_time - self.request_time
        msg_size = msg.get_bit_length()
        self.throughputs.append(msg_size/t)

        # Salva para calcular posteriormente
        self.request_time = time.perf_counter()

        quality_list = self.parsed_mpd.get_qi()

        print(f'>>>>>>>>>>>>>>>>>>>> {quality_list}')

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        if len(self.throughputs) > 3:
            self.throughputs.pop(0)

        average = mean(self.throughputs)

        selected_qi = self.qi[8]
        for i in self.qi:
            if average > i:
                selected_qi = i

        print(f'-----------------------{selected_qi}')

        msg.add_quality_id(selected_qi)

        self.send_down(msg)

    def handle_segment_size_response(self, msg):

        # Calcula a vazao
        self.response_time = time.perf_counter()
        t = self.response_time - self.request_time
        msg_size = msg.get_bit_length()
        self.throughputs.append(msg_size / t)

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
