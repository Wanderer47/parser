from aiopg.sa import SAConnection

from models import certified_taxi_drivers as cert_drivers
from models import cert_taxi_drivers_meta_data as cert_drivers_meta


class CertificateTaxiRepository():
    @classmethod
    async def add_data(cls, connector: SAConnection, cert_drivers: cert_drivers):
        connector.execute(cert_drivers_meta.insert().values(
            region = cert_drivers.region,
            name = cert_drivers.name,
            phone = cert_drivers.phone,
            addres = cert_drivers.addres
            ))
