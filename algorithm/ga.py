# -*- encoding: utf-8 -*-
import random
import logging
import copy
from model.cost import compute_cost
import numpy


SUCCESS = 1
FAILED = 0
log = logging.getLogger('default')
VALUE_MAX = 1000000000


def update_global(default_conf):
    global MAX_SIZE
    global EXCHANGE_MIN
    global MUTATION_COUNT
    global TRY_TIMES
    global EVOLUTION_MAX_TIME
    global OFFSPRING_MAX
    global NODE_MAX_RATE

    MAX_SIZE = default_conf['colony_size']
    EXCHANGE_MIN = default_conf['exchange_min']
    MUTATION_COUNT = default_conf['mutation_count']
    TRY_TIMES = default_conf['try_times']
    EVOLUTION_MAX_TIME = default_conf['evolution_max_time']
    OFFSPRING_MAX = default_conf['offspring_max']


class Gene:
    '''
    This is a class to represent individual(Gene) in GA algorithom
    '''
    def __init__(self):
        self.data = ''
        self.size = 0   # length of gene
        self.value = 0
        self.relative_value = 0
        self.gene_data = None

    def data_to_gene(self):
        result = SUCCESS
        return result

    '''
    def gene_to_data(self, order, key_order):
        gene_data = self.data
        count = 0
        all_data = {}

        for key_ in key_order:
            for value_ in order[key_]:
                if gene_data[count] == '1':
                    if key_ not in all_data:
                        all_data[key_] = []
                    all_data[key_].append(value_)
                count += 1
        self.gene_data = all_data
    '''

    def gene_to_data(self, gene_bits, order_list):
        gene_data = copy.deepcopy(self.data)
        count = 0
        all_data = {}
        # print len(gene_data)
        for key_ in order_list:
            # print gene_data
            all_data[key_] = int('0b'+gene_data[:gene_bits], 2)
            gene_data = gene_data[gene_bits:]
        self.gene_data = all_data


class GA:
    def __init__(self):
        self.colony = []
        self.colony_max_size = MAX_SIZE

        self.colony_size = 0
        self.gene_size = 0
        self.order = {}
        self.key_order = []
        self.max_order = {}
        self.gene_set = set()
        self.order_list = []
        self.trunk_list = []
        self.trunk_data = {}
        self.gene_bits = 15
        self.trunk_orders = None
        self.all_order = None

    def init_order(self, data, max_order):
        # order = { trunk: order}
        self.order = data
        self.key_order = list(self.order)
        self.max_order = max_order

    def init_order2(self, trunk_data, order_list):
        # order = { trunk: order}
        self.order_list = order_list
        self.trunk_list = list(trunk_data)
        self.trunk_data = trunk_data
        self.gene_bits = 15

    def init_colony(self):
        self.colony = []
        while 1:
            if len(self.colony) >= self.colony_max_size:
                break
            str_ = ''
            # print self.key_order
            # print self.order
            # print self.max_order
            for key_ in self.key_order:
                # print key_
                min_len = min(self.max_order[key_], len(self.order[key_]))
                num = random.randint(0, min_len)
                id_list = set()
                while 1:
                    if len(id_list) == num:
                        break
                    id_list.add(random.randint(0, len(self.order[key_])-1))
                key_str = ''
                for id in range(len(self.order[key_])):
                    if id in id_list:
                        key_str += '1'
                    else:
                        key_str += '0'
                str_ += key_str

            gene_temp = Gene()
            gene_temp.size = len(str_)
            # print gene_temp.size
            gene_temp.data = str_
            result = self.evaluate_gene(gene_temp)

            if result > 0:
                # print result
                if gene_temp.data not in self.gene_set:
                    self.gene_set.add(gene_temp.data)
                else:
                    continue
                self.colony.append(gene_temp)
            elif result == 0:
                self.colony.append(gene_temp)
            else:
                continue

    def get_one_var(self, str_):
        data = ''
        for i in range(self.gene_bits - len(str_)):
            data += '0'
        data += str_
        return data

    def add_empty_result(self, gene_size):
        data = ''
        for i in range(gene_size):
            data += '0'
        gene_temp = Gene()
        gene_temp.size = len(data)
        gene_temp.data = data
        result = self.evaluate_gene(gene_temp)
        if result > 0:
            self.colony.append(gene_temp)
        print 'gene_temp 000 : ', result

    def init_colony2(self):
        self.colony = []
        gene_size = 0
        while 1:
            if len(self.colony) >= self.colony_max_size:
                break
            str_ = ''
            # trunk_list, order_list
            arr = numpy.random.choice(self.trunk_list, size=len(self.trunk_list),
                                      replace=False, p=None)
            arr_len = len(self.trunk_list)
            chosen_trunk = set()
            chosen_ = {}
            # gene_data = {order_id: trunk_count]}
            # trunk_data[trunk_count] = trunk_id
            count = 0
            for order_ in self.order_list:
                if self.all_order[order_].class_of_delay_time == 3:
                    no_trunk = True
                    for trunk_count in arr:
                        if trunk_count in chosen_trunk:
                            continue
                        trunk_id = self.trunk_data[trunk_count]
                        if order_ in self.trunk_orders[trunk_id]:
                            b_trunk_id = bin(int(trunk_count))[2:]
                            str_ += self.get_one_var(b_trunk_id)
                            if trunk_id not in chosen_:
                                chosen_[trunk_id] = []
                            chosen_[trunk_id].append(order_)
                            chosen_trunk.add(trunk_count)
                            no_trunk = False
                            break
                    if no_trunk:
                        str_ += self.get_one_var('')
                else:
                    str_ += self.get_one_var('')
            gene_temp = Gene()
            gene_temp.size = len(str_)
            gene_size = len(str_)
            # print gene_temp.size
            gene_temp.data = str_
            # print str_, gene_size
            # print chosen_

            result = self.evaluate_gene(gene_temp)

            # print result, chosen_
            # import time
            # time.sleep(100)

            if result > 0:
                # print result
                if gene_temp.data not in self.gene_set:
                    self.gene_set.add(gene_temp.data)
                else:
                    continue
                self.colony.append(gene_temp)
            elif result == 0:
                self.colony.append(gene_temp)
            else:
                continue
        # self.add_empty_result(gene_size)

    '''
    def evaluate_gene(self, gene):
        gene.gene_to_data(self.order, self.key_order)
        compute_cost(gene)
        # print gene.value
        return gene.value
    '''

    def evaluate_gene(self, gene):
        gene.gene_to_data(self.gene_bits, self.order_list)
        compute_cost(gene, self.trunk_data, self.trunk_orders)
        # print gene.value
        return gene.value

    def change_gene_data(self,gene,pos):
        l = list(gene.data)
        l[pos] = '1' if l[pos] == '0' else '0'
        gene.data = ''.join(l)

    def selectBest(self):
        if not self.colony:
            log.error('error : no self.colony')
            return ''
        best_gene = copy.deepcopy(self.colony[0])
        # print best_gene.value
        for gene_temp in self.colony:
            # print 'gene_temp.value: '+str(gene_temp.value)+' best_gene.value: '+str(best_gene.value)
            if gene_temp.value < best_gene.value:
                best_gene = copy.deepcopy(gene_temp)
        return best_gene

    def selection(self, max_num):
        if not int(max_num):
            chosen = []
            max_ = len(self.colony)
            num = random.randint(0,max_-1)
            chosen.append(self.colony[num])
            while 1:
                num2 = random.randint(0,max_-1)
                if num2 == num:
                    continue
                else:
                    chosen.append(self.colony[num])
                    return chosen
        chosen = []
        max_num = int(max_num)
        num = random.randint(1,max_num)
        num1 = num
        for gene_ in self.colony:
            if num > gene_.relative_value:
                num -= gene_.relative_value
            else:
                chosen.append(gene_)
        while 1:
            num2 = random.randint(1, max_num)
            if num2 == num1:
                continue
            for gene_ in self.colony:
                if num2 > gene_.relative_value:
                    num2 -= gene_.relative_value
                else:
                    chosen.append(gene_)
                    return chosen

    def crossoperate(self, chosen):
        gene1 = chosen[0]
        gene2 = chosen[1]
        gene_size = gene1.size
        gene_bits_size = gene_size/self.gene_bits
        pos_ = []
        for i in range(4):
            pos_.append(random.randint(0, gene_bits_size-1))
        pos_.sort()
        gene_new = Gene()
        for i in range(gene_size):
            if ((i >= pos_[0] * self.gene_bits) and (i <= pos_[1] * self.gene_bits)) or \
                    ((i >= pos_[2] * self.gene_bits) and (i <= pos_[3] * self.gene_bits)):
                gene_new.data += gene2.data[i]
            else:
                gene_new.data += gene1.data[i]
        gene_new.size = gene_size
        return gene_new

    def mutation(self):
        num = len(self.colony)
        count = int(num/200)+1
        temp = set()
        best_gene = self.selectBest()
        for times in range(count):
            gene_num = random.randrange(0,num-1)
            if gene_num in temp:
                continue
            if best_gene == self.colony[gene_num]:
                continue
            temp.add(gene_num)
            gene = self.colony[gene_num]
            gene_size = gene.size
            result = -1
            while result < 0:
                for i in range(MUTATION_COUNT):
                    # print gene_size
                    pos = random.randrange(1, gene_size)
                    self.change_gene_data(gene,pos-1)
                result = self.evaluate_gene(gene)

    def evolution_loop(self):
        result = SUCCESS
        for times in range(EVOLUTION_MAX_TIME):
            max_ = 0
            offsprint = []
            # self.mutation()
            for gene_temp in self.colony:
                if max_ < gene_temp.value:
                    max_ = gene_temp.value
            sum = 0
            for gene_temp in self.colony:
                gene_temp.relative_value = max_ - gene_temp.value
                sum += gene_temp.relative_value
            best_gene = self.selectBest()
            if best_gene.value == 0:
                result = SUCCESS
                break
            if (times == 10) and (best_gene.value > VALUE_MAX):
                result = FAILED
                break
            gene_one = copy.deepcopy(best_gene)
            offsprint.append(gene_one)
            while len(offsprint) < OFFSPRING_MAX:
                chosen = self.selection(sum)
                gene_new = self.crossoperate(chosen)
                evaluate_data = self.evaluate_gene(gene_new)
                if evaluate_data >= 0:
                    '''
                    if gene_new.data not in gene_set:
                        #gene_set.add(gene_new.data)
                        pass
                    else:
                        continue
                    '''
                    offsprint.append(gene_new)
            offsprint.sort(cmp=None, key=lambda x: x.value, reverse=False)
            new_colony = []
            for i in range(self.colony_max_size):
                gene_temp = copy.deepcopy(offsprint[i])
                new_colony.append(gene_temp)
            self.colony = []
            self.colony = new_colony
            best_gene = self.selectBest()
            print('times: '+str(times)+' max_: '+str(max_)+' best_gene: '+str(best_gene.value))
        return result

    def GA_main(self, data, max_order):
        self.init_order(data, max_order)
        times = 1
        while 1:
            self.init_colony()
            log.info('init_colony down! start to evolution_loop')
            result = self.evolution_loop()
            if result == SUCCESS:
                break
            elif times == TRY_TIMES:
                log.error('error!!!! '+str(times)+' times')
                break
            times += 1

    def GA_main2(self, trunk_data, order_list, data, All_order):
        self.trunk_orders = data
        self.init_order2(trunk_data, order_list)
        self.all_order = All_order
        times = 1
        while 1:
            self.init_colony2()
            log.info('init_colony down! start to evolution_loop')
            result = self.evolution_loop()
            if result == SUCCESS:
                break
            elif times == TRY_TIMES:
                log.error('error!!!! '+str(times)+' times')
                break
            times += 1

