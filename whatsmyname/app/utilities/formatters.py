from typing import List
import csv


from whatsmyname.app.models.schemas.sites import SiteSchema


def to_csv(sites: List[SiteSchema], file_path: str) -> None:
    """
    Write out the data to a csv file format
    :param sites:
    :param file_path:
    :return:
    """
    field_names: List[str] = list(SiteSchema.schema()["properties"].keys())
    with open(file_path, "w") as fp:
        writer = csv.DictWriter(fp, fieldnames=field_names)
        writer.writeheader()
        site: SiteSchema
        for site in sites:
            writer.writerow(site.dict())


def to_json(sites: List[SiteSchema], file_path: str) -> None:
    """
    Write the sites to json file
    :param sites:
    :param file_path:
    :return:
    """
    with open(file_path, "w") as fp:
        fp.write("[")
        site: SiteSchema
        for site in sites:
            fp.write(site.json())
        fp.write("]")


def to_table(sites: List[SiteSchema], file_path: str) -> None:
    pass


