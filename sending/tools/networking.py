import smtplib
import dns.resolver


def create_smtp_connections(records):
    for record in records:
        record["conn"] = smtplib.SMTP("mail." + record["host"], 587)
        record["conn"].starttls()
        record["conn"].login(record["username"] + "@" + record["host"], record["password"])


def resolve_domain_to_mx_ips(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_ips = []
        for record in mx_records:
            a_records = dns.resolver.resolve(record.exchange, 'A')
            for a_record in a_records:
                mx_ips.append(a_record.address)
        return mx_ips
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        return []
