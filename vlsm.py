import os
import sys


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


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


def main():
    if not len(sys.argv[1:]):
        print_help()


main()
