import ast
import time

import numpy as np

from collections import defaultdict
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

from instr.instrumentfactory import mock_enabled, GeneratorFactory, SourceFactory, MultimeterFactory, AnalyzerFactory
from measureresult import MeasureResult
from util.file import load_ast_if_exists, pprint_to_file


GIGA = 1_000_000_000
MEGA = 1_000_000
KILO = 1_000
MILLI = 1 / 1_000


class InstrumentController(QObject):
    pointReady = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        addrs = load_ast_if_exists('instr.ini', default={
            'Анализатор': 'GPIB1::18::INSTR',
            'P LO': 'GPIB1::6::INSTR',
            'P RF': 'GPIB1::20::INSTR',
            'Источник': 'GPIB1::3::INSTR',
            'Мультиметр': 'GPIB1::22::INSTR',
        })

        self.requiredInstruments = {
            'Анализатор': AnalyzerFactory(addrs['Анализатор']),
            'P LO': GeneratorFactory(addrs['P LO']),
            'P RF': GeneratorFactory(addrs['P RF']),
            'Источник': SourceFactory(addrs['Источник']),
            'Мультиметр': MultimeterFactory(addrs['Мультиметр']),
        }

        self.deviceParams = {
            'Модулятор': {
                'F': 1,
            },
        }

        self.secondaryParams = load_ast_if_exists('params.ini', default={
            'Plo': -5.0,
            'Flo_min': 0.6,
            'Flo_max': 6.6,
            'Flo_delta': 1.0,
            'is_Flo_div2': False,
            'Fmod_min': 1.0,   # MHz
            'Fmod_max': 501.0,   # MHz
            'Fmod_delta': 10.0,   # MHz
            'Uoffs': 250,   # mV
            'Usrc': 5.0,
            'sa_rlev': 10.0,
            'sa_scale_y': 10.0,
            'sa_span': 10.0,   # MHz
            'sa_avg_state': False,
            'sa_avg_count': 16,
            'sep_1': None,
            'u_min': 4.75,
            'u_max': 5.25,
            'u_delta': 0.05,
        })
        self._calibrated_pows_lo = load_ast_if_exists('cal_lo.ini', default={})
        self._calibrated_pows_rf = load_ast_if_exists('cal_rf.ini', default={})

        self._instruments = dict()
        self.found = False
        self.present = False
        self.hasResult = False
        self.only_main_states = False

        self.result = MeasureResult()

    def __str__(self):
        return f'{self._instruments}'

    def connect(self, addrs):
        print(f'searching for {addrs}')
        for k, v in addrs.items():
            self.requiredInstruments[k].addr = v
        self.found = self._find()

    def _find(self):
        self._instruments = {
            k: v.find() for k, v in self.requiredInstruments.items()
        }
        return all(self._instruments.values())

    def check(self, token, params):
        print(f'call check with {token} {params}')
        device, secondary = params
        self.present = self._check(token, device, secondary)
        print('sample pass')

    def _check(self, token, device, secondary):
        print(f'launch check with {self.deviceParams[device]} {self.secondaryParams}')
        self._init()
        return True

    def calibrate(self, token, params):
        print(f'call calibrate with {token} {params}')
        return self._calibrate(token, self.secondaryParams)

    def _calibrateLO(self, token, secondary):
        print('run calibrate LO with', secondary)

        gen_lo = self._instruments['P LO']
        sa = self._instruments['Анализатор']

        secondary = self.secondaryParams

        lo_pow_start = secondary['Plo_min']
        lo_pow_end = secondary['Plo_max']
        lo_pow_step = secondary['Plo_delta']
        lo_f_start = secondary['Flo_min'] * GIGA
        lo_f_end = secondary['Flo_max'] * GIGA
        lo_f_step = secondary['Flo_delta'] * GIGA

        lo_f_is_div2 = secondary['is_Flo_div2']

        sa_rlev = secondary['sa_rlev']
        sa_scale_y = secondary['sa_scale_y']
        sa_span = secondary['sa_span'] * MEGA

        pow_lo_values = [round(x, 3) for x in np.arange(start=lo_pow_start, stop=lo_pow_end + 0.002, step=lo_pow_step)] \
            if lo_pow_start != lo_pow_end else [lo_pow_start]
        freq_lo_values = [round(x, 3) for x in
                          np.arange(start=lo_f_start, stop=lo_f_end + 0.0001, step=lo_f_step)]

        sa.send(':CAL:AUTO OFF')
        sa.send(':SENS:FREQ:SPAN 1MHz')
        sa.send(f'DISP:WIND:TRAC:Y:RLEV 10')
        sa.send(f'DISP:WIND:TRAC:Y:PDIV 5')

        gen_lo.send(f':OUTP:MOD:STAT OFF')

        sa.send(':CALC:MARK1:MODE POS')
        sa.send(f':SENS:FREQ:SPAN {sa_span}Hz')
        sa.send(f'DISP:WIND:TRAC:Y:RLEV {sa_rlev}')
        sa.send(f'DISP:WIND:TRAC:Y:PDIV {sa_scale_y}')

        result = defaultdict(dict)
        for pow_lo in pow_lo_values:
            gen_lo.send(f'SOUR:POW {pow_lo}dbm')

            for freq in freq_lo_values:

                freq_gen = freq
                if lo_f_is_div2:
                    freq_gen *= 2

                if token.cancelled:
                    gen_lo.send(f'OUTP:STAT OFF')
                    time.sleep(0.5)

                    gen_lo.send(f'SOUR:POW {pow_lo}dbm')

                    gen_lo.send(f'SOUR:FREQ {lo_f_start}GHz')
                    raise RuntimeError('calibration cancelled')

                gen_lo.send(f'SOUR:POW {pow_lo}dbm')
                gen_lo.send(f'SOUR:FREQ {freq_gen}Hz')

                gen_lo.send(f'OUTP:STAT ON')
                gen_lo.send(f':RAD:ARB ON')

                if not mock_enabled:
                    time.sleep(0.5)

                sa.send(f':SENSe:FREQuency:CENTer {freq_gen}Hz')

                if not mock_enabled:
                    time.sleep(0.5)

                sa.send(f':CALCulate:MARKer1:X {freq_gen}Hz')
                pow_read = float(sa.query(':CALCulate:MARKer:Y?'))
                loss = abs(pow_lo - pow_read)
                if mock_enabled:
                    loss = 10

                print('loss: ', loss)
                result[pow_lo][freq_gen] = loss

        result = {k: v for k, v in result.items()}
        pprint_to_file('cal_lo.ini', result)

        gen_lo.send(f'OUTP:STAT OFF')
        sa.send(':CAL:AUTO ON')
        self._calibrated_pows_lo = result
        return True

    def _calibrateRF(self, token, secondary):
        print('run empty calibrate RF')

        result = dict()
        pprint_to_file('cal_rf.ini', result)

        self._calibrated_pows_rf = result
        return True

    def measure(self, token, params):
        print(f'call measure with {token} {params}')
        device, _ = params
        try:
            self.result.set_secondary_params(self.secondaryParams)
            self._measure(token, device)
            # self.hasResult = bool(self.result)
            self.hasResult = True  # HACK
        except RuntimeError as ex:
            print('runtime error:', ex)

    def _measure(self, token, device):
        param = self.deviceParams[device]
        secondary = self.secondaryParams
        print(f'launch measure with {token} {param} {secondary}')

        self._clear()
        self._measure_s_params(token, param, secondary)
        return True

    def _clear(self):
        self.result.clear()

    def _init(self):
        self._instruments['P LO'].send('*RST')
        self._instruments['P RF'].send('*RST')
        self._instruments['Источник'].send('*RST')
        self._instruments['Мультиметр'].send('*RST')
        self._instruments['Анализатор'].send('*RST')

    def _measure_s_params(self, token, param, secondary):

        def set_read_marker(freq):
            sa.send(f':CALCulate:MARKer1:X {freq}Hz')
            if not mock_enabled:
                time.sleep(0.01)
            return float(sa.query(':CALCulate:MARKer:Y?'))

        gen_lo = self._instruments['P LO']
        gen_mod = self._instruments['P RF']
        src = self._instruments['Источник']
        mult = self._instruments['Мультиметр']
        sa = self._instruments['Анализатор']

        lo_pow = secondary['Plo']
        lo_f_start = secondary['Flo_min'] * GIGA
        lo_f_end = secondary['Flo_max'] * GIGA
        lo_f_step = secondary['Flo_delta'] * GIGA

        lo_f_is_div2 = secondary['is_Flo_div2']

        mod_f_min = secondary['Fmod_min'] * MEGA
        mod_f_max = secondary['Fmod_max'] * MEGA
        mod_f_delta = secondary['Fmod_delta'] * MEGA
        mod_u_offs = secondary['Uoffs'] * MILLI
        mod_pow = lo_pow

        src_u = secondary['Usrc']
        src_i_max = 200   # mA

        sa_rlev = secondary['sa_rlev']
        sa_scale_y = secondary['sa_scale_y']
        sa_span = secondary['sa_span'] * MEGA
        sa_avg_state = 'ON' if secondary['sa_avg_state'] else 'OFF'
        sa_avg_count = secondary['sa_avg_count']

        mod_f_values = [
            round(x, 3)for x in
            np.arange(start=mod_f_min, stop=mod_f_max + 0.0002, step=mod_f_delta)
        ]

        freq_lo_values = [
            round(x, 3) for x in
            np.arange(start=lo_f_start, stop=lo_f_end + 0.0001, step=lo_f_step)
        ]

        gen_lo.send(f':OUTP:MOD:STAT OFF')
        gen_lo.send(f':RAD:ARB OFF')
        gen_lo.send(f':DM:IQAD:EXT:COFF {mod_u_offs}')

        src.send(f'APPLY p6v,{src_u}V,{src_i_max}mA')
        src.send('OUTPut ON')

        gen_lo.send(f':DM:IQAD ON')
        gen_lo.send(f':DM:STAT ON')

        gen_lo.send(f'SOUR:POW {lo_pow}dbm')
        gen_mod.send(f'SOUR:POW {mod_pow}dbm')

        sa.send(':CAL:AUTO OFF')
        sa.send(f':SENS:FREQ:SPAN {sa_span}')
        sa.send(f'DISP:WIND:TRAC:Y:RLEV {sa_rlev}')
        sa.send(f'DISP:WIND:TRAC:Y:PDIV {sa_scale_y}')
        sa.send(f'AVER:COUNT {sa_avg_count}')
        sa.send(f'AVER {sa_avg_state}')
        sa.send(':CALC:MARK1:MODE POS')

        gen_lo.send(f'OUTP:STAT ON')
        gen_mod.send(f'OUTP:STAT ON')

        if mock_enabled:
            with open('./mock_data/-5-0db.txt', mode='rt', encoding='utf-8') as f:
                index = 0
                mocked_raw_data = ast.literal_eval(''.join(f.readlines()))

        res = []
        for lo_freq in freq_lo_values:

            sa_freq = lo_freq

            if lo_f_is_div2:
                lo_freq *= 2

            gen_lo.send(f'SOUR:FREQ {lo_freq}')

            for mod_f in mod_f_values:

                if token.cancelled:
                    gen_mod.send(f'OUTP:STAT OFF')
                    gen_lo.send(f'OUTP:STAT OFF')

                    time.sleep(0.5)

                    src.send('OUTPut OFF')

                    gen_lo.send(f':DM:IQAD OFF')
                    gen_lo.send(f':DM:STAT OFF')
                    gen_lo.send(f'SOUR:POW {lo_pow}dbm')
                    gen_lo.send(f'SOUR:FREQ {lo_f_start}')

                    gen_mod.send(f'SOUR:FREQ {mod_f_min}')

                    sa.send(':CAL:AUTO ON')
                    raise RuntimeError('measurement cancelled')

                loss = 10

                gen_mod.send(f'SOUR:FREQ {mod_f}')

                if not mock_enabled:
                    time.sleep(0.8)

                sa.send(f':SENSe:FREQuency:CENTer {sa_freq}')

                if lo_f_is_div2:
                    f_out = sa_freq + mod_f
                    sa_p_out = set_read_marker(f_out)
                else:
                    f_out = sa_freq - mod_f
                    sa_p_out = set_read_marker(f_out)

                src_u_read = src_u
                src_i_read = float(mult.query('MEAS:CURR:DC? 1A,DEF'))

                raw_point = {
                    'lo_p': lo_pow,
                    'lo_f': lo_freq,
                    'mod_f': mod_f,
                    'src_u': src_u_read,   # power source voltage as set in GUI
                    'src_i': src_i_read,
                    'sa_p_out': sa_p_out,
                    'loss': loss,
                }

                if mock_enabled:
                    # TODO record new test data
                    raw_point = mocked_raw_data[index]
                    raw_point['loss'] = loss
                    raw_point['mod_f'] = mod_f
                    index += 1

                print(raw_point)
                res.append(raw_point)
                self._add_measure_point(raw_point)

        gen_mod.send(f'OUTP:STAT OFF')
        gen_lo.send(f'OUTP:STAT OFF')

        time.sleep(0.5)

        src.send('OUTPut OFF')

        gen_lo.send(f':DM:IQAD OFF')
        gen_lo.send(f':DM:STAT OFF')
        gen_lo.send(f'SOUR:POW {lo_pow}dbm')
        gen_lo.send(f'SOUR:FREQ {lo_f_start}')
        gen_mod.send(f'SOUR:FREQ {mod_f_min}')

        sa.send(':CAL:AUTO ON')

        if not mock_enabled:
            with open('out.txt', mode='wt', encoding='utf-8') as f:
                f.write(str(res))

        return res

    def _add_measure_point(self, data):
        print('measured point:', data)
        self.result.add_point(data)
        self.pointReady.emit()

    def saveConfigs(self):
        pprint_to_file('params.ini', self.secondaryParams)

    @pyqtSlot(dict)
    def on_secondary_changed(self, params):
        self.secondaryParams = params

    @property
    def status(self):
        return [i.status for i in self._instruments.values()]
