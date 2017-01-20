import getopt
import os
import sys

DOT_DELIMITER = '.'
COMMA_DELIMITER = ','
INFO_TAG = "[*]"
IP_V4_LENGTH = 32
NUMBER_OF_OCTS = IP_V4_LENGTH // 8
BITS_IN_OCT = 255

verbose = False


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def print_help():
    print("VLSM subnetting tool for IPv4")
    print('')
    print("usage:\nvlsm.py -n network_address -m mask -h hosts\n")
    print("options:")
    print("-v\t Have vlsm.py give more verbose output.")
    print("\n")
    print("Examples:")
    print("vlsm.py -n 192.168.1.0 -m 255.255.255.0 -h 100,50,25,5")
    print("vlsm.py -n 192.168.1.0 -m /24 -h 50,25,100,5")

    sys.exit(0)


def print_error(error):
    print(error)
    print("If you need help type: vlsm.py --help")
    sys.exit(0)


def print_info(message):
    print("{0} {1} {2}".format(INFO_TAG, message, INFO_TAG))


def parse_input():
    global verbose
    if not len(sys.argv[1:]):
        print_help()

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "h:n:m:h:v",
                                   ["help", "network", "mask", "hosts", "verbose"])
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
        elif o in ("-v", "--verbose"):
            verbose = True

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
        host_capacity = (2 ** power) - 2

    return convert_slash_mask_to_address("/" + str(IP_V4_LENGTH - power))


def add_full_range(network, mask):
    network_copy = list(network)
    mask_copy = list(mask)

    for i in range(NUMBER_OF_OCTS):
        mask_copy[i] ^= 255
        network_copy[i] += mask_copy[i]
    return network_copy, mask_copy


def check_overflow(network):
    for i in range(NUMBER_OF_OCTS - 1, -1, -1):
        if network[i] > BITS_IN_OCT:
            if i == 0:
                raise Exception("Operation exceeded IPv4 range")
            network[i] -= (BITS_IN_OCT + 1)
            network[i - 1] += 1


def add_one_to_network(network):
    network[NUMBER_OF_OCTS - 1] += 1


def subtract_one_from_network(network):
    for i in range(NUMBER_OF_OCTS - 1, -1, -1):
        if network[i] != 0:
            network[i] -= 1
            break


def calculate_next_network(current_network, current_mask):
    network, mask = add_full_range(current_network, current_mask)
    add_one_to_network(network)
    check_overflow(network)

    return network


def is_network_valid(network_to_validate, whole_network, mask):
    for i in range(NUMBER_OF_OCTS):
        if network_to_validate[i] & mask[i] != whole_network[i]:
            return False

    return True


def calculate_networks(network, mask, hosts):
    whole_network = list(network)
    result = []

    current_network = list(network)
    for host_number in hosts:
        current_mask = find_optimal_mask(host_number)
        result.append((current_network, current_mask))

        current_network = calculate_next_network(current_network, current_mask)
        if not is_network_valid(current_network, whole_network, mask):
            raise Exception("Number of hosts exceeded capacity of given network")

    return result


def calculate_available_addresses(networks):
    networks_count = len(networks)
    available_addresses = []

    for i in range(networks_count):
        network_copy = list(networks[i][0])
        mask_copy = list(networks[i][1])

        broadcast_address = add_full_range(network_copy, mask_copy)[0]
        add_one_to_network(network_copy)
        check_overflow(network_copy)
        first_address = network_copy
        last_address = list(broadcast_address)
        subtract_one_from_network(last_address)

        available_addresses.append((first_address, last_address, broadcast_address))

    return available_addresses


def convert_ip_to_str(address):
    return DOT_DELIMITER.join(str(x) for x in address)


def print_result(networks, demanded_hosts, available_addresses):
    networks_count = len(networks)
    for i in range(networks_count):
        network = networks[i][0]
        mask = networks[i][1]
        broadcast = available_addresses[i][2]
        first_address = available_addresses[i][0]
        last_address = available_addresses[i][1]

        print("Network #{0} (demanded hosts:{1}):".format(i + 1, demanded_hosts[i]))
        print("Network address: {0}".format(convert_ip_to_str(network)))
        if verbose:
            print_ip_binary(network)
            print("")
        print("Network mask: {0}".format(convert_ip_to_str(mask)))
        if verbose:
            print_ip_binary(mask)
            print("")
        print("Broadcast address: {0}".format(convert_ip_to_str(broadcast)))
        if verbose:
            print_ip_binary(broadcast)
            print("")
        print("Available addresses for hosts: {0} - {1}".format(convert_ip_to_str(first_address),
                                                                convert_ip_to_str(last_address)))
        if verbose:
            print("First address:")
            print_ip_binary(first_address)
            print("Last address:")
            print_ip_binary(last_address)
            print("")
        print("")


def correct_network(address, mask):
    for i in range(NUMBER_OF_OCTS):
        address[i] = address[i] & mask[i]

    return address


def check_network(address, mask):
    if verbose:
        print_info("Checking network")

    network_is_valid = is_network_valid(address, address, mask)
    if not network_is_valid:
        print("[!] Mask does not cover the whole network [!]")
        print("[!] Attempting to correct the mask by ANDing Network and MASK [!]")
        print("\n")
        address = correct_network(address, mask)

    if verbose and network_is_valid:
        print_info("Network is valid")
        print("\n")
    return address


def convert_oct_to_bin(oct):
    oct = bin(oct)[2:]
    l = len(oct)
    if l < 8:
        oct = "0" * (8 - l) + oct
    return oct


def print_ip_decimal(ip):
    s = convert_ip_to_str(ip)
    print(s)


def print_ip_binary(ip):
    s = DOT_DELIMITER.join(convert_oct_to_bin(i) for i in ip)
    print(s)


def print_ip(ip, is_decimal_form, is_binary_form):
    if is_decimal_form:
        print_ip_decimal(ip)
    if is_binary_form:
        print_ip_binary(ip)


def print_arguments(network, mask):
    print_info("Given network:")
    print_ip(network, True, True)
    print("")

    print_info("Given mask:")
    print_ip(mask, True, True)
    print("\n")


def main():
    cls()
    network, mask, hosts = parse_input()

    network = convert_input_to_array(network, DOT_DELIMITER)
    hosts = convert_input_to_array(hosts, COMMA_DELIMITER)
    if mask[0] == '/' or mask[0] == '\\':
        mask = convert_slash_mask_to_address(mask)
    else:
        mask = convert_input_to_array(mask, DOT_DELIMITER)
    if verbose:
        print_arguments(network, mask)

    network = check_network(network, mask)

    hosts.sort(reverse=True)

    if verbose:
        print_info("Calculating networks")
        print("")
    calculated_networks = calculate_networks(network, mask, hosts)
    available_addresses = calculate_available_addresses(calculated_networks)
    print_result(calculated_networks, hosts, available_addresses)


main()
