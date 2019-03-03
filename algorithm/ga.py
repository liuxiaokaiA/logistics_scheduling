import random
import logging
import copy
from model.cost import compute_cost


SUCCESS = 1
FAILED = 0
log = logging.getLogger('default')
VALUE_MAX = 10000000


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

    def gene_to_data(self, order, key_order):
        gene_data = self.data
        count = 0
        all_data = {}

        for key_ in key_order:
            for value_ in order[key_]:
                if gene_data[count] == '1':
                    all_data[key_].append(value_)
                count += 1
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
        self.status = None

    def init_order(self, data, max_order, status):
        # order = { trunk: order}
        self.order = data
        self.key_order = list(self.order)
        self.max_order = max_order
        self.status = status

    def init_colony(self):
        self.colony = []
        while 1:
            if len(self.colony) >= self.colony_max_size:
                break
            str_ = ''
            for key_ in self.key_order:
                key_str = ''
                while 1:
                    key_str = ''
                    count = 0
                    for value in self.order[key_]:
                        num = random.randint(0, 1)
                        if num == 0:
                            key_str += '0'
                        else:
                            key_str += '1'
                            count += 1
                    if count <= self.max_order[key_]:
                        break
                str_ += key_str

            gene_temp = Gene()
            gene_temp.size = len(str_)
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

    def evaluate_gene(self, gene):
        gene.gene_to_data(self.order, self.key_order)
        compute_cost(gene)
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
        pos_ = []
        for i in range(4):
            pos_.append(random.randint(0, gene_size-1))
        pos_.sort()
        gene_new = Gene()
        for i in range(gene_size):
            if pos_:
                pos_temp = pos_[0]
            if ((i >= pos_[0]) and (i <= pos_[1])) or \
                    ((i >= pos_[2]) and (i <= pos_[3])):
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
                    pos = random.randrange(1,gene_size)
                    self.change_gene_data(gene,pos-1)
                result = self.evaluate_gene(gene)

    def evolution_loop(self):
        result = SUCCESS
        for times in range(EVOLUTION_MAX_TIME):
            max_ = 0
            offsprint = []
            self.mutation()
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
            # best_gene = self.selectBest()
            # log.error('times: '+str(times)+' max_: '+str(max_)+' best_gene: '+str(best_gene.value))
        return result

    def GA_main(self):
        self.init_order()
        times = 1
        while 1:
            self.init_colony()
            result = self.evolution_loop()
            if result == SUCCESS:
                break
            elif times == TRY_TIMES:
                log.error('error!!!! '+str(times)+' times')
                break
            times += 1

