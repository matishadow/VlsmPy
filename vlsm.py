import getopt
import os
import sys

DOT_DELIMITER = '.'
COMMA_DELIMITER = ','
IP_V4_LENGTH = 32
NUMBER_OF_OCTS = IP_V4_LENGTH // 8
BITS_IN_OCT = 255


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def print_help():
    cls()
    print("VLSM subnetting tool for IPv4")
    print('')
    print("usage: vlsm.py -n network_address -m mask -h hosts")
    print("\n")
    print("Examples:")
    print("vlsm.py -n 192.168.1.0 -m 255.255.255.0 -h 100,50,25,5")
    print("vlsm.py -n 192.168.1.0 -m /24 -h 50,25,100,5")

    sys.exit(0)


def print_error(error):
    cls()
    print(error)
    print("If you need help type: vlsm.py --help")
    sys.exit(0)


def parse_input():
    if not len(sys.argv[1:]):
        print_help()

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "h:n:m:h",
                                   ["help", "network", "mask", "hosts"])
    except getopt.GetoptError as error:
        print_error(error)

    for o, a in opts:
        if o == "--help":
            print_help()
        elif o in ("-n", "--network"):
            network = a
        elif o in ("-m", "--mask"):
            mask = a
        elif o in ("-h", "--hosts"):
            hosts = a

    try:
        network, mask, hosts
    except NameError as error:
        print_error(error)

    return network, mask, hosts


def convert_input_to_array(data, delimiter):
    data = data.split(delimiter)
    data = list(map(int, data))
    return data


def convert_slash_mask_to_address(mask):
    address_mask = []

    mask = int(mask[1:])

    for i in range(NUMBER_OF_OCTS):
        if mask >= 8:
            address_mask.append(255)
            mask -= 8
        elif mask > 0:
            address_mask.append(int("1" * mask + "0" * (8 - mask), 2))
            mask = 0
        else:
            address_mask.append(0)

    return address_mask


def find_optimal_mask(host_demand):
    host_capacity = 0
    power = 1

    while host_capacity < host_demand:
        power += 1
        host_capacity = (2**power) - 2

    return convert_slash_mask_to_address("/" + str(IP_V4_LENGTH - power))


def calculate_next_network(current_network, current_mask):
    network_copy = list(current_network)
    mask_copy = list(current_mask)

    for i in range(NUMBER_OF_OCTS):
        mask_copy[i] ^= 255
        network_copy[i] += mask_copy[i]
    network_copy[NUMBER_OF_OCTS - 1] += 1

    for i in range(NUMBER_OF_OCTS - 1, -1, -1):
        if network_copy[i] > BITS_IN_OCT:
            if i == 0:
                raise Exception("Operation exceeded IPv4 range")
            network_copy[i] -= (BITS_IN_OCT + 1)
            network_copy[i - 1] += 1

    return network_copy


def calculate_networks(network, mask, hosts):
    result = []

    current_network = list(network)
    for host_number in hosts:
        current_mask = find_optimal_mask(host_number)
        result.append((current_network, current_mask))

        current_network = calculate_next_network(current_network, current_mask)

    return result


def main():
    network, mask, hosts = parse_input()

    network = convert_input_to_array(network, DOT_DELIMITER)
    hosts = convert_input_to_array(hosts, COMMA_DELIMITER)
    if mask[0] == '/' or mask[0] == '\\':
        mask = convert_slash_mask_to_address(mask)
    else:
        mask = convert_input_to_array(mask, DOT_DELIMITER)

    hosts.sort(reverse=True)
    calculated_networks = calculate_networks(network, mask, hosts)
    print(calculated_networks)

main()
