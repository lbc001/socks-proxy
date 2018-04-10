'''
get the host ip from the domain.
'''
import re
from dns import resolver
from .exceptions import NotExistDomainError, ReqFormatsError

def valid_domain_check(domain):
    '''
    check the domain is valid or not.
    '''
    return re.match("^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6}$", domain)

def valid_ip_check(ip):
    '''
    check the ip is valid or not.
    '''
    return re.match("^(([1-9]?\d|1\d\d|2[0-5][0-5]|2[0-4]\d)\.){3}([1-9]?\d|1\d\d|2[0-5][0-5]|2[0-4]\d)$", ip)

def get_the_dst_ip(req_string):
    '''
    get the dst ip from the request string.
    '''
    try:
        if valid_domain_check(req_string):
            return [dns_res.address for dns_res in resolver.query(req_string, 'A')]#A represents host address
        elif valid_ip_check(req_string):
            return req_string#represents the req_string is the dst ip
        else:
            raise ReqFormatsError("the request domain or ip is invalid.")
    except resolver.NXDOMAIN:
        raise NotExistDomainError("DNS query names not exist.")