import ipaddress


class Cloudflare:
    addressListv4 = []
    addressListv6 = []

    @classmethod
    def isCloudflareIP(cls, ip: str):
        for ipRange in cls.addressListv4:
            network = ipaddress.IPv4Network(ipRange, strict=False)
            if ipaddress.ip_address(ip) in network:
                return True
        for ipRange in cls.addressListv6:
            network = ipaddress.IPv6Network(ipRange, strict=False)
            if ipaddress.ip_address(ip) in network:
                return True
        return False
