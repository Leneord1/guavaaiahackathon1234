"""Diagnostic information provider catalog."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Provider:
    id: str
    name: str
    category: str
    portal_url: str


PROVIDERS = (
    Provider("alldata", "ALLDATA", "Aftermarket", "https://my.alldata.com/"),
    Provider("identifix", "Identifix", "Aftermarket", "https://www.identifix.com/"),
    Provider("prodemand", "Mitchell 1 ProDemand", "Aftermarket", "https://www.prodemand.com/"),
    Provider("ford", "Ford Motorcraft Service", "Manufacturer", "https://www.motorcraftservice.com/"),
    Provider("gm", "GM ACDelco TDS", "Manufacturer", "https://www.acdelcotds.com/"),
    Provider("stellantis", "Stellantis wiTECH", "Manufacturer", "https://www.witechsystem.com/"),
    Provider("toyota", "Toyota TIS", "Manufacturer", "https://techinfo.toyota.com/"),
    Provider("honda", "Honda TechInfo", "Manufacturer", "https://techinfo.honda.com/"),
    Provider("nissan", "Nissan TechInfo", "Manufacturer", "https://www.nissan-techinfo.com/"),
    Provider("hyundai_kia", "Hyundai/Kia Service", "Manufacturer", "https://www.hyundaitechinfo.com/"),
    Provider("bmw", "BMW AOS", "Manufacturer", "https://aos.bmwgroup.com/"),
    Provider("mercedes", "Mercedes-Benz XENTRY", "Manufacturer", "https://xentry.mercedes-benz.com/"),
    Provider("vw_audi", "Volkswagen/Audi erWin", "Manufacturer", "https://erwin.vw.com/"),
    Provider("custom", "Custom provider", "Custom", ""),
)


def provider_by_id(provider_id: str) -> Provider:
    """Find provider or reject unknown ID."""
    for provider in PROVIDERS:
        if provider.id == provider_id:
            return provider
    raise KeyError(provider_id)
