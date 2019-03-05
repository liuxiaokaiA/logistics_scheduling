gene_data = {
    514: [1569, 1550, 1587, 1771],
    393: [1743],
    266: [261, 320, 348],
    282: [121, 131],
    418: [946, 947, 952],
    293: [710, 668, 811, 779, 781],
    295: [667, 780, 800],
    296: [857, 825, 826],
    427: [347],
    300: [1087, 1150, 1181, 1172],
    436: [1928, 1926, 1897, 2013, 2044, 2043],
    309: [1517, 1518, 1519],
    311: [1621, 1611, 1640, 1613],
    312: [1654, 1662, 1669, 1676, 1682],
    315: [1848, 1855, 1856, 1859],
    319: [2077, 2081],
    328: [420],
    428: [586, 587, 572, 574],
    331: [108, 101, 537, 511, 1492],
    334: [740, 763],
    350: [1568, 1549, 1785, 1792],
    357: [150, 1953, 1954],
    363: [163],
    365: [314, 333, 1374, 1353],
    369: [456, 463, 498, 494, 509, 495],
    370: [573],
    246: [1352, 1354, 1419],
    377: [860, 914],
    379: [1451],
    381: [1039, 1115],
    383: [1190, 1235, 2080, 2054]
}


def change_gene(gene_data):
    order_data = {}
    gene_data_ok = {}
    for key in gene_data:
        for order in gene_data[key]:
            if order not in order_data:
                order_data[order] = []
            order_data[order].append(key)
    for order in order_data:
        # print order, order_data[order]
        if order_data[order][0] not in gene_data_ok:
            gene_data_ok[order_data[order][0]] = []
        gene_data_ok[order_data[order][0]].append(order)
    return gene_data_ok

if __name__ == '__main__':
    print count(gene_data)
