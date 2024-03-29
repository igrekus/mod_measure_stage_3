import os
import openpyxl
import random

from collections import defaultdict
from textwrap import dedent

import pandas as pd

from instr.const import *
from forgot_again.file import load_ast_if_exists, pprint_to_file, make_dirs, open_explorer_at
from forgot_again.string import now_timestamp


class MeasureResult:
    def __init__(self):
        self._primary_params = None
        self._secondaryParams = None
        self._raw = list()
        self._raw_current = list()
        self._report = dict()
        self._processed = list()
        self._processed_currents = list()
        self.ready = False

        self.data1 = defaultdict(list)
        self.data2 = dict()

        self.adjustment = load_ast_if_exists('adjust.ini', default=None)
        self._table_header = list()
        self._table_data = list()

    def __bool__(self):
        return self.ready

    def process(self):
        currents = [list(d.values()) for d in self._raw_current]
        self.data2[1] = currents
        self._processed_currents = currents

        self.ready = True
        self._prepare_table_data()

    def _process_point(self, data):
        lo_p = data['lo_p']
        lo_f = data['lo_f']
        mod_f = data['mod_f']

        src_u = data['src_u']
        src_i = data['src_i'] / MILLI

        out_loss = data['out_loss']
        sa_p_out = data['sa_p_out'] + out_loss

        if self.adjustment is not None:
            try:
                point = self.adjustment[len(self._processed)]
                sa_p_out += point['p_out']
            except LookupError:
                pass

        self._report = {
            'lo_p': lo_p,
            'lo_f': round(lo_f / GIGA, 3),
            'mod_f': round(mod_f / MEGA, 3),
            'out_loss': out_loss,

            'p_out': round(sa_p_out, 2),

            'src_u': src_u,
            'src_i': round(src_i, 2),
        }

        lo_f_label = lo_f / GIGA
        mod_f_label = mod_f / MEGA
        self.data1[lo_f_label].append([mod_f_label, sa_p_out])
        self._processed.append({**self._report})

    def clear(self):
        self._secondaryParams.clear()
        self._raw.clear()
        self._raw_current.clear()
        self._report.clear()
        self._processed.clear()
        self._processed_currents.clear()

        self.data1.clear()
        self.data2.clear()

        self.adjustment = load_ast_if_exists(self._primary_params.get('adjust', ''), default={})

        self.ready = False

    def set_secondary_params(self, params):
        self._secondaryParams = dict(**params)

    def set_primary_params(self, params):
        self._primary_params = dict(**params)

    def add_point(self, data):
        self._raw.append(data)
        self._process_point(data)

    def save_adjustment_template(self):
        if not self.adjustment:
            print('measured, saving template')
            self.adjustment = [{
                'lo_p': p['lo_p'],
                'lo_f': p['lo_f'],
                'p_out': 0,
            } for p in self._processed]
            pprint_to_file('adjust.ini', self.adjustment)

    @property
    def report(self):
        return dedent("""        Генератор:
        Pгет, дБм={lo_p}
        Fгет, ГГц={lo_f:0.2f}
        Fмод, МГц={mod_f:0.2f}
        Pпот, дБ={out_loss:0.2f}

        Источник питания:
        U, В={src_u}
        I, мА={src_i}

        Анализатор:
        Pвых, дБм={p_out:0.3f}
        """.format(**self._report))

    def export_excel(self):
        device = 'mod'
        path = 'xlsx'

        make_dirs(path)

        file_name = f'./{path}/{device}-pout-{now_timestamp()}.xlsx'
        df = pd.DataFrame(self._processed)

        df.columns = [
            'Pгет, дБм', 'Fгет, ГГц', 'Fмод. МГц',
            'Pпот, дБ',
            'Loss rf, дБм',
            'Uпит, В', 'Iпит, мА',
        ]
        df.to_excel(file_name, engine='openpyxl', index=False)

        self._export_current()

        open_explorer_at(os.path.abspath(file_name))

    def _export_current(self):
        device = 'mod'
        path = 'xlsx'

        file_name = f'./{path}/{device}-curr-{now_timestamp()}.xlsx'
        df = pd.DataFrame(self._processed_currents, columns=['Uпит, В', 'Iпот, мА'])

        df.to_excel(file_name, engine='openpyxl', index=False)

    def _prepare_table_data(self):
        table_file = self._primary_params.get('result', '')

        if not os.path.isfile(table_file):
            return

        wb = openpyxl.load_workbook(table_file)
        ws = wb.active

        rows = list(ws.rows)
        self._table_header = [row.value for row in rows[0][1:]]

        gens = [
            [rows[1][j].value, rows[2][j].value, rows[3][j].value]
            for j in range(1, ws.max_column)
        ]

        self._table_data = [self._gen_value(col) for col in gens]

    def _gen_value(self, data):
        if not data:
            return '-'
        if '-' in data:
            return '-'
        span, step, mean = data
        start = mean - span
        stop = mean + span
        if span == 0 or step == 0:
            return mean
        return round(random.randint(0, int((stop - start) / step)) * step + start, 2)

    def get_result_table_data(self):
        return list(self._table_header), list(self._table_data)
