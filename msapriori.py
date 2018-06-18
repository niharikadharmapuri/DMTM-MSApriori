import sys
import numpy
import itertools


def main():
    if len(sys.argv) > 1:
        parameter_filename = sys.argv[1]
        input_filename = sys.argv[2]
    else:
        parameter_filename = 'parameter-file.txt'
        input_filename = 'input-data.txt'

    T = parse_input_data(input_filename)

    # I = get_itemset(T)

    MS, SDC, cbt, must_have = parse_parameter_file(parameter_filename)

    result, item_count, support = MS_Apriori(T, MS, SDC)

    final = apply_restrictions(result, cbt, must_have)

    k = 1
    for itemset in final:
        if len(itemset) > 0:
            print("Frequent", str(k) + "-itemsets:")
            print()
            for i in itemset:
                #in the first level the item is only a string, else is a set
                if k == 1:
                    print(item_count[i], ": {" + str(i) + "}")
                else:
                    print(support[repr(i)], ":", repr(i).replace("[", "{").replace("]", "}").replace("'", ""))
                    if k == 2:
                        print("Tailcount =", item_count[i[-1]])
                    else:
                        if repr(i[1:]) in support:
                            print("Tailcount =", support[repr(i[1:])])
                        else:
                            print("Tailcount =", get_support(i[1:], T))

            print()
            print("Total number of", str(k) + "-itemsets =", len(itemset))
            print()
            print()

            k = k + 1

    return 0


def MS_Apriori(T, MS, SDC):
    phi = float(SDC)
#   all frequen itemset will be contained in F
    F =[[],[]]
    n = len(T)
    c_count = {}

    M = get_sorted_itemset(MS)
#   print("M",M)
    L, support = initial_pass(M, T, MS)

    for l in L:
        if (support[l] / n) >= float(MS['MIS('+ l +')']):
            F[1].append(l)

#   print("Frequent 1 itemsets", F[1])

    k = 2
    while True:
        F.append([])

        if k == 2:
            Ck = level2_candidate_gen(L, phi, support, n, MS)
        else:
            Ck = MScandidate_gen(F[k - 1], phi, n, support, MS)
            #print("Ck is", Ck)

        # print("Ck:", Ck)
        # For each transaction t in T
        # print("T", T)
        for t in T:
            # FIX
            # create a list of all possible subsets of size equal to c
            all_t = []
            for z1 in map(list, itertools.permutations(t, k)):
                all_t.append(z1)

            for c in Ck:
#WH
                if c in all_t:
                    if repr(c) in c_count:
                        c_count[repr(c)] = c_count[repr(c)] + 1
                    else:
                        c_count[repr(c)] = 1

                if c[1:] in all_t:
                    if repr(c[1:]) in c_count:
                        c_count[repr(c[1:])] = c_count[repr(c[1:])] + 1
                    else:
                        c_count[repr(c[1:])] = 1

        # print("c_count", c_count)
        for c in Ck:
            # only if I have a count on the itemset, if not, it means the count was zero
            if repr(c) in c_count:
                if (c_count[repr(c)]/n) >= MS['MIS(' + c[0] + ')']:
                    F[k].append(c)

        # if we found no more frequent itemsets, end the loop
        # print("k is:", k)
        if len(F[k]) == 0:
            break

        k = k + 1

    return F, support, c_count


def MScandidate_gen(F, phi, n, support, MS):
    C = []

    for f1, f2 in itertools.permutations(F, 2):
        # k_length is the number of elements on the previous k-1 itemset
        k_length = len(f1)
        # if
        # compare all elements except the last
        # compare if the last element of f1 is precedent to that of t2
        # compare if the last elements keep the MSD

        if (numpy.array_equal(f1[:-1], f2[:-1]) == True) and (f1[-1] > f2[-1]) and (abs((support[f1[-1]] / n) - (support[f2[-1]] / n)) <= phi):
            # join the two itemsets f1 and f2 (append last element of f2 to f1)
            if MS['MIS(' + f1[-1] + ')'] < MS['MIS(' + f2[-1] + ')']:
                c = f1 + [f2[-1]]
            else:
                c = f2 + [f1[-1]]
            # print("c", c)
            # print("c is", c, "C was", C)
            prune = False
            # print("C is now", C)
            for s in map(list, itertools.combinations(c, k_length)):
                if (c[0] in s) or ((support[c[1]]/n) == (support[c[0]]/n)):
                    if (s in F) == False:
                        # C.remove(c)
                        prune = True

            if prune == False:
                C.append(c)

    return C


def level2_candidate_gen(L, phi, support, n, MS):
    C = []

    # what does it mean "in the same order?"
    i = 0
    for l in L:
        if support[l]/n >= float(MS['MIS('+ l + ')']):
            # each item h in L that is after l
            for j in range(i + 1, len(L)):
                h = L[j]
                if (support[h]/n >= MS['MIS(' + l + ')']) and (abs(support[h]/n - support[l]/n) <= phi):
                    # QUESTION
                    # the candidate itemset must be sorted, right?
                    #C.append(sorted([l, h]))
                    C.append([l, h])
        i = i + 1

    return C


# INPUT:
#       items ordered by their minimum support (M)
#       list of transactions (T)
#       dictionary of minimum support for items (MS)
def initial_pass(M, T, MS):
    support = {}

    # initialize all items to 0
    for i in M:
        support[i] = 0

    # count the total number of transactions
    n = len(T)

    for t in T:
        for i in t:
            support[i] = support[i] + 1

    # print("support", support)

    # Follow the sorted order to find the first item i in M that
    # meets MIS(i). i is inserted into L. for each subsequent item j
    # in M after i, if j.count/n >= MIS(i), then j is also inserted into L,
    # where j.count is the support count of j, and n is the total number
    # of transactions in T
    L = []
    found_first = False
    # first_item = 0
    for item in M:
        if (found_first == True) and ((support[item] / n) >= float(MS['MIS('+first_item+')'])):
            L.append(item)

        if (found_first == False) and ((support[item] / n) >= float(MS['MIS('+item+')'])):
            found_first = True
            first_item = item
            L.append(item)
            #print("L", L[0])

    # print("MS", MS)
    # print("M", M)
    # print("L",L)

    return L, support

def apply_restrictions(result, cbt, must_have):
    final = []
    k = 0
    for level in result:
        final.append([])
        if len(level) > 0:
            for itemset in level:
                contains_required = False
                cbt_not_found = True

                #check if the itemset containts any of the 'must have'
                for mh in must_have:
                    #in the first level, each itemset is only one string
                    if k > 1:
                        if mh in itemset:
                            contains_required = True
                    else:
                        if mh == itemset:
                            contains_required = True

                #check if the itemset does not contain those who cannot be together
                for cbt_set in cbt:
                    for subset in itertools.permutations(itemset, len(cbt_set)):
                        if numpy.array_equal(cbt_set, subset) == True:
                            cbt_not_found = False

                # support empty parameters
                if must_have[0] == '':
                    contains_required = True

                if cbt[0][0] == '':
                    cbt_not_found = True

                if contains_required and cbt_not_found:
                    final[k].append(itemset)

        k = k + 1

    return final

# Will the results be the same if ties are broken in some other way?
def get_sorted_itemset(MS):
    M = []
    # print("MS", MS)
    for i in sorted(MS, key=MS.__getitem__):
        M.append(i[4:-1])

    # print("M",M)
    return M


def parse_input_data(input_filename):
    input_data = open(input_filename, "r")

    all_transactions = []
    for line in input_data.readlines():
        line = line.translate({ord(i):None for i in '{ }\n\r\t'})
        # QUESTION
        # should I add transactions with their items ordered?
        all_transactions.append(sorted(line.split(',')))

    input_data.close()

    return all_transactions


def get_itemset(T):
    I = []
    I.append(T)
    return I


def parse_parameter_file(parameter_filename):

    input_data = open(parameter_filename, "r")

    MS = {}
    for line in input_data.readlines():
        line = line.translate({ord(i):None for i in ' \n\r\t'})
        if line.startswith('MIS'):
            mis = line.split('=')
            MS[mis[0]] = float(mis[1])
        elif line.startswith('SDC'):
            #print("la linea es", line)
            mis = line.split('=')
            SDC = mis[1]
        elif line.startswith('cannot_be_together'):
            mis = line.split(':')
            cbt = list(groups.replace('}','').split(',') for groups in mis[1].replace(' ','').replace('{','').split('},'))
            # print("cbt", cbt)
        elif line.startswith('must'):
            must_have = line.split(':')
            must_have = list(item.replace(' ', '') for item in must_have[1].split('or'))
            # print("must_have", must_have)

    input_data.close()

    #print("MS", MS)
    #print("SDC", SDC)
    #print("cbt", cbt)
    #print("must_have", must_have)

    return MS, SDC, cbt, must_have

def get_support(itemset, T):
    support = 0
    for t in T:
        all_t = []
        for z in map(list, itertools.permutations(t, len(itemset))):
            all_t.append(z)


        if itemset in all_t:
            support = support + 1

    return support

def sort(I, MS):
    items = MS[0]
    M = sorted(items)
    return M


def init_pass(L, MS):
    return 0


main()