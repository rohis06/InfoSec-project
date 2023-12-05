import whois
import dns.resolver
from datetime import datetime

def get_domain_age(domain):
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        age = (datetime.now() - creation_date).days
        return age
    except Exception as e:
        print(f"Error getting domain age: {e}")
        return None

domain = "www.ucdavis.com"

age = get_domain_age(domain)
print(f"Domain Age: {age} days")
