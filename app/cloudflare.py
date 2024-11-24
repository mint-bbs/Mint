import ipaddress


class Cloudflare:
    addressList = []

    @classmethod
    def isCloudflareIP(cls, ip: str):
        for ipRange in cls.addressList:
            network = ipaddress.IPv4Network(ipRange, strict=False)
            if ipaddress.ip_address(ip) in network:
                return True
        return False
