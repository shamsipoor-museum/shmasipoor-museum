# Copyright 2023 MohammadMohsen Akbarpoor Darabi (M. MAD)

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import os
from os import path as osp
from pprint import pprint
from datetime import date
from typing import Optional, Union, Type, Callable, Tuple, Dict

from attrs import asdict, define, frozen, make_class, Factory
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
import frontmatter as fm

import blogger as b

PREFIX = "https://shamsipoor-museum.github.io/museum-website/"
FA_IR_PREFIX = PREFIX + "fa_IR/"
FA_IR_PARTS_PREFIX = FA_IR_PREFIX + "parts/"
FA_IR_SCIENTISTS_PREFIX = FA_IR_PREFIX + "scientists/"


#  ____       _            _   _     _
# / ___|  ___(_) ___ _ __ | |_(_)___| |_ ___
# \___ \ / __| |/ _ \ '_ \| __| / __| __/ __|
#  ___) | (__| |  __/ | | | |_| \__ \ |_\__ \
# |____/ \___|_|\___|_| |_|\__|_|___/\__|___/

# (slots=False) is there because we have to have access to __dict__, and
# __dict__ won't be available when using slots
@frozen
class ScientistTable:
    name: Optional[str] = None
    # birth_date: Optional[date] = None
    # birth_location: Optional[str] = None
    born: Optional[str] = None
    # death_date: Optional[date] = None
    # death_location: Optional[str] = None
    died: Optional[str] = None
    nationality: Optional[Union[str, tuple]] = None
    alma_mater: Optional[Union[str, tuple]] = None
    known_for: Optional[Union[str, tuple]] = None
    awards: Optional[Union[str, tuple]] = None
    tags: Optional[tuple] = None


@frozen(slots=False)
class ScientistData:
    title: Optional[str] = None
    header: Optional[str] = None
    pic: Optional[str] = None
    table: Optional[ScientistTable] = None
    bio_summary: Optional[Union[str, Tuple[str]]] = None
    bio: Optional[Union[str, Tuple[str]]] = None


@frozen
class ScientistsIndexRow:
    filename: str = ""
    link: str = ""
    scientist_title: str = ""  # There is also a title on top of the page
    # pic: str = ""
    table: Optional[ScientistTable] = None


#  ____            _
# |  _ \ __ _ _ __| |_ ___
# | |_) / _` | '__| __/ __|
# |  __/ (_| | |  | |_\__ \
# |_|   \__,_|_|   \__|___/


@frozen
class PartTable:
    name: str = ""
    manufacturing_date: int = 0
    category: str = ""
    manufacturer_name: str = ""
    manufacturer_country: str = ""


@frozen(slots=False)
class PartData:
    title: Optional[str] = None
    header: Optional[str] = None
    pic: Optional[str] = None
    table: Optional[PartTable] = None
    explanation_paragraphs: Optional[Union[str, Tuple[str]]] = None


@frozen
class PartsIndexRow:
    filename: str = ""
    link: str = ""
    part_title: str = ""  # There is also a title on top of the page
    # pic: str = ""
    table: Optional[PartTable] = None


#  ____       _            _   _     _         ____        _
# / ___|  ___(_) ___ _ __ | |_(_)___| |_ ___  |  _ \  __ _| |_ __ _
# \___ \ / __| |/ _ \ '_ \| __| / __| __/ __| | | | |/ _` | __/ _` |
#  ___) | (__| |  __/ | | | |_| \__ \ |_\__ \ | |_| | (_| | || (_| |
# |____/ \___|_|\___|_| |_|\__|_|___/\__|___/ |____/ \__,_|\__\__,_|


def fa_ir_scientists_extract_table_from_md(loaded_file: fm.Post) -> ScientistTable:
    return ScientistTable(
        name=loaded_file["name"],
        born=loaded_file["born"],
        died=loaded_file["died"],
        nationality=loaded_file["nationality"],
        alma_mater=loaded_file["alma_mater"],
        known_for=loaded_file["known_for"],
        awards=loaded_file["awards"],
        tags=loaded_file["tags"]
    )


def fa_ir_scientists_extract_data_from_md(dirpath, f) -> ScientistData:
    # f_text = b.read_file(osp.join(dirpath, f))
    # print(f_text)
    # fl = fm.loads(f_text)
    fl = fm.load(osp.join(dirpath, f))
    # print("[debug]", fl.__dict__)
    return ScientistData(
        title=fl["title"],
        header=fl["header"],
        pic=fl["pic"],
        table=fa_ir_scientists_extract_table_from_md(fl),
        bio=fl.content
    )


def fa_ir_scientists_extract_data(sec: b.SecSpec, exceptions: Tuple[str] = b.GE) -> Dict[str, ScientistData]:
    exceptions = b.compile_re_collection(exceptions)
    sd_dict = dict()
    for dirpath, dirnames, filenames in os.walk(sec.input_path):
        for f in filenames:
            if f.endswith(".md"):
                if b.search_re_collection(exceptions, f):
                    continue
                sd_dict[f] = sec.extract_data_from_md(dirpath, f)
    return sd_dict


def fa_ir_scientists_write_data(sec: b.SecSpec, sd_dict: Dict[str, ScientistData]):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.template_path)),
        autoescape=False  # select_autoescape()
    )
    template = env.get_template(osp.basename(sec.template_path))
    for filename in sd_dict:
        # print(osp.join(sec.output_path, filename.replace(".md", ".html")),
        #       pd_dict[filename], sep="\n---\n", end="\n----------\n")
        with open(osp.join(sec.output_path, filename.replace(".md", ".html")), mode="w") as f:
            f.write(template.render(sd_dict[filename].__dict__))


#  ____       _            _   _     _         ___           _
# / ___|  ___(_) ___ _ __ | |_(_)___| |_ ___  |_ _|_ __   __| | _____  __
# \___ \ / __| |/ _ \ '_ \| __| / __| __/ __|  | || '_ \ / _` |/ _ \ \/ /
#  ___) | (__| |  __/ | | | |_| \__ \ |_\__ \  | || | | | (_| |  __/>  <
# |____/ \___|_|\___|_| |_|\__|_|___/\__|___/ |___|_| |_|\__,_|\___/_/\_\


def fa_ir_scientists_extract_table_from_soup(soup: BeautifulSoup) -> ScientistTable:
    rows = [row.text.strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return ScientistTable(
        name=rows[0][1],
        born=rows[0][3],
        died=rows[1][1],
        nationality=rows[1][3],
        alma_mater=rows[2][1],
        known_for=rows[2][3],
        awards=rows[3][1],
        tags=rows[3][3]
    )


def fa_ir_scientists_extract_table_from_soup_no_escape(soup: BeautifulSoup) -> ScientistTable:
    rows = [str(row).strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return ScientistTable(
        name=rows[0][2][9:-5],  # removing "</b><br/>" from start and "</td>" from end
        born=rows[0][4][9:-5],
        died=rows[1][2][9:-5],
        nationality=rows[1][4][9:-5],
        alma_mater=rows[2][2][9:-5],
        known_for=rows[2][4][9:-5],
        awards=rows[3][2][9:-5],
        tags=rows[3][4][9:-5]
    )


def fa_ir_scientists_extract_index_row(dirpath: str, f: str) -> ScientistsIndexRow:
    path = osp.join(dirpath, f)
    f_text = b.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return ScientistsIndexRow(
        filename=f,
        link=f,
        scientist_title=soup.title.text,
        table=fa_ir_scientists_extract_table_from_soup(soup)
    )


def fa_ir_scientists_extract_index(sec: b.SecSpec, exceptions: Tuple[str] = b.GE) -> tuple:
    exceptions = b.compile_re_collection(exceptions)
    index = []
    for dirpath, dirnames, filenames in os.walk(sec.output_path):
        for f in filenames:
            if f.endswith(".html"):
                if b.search_re_collection(exceptions, f):
                    continue
                index.append(fa_ir_scientists_extract_index_row(dirpath, f))
    return tuple(index)


def fa_ir_scientists_write_index(sec: b.SecSpec, index: tuple, title="فهرست دانشمندان"):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    )
    template = env.get_template(osp.basename(sec.index_template_path))
    with open(osp.join(sec.output_path, sec.index_filename), mode="w") as f:
        f.write(template.render(title=title, index=index))


#  ____            _         ____        _
# |  _ \ __ _ _ __| |_ ___  |  _ \  __ _| |_ __ _
# | |_) / _` | '__| __/ __| | | | |/ _` | __/ _` |
# |  __/ (_| | |  | |_\__ \ | |_| | (_| | || (_| |
# |_|   \__,_|_|   \__|___/ |____/ \__,_|\__\__,_|


def fa_ir_parts_extract_table_from_md(loaded_file: fm.Post) -> PartTable:
    return PartTable(
        name=loaded_file["name"],
        manufacturing_date=loaded_file["manufacturing_date"],
        category=loaded_file["category"],
        manufacturer_name=loaded_file["manufacturer_name"],
        manufacturer_country=loaded_file["manufacturer_country"]
    )


def fa_ir_parts_extract_data_from_md(dirpath, f) -> PartData:
    fl = fm.load(osp.join(dirpath, f))
    # print("[debug]", fl.__dict__)
    return PartData(
        title=fl["title"],
        header=fl["header"],
        pic=fl["pic"],
        table=fa_ir_parts_extract_table_from_md(fl),
        explanation_paragraphs=fl.content
    )


def fa_ir_parts_extract_data(sec: b.SecSpec, exceptions: Tuple[str] = b.GE) -> Dict[str, PartData]:
    exceptions = b.compile_re_collection(exceptions)
    pd_dict = dict()
    for dirpath, dirnames, filenames in os.walk(sec.input_path):
        for f in filenames:
            if f.endswith(".md"):
                if b.search_re_collection(exceptions, f):
                    continue
                pd_dict[f] = sec.extract_data_from_md(dirpath, f)
    return pd_dict


def fa_ir_parts_write_data(sec: b.SecSpec, pd_dict: Dict[str, PartData]):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.template_path)),
        autoescape=False  # select_autoescape()
    )
    template = env.get_template(osp.basename(sec.template_path))
    for filename in pd_dict:
        # print(osp.join(sec.output_path, filename.replace(".md", ".html")),
        #       pd_dict[filename], sep="\n---\n", end="\n----------\n")
        with open(osp.join(sec.output_path, filename.replace(".md", ".html")), mode="w") as f:
            f.write(template.render(pd_dict[filename].__dict__))


#  ____            _         ___           _
# |  _ \ __ _ _ __| |_ ___  |_ _|_ __   __| | _____  __
# | |_) / _` | '__| __/ __|  | || '_ \ / _` |/ _ \ \/ /
# |  __/ (_| | |  | |_\__ \  | || | | | (_| |  __/>  <
# |_|   \__,_|_|   \__|___/ |___|_| |_|\__,_|\___/_/\_\


def fa_ir_parts_extract_table_from_soup(soup: BeautifulSoup) -> PartTable:
    rows = [row.text.strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return PartTable(
        name=rows[0][1],
        manufacturing_date=rows[0][3],
        category=rows[1][1],
        manufacturer_name=rows[1][3],
        manufacturer_country=rows[2][1]
    )


def fa_ir_parts_extract_table_from_soup_no_escape(soup: BeautifulSoup) -> PartTable:
    rows = [str(row).strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    # print(rows)
    return PartTable(
        name=rows[0][2][9:-5],  # removing "</b><br/>" from start and "</td>" from end
        manufacturing_date=rows[0][4][9:-5],
        category=rows[1][2][9:-5],
        manufacturer_name=rows[1][4][9:-5],
        manufacturer_country=rows[2][2][9:-5]
    )


def fa_ir_parts_extract_index_row(dirpath: str, f: str) -> PartsIndexRow:
    path = osp.join(dirpath, f)
    f_text = b.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return PartsIndexRow(
        filename=f,
        link=f,
        part_title=soup.title.text,
        table=fa_ir_parts_extract_table_from_soup(soup)
    )


def fa_ir_parts_extract_index(sec: b.SecSpec, exceptions: Tuple[str] = b.GE) -> tuple:
    exceptions = b.compile_re_collection(exceptions)
    index = []
    for dirpath, dirnames, filenames in os.walk(sec.output_path):
        for f in filenames:
            if f.endswith(".html"):
                if b.search_re_collection(exceptions, f):
                    continue
                index.append(fa_ir_parts_extract_index_row(dirpath, f))
    return tuple(index)


def fa_ir_parts_write_index(sec: b.SecSpec, index: tuple, title="فهرست قطعات"):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    )
    template = env.get_template(osp.basename(sec.index_template_path))
    with open(osp.join(sec.output_path, sec.index_filename), mode="w") as f:
        f.write(template.render(title=title, index=index))


#  ____                                  ____       _            _   _     _
# |  _ \ _____   _____ _ __ ___  ___ _  / ___|  ___(_) ___ _ __ | |_(_)___| |_ ___
# | |_) / _ \ \ / / _ \ '__/ __|/ _ (_) \___ \ / __| |/ _ \ '_ \| __| / __| __/ __|
# |  _ <  __/\ V /  __/ |  \__ \  __/_   ___) | (__| |  __/ | | | |_| \__ \ |_\__ \
# |_| \_\___| \_/ \___|_|  |___/\___(_) |____/ \___|_|\___|_| |_|\__|_|___/\__|___/


def fa_ir_scientists_extract_data_from_html(dirpath: str, f: str, markdownify: bool = False) -> ScientistData:
    path = osp.join(dirpath, f)
    f_text = b.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return ScientistData(
        title=soup.title.text,
        header=soup.h1.text,  # TODO
        pic=soup.img["src"],
        table=fa_ir_scientists_extract_table_from_soup_no_escape(soup),
        bio=str(
            soup.body.find("div", {"class": "fa-IR-explanation"})
        ).lstrip('<div class="fa-IR-explanation">').rstrip('</div>')
    )


#  ____                                  ____            _
# |  _ \ _____   _____ _ __ ___  ___ _  |  _ \ __ _ _ __| |_ ___
# | |_) / _ \ \ / / _ \ '__/ __|/ _ (_) | |_) / _` | '__| __/ __|
# |  _ <  __/\ V /  __/ |  \__ \  __/_  |  __/ (_| | |  | |_\__ \
# |_| \_\___| \_/ \___|_|  |___/\___(_) |_|   \__,_|_|   \__|___/


def fa_ir_parts_extract_data_from_html(dirpath: str, f: str, markdownify: bool = False) -> PartData:
    path = osp.join(dirpath, f)
    f_text = b.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    # ep = [p.text for p in e.find_all("p") for e in soup.body.find_all("div", {"class": "fa-IR-explanation"})]
    # ep = []
    # for e in soup.body.find_all("div", {"class": "fa-IR-explanation"}):
    #     for p in e.find_all("p"):
    #         # print(md(str(p)))
    #         ep.append(md(str(p)) if markdownify else p.text)
    return PartData(
        title=str(soup.title)[7:-8],
        header=str(soup.h1)[43:-5],  # TODO
        pic=soup.img["src"],
        table=fa_ir_parts_extract_table_from_soup_no_escape(soup),
        explanation_paragraphs=str(
            soup.body.find("div", {"class": "fa-IR-explanation"})
        ).lstrip('<div class="fa-IR-explanation">').rstrip('</div>')
    )


def fa_ir_write_data_to_md(pd: Union[ScientistData, PartData],
                           template: Template, path: str, mode: str = "w"):
    with open(path, mode) as f:
        f.write(template.render(pd.__dict__))


def generate_beautiful_qr_codes(sec: b.SecSpec, exceptions: Tuple[str] = b.GE,
                                qr_pages: bool = True,
                                qr_pages_exceptions: Tuple[str] = b.GE,
                                qr_pages_rows: int = 5, qr_pages_cols: int = 4,
                                qr_pages_filename_fmt: str = "qr_codes_{i}.html",
                                qr_pages_title_fmt: str = "QR Codes {i}",
                                dry_run: bool = False):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.qr_template_path)),
        autoescape=False  # select_autoescape()
    )
    template = env.get_template(osp.split(sec.qr_template_path)[1])

    b.generate_qr_imgs(sec, exceptions=exceptions, dry_run=dry_run)
    if qr_pages:
        pages = b.extract_qr_table(sec, rows=qr_pages_rows, cols=qr_pages_cols, exceptions=qr_pages_exceptions)
        # print(qr_pages_rows, qr_pages_cols)
        # pprint(pages)
        for i, table in enumerate(pages, start=1):
            # pprint(f'{sec.input_path = }; {table}; {[p + ".md" for p in table[0]]}')
            pprint(
                [
                    table,
                    [
                        sec.extract_data_from_md(
                            dirpath=sec.input_path,
                            f=p + ".md"
                        ).header
                        for p in table[0]
                    ]
                ])
            b.write_qr_table(
                [
                    table,
                    [
                        sec.extract_data_from_md(
                            dirpath=sec.input_path,
                            f=p + ".md"
                        ).header
                        for p in table[0]
                    ]
                ],
                template,
                osp.join(osp.join(sec.output_path, sec.qr_pages_dirname),
                         qr_pages_filename_fmt.format(i=i)),
                title=qr_pages_title_fmt.format(i=i)
            )


document_root = b.SecSpec(name="root", output_path="docs", url_prefix=PREFIX)
fa_ir_root = b.SecSpec(name="fa_ir", output_path="docs/fa_IR", url_prefix=FA_IR_PREFIX)
fa_ir_parts = b.SecSpec(
    name="fa_ir_parts",
    output_path="docs/fa_IR/parts",
    url_prefix=FA_IR_PARTS_PREFIX,
    input_path="scripts/original_content/fa_IR/parts",
    data_spec=PartData,
    template_path="scripts/templates/fa_IR/parts/parts_template.html",
    md_template_path="scripts/templates/fa_IR/parts/parts_template.md",
    extract_data=fa_ir_parts_extract_data,
    write_data=fa_ir_parts_write_data,
    extract_data_from_md=fa_ir_parts_extract_data_from_md,
    write_data_to_html=None,
    extract_data_from_html=fa_ir_parts_extract_data_from_html,
    write_data_to_md=fa_ir_write_data_to_md,
    index_template_path="scripts/templates/fa_IR/parts/parts_index_template.html",
    extract_index=fa_ir_parts_extract_index,
    write_index=fa_ir_parts_write_index,
    # qr_template_path="scripts/templates/fa_IR/parts/qr_pages_table_template.html",
    qr_template_path="scripts/templates/fa_IR/parts/qr_pages_triangle_template.html",
)
fa_ir_scientists = b.SecSpec(
    name="fa_ir_scientists",
    output_path="docs/fa_IR/scientists",
    url_prefix=FA_IR_SCIENTISTS_PREFIX,
    input_path="scripts/original_content/fa_IR/scientists",
    data_spec=ScientistData,
    template_path="scripts/templates/fa_IR/scientists/scientists_template.html",
    md_template_path="scripts/templates/fa_IR/scientists/scientists_template.md",
    extract_data=fa_ir_scientists_extract_data,
    write_data=fa_ir_scientists_write_data,
    extract_data_from_md=fa_ir_scientists_extract_data_from_md,
    write_data_to_html=None,
    extract_data_from_html=fa_ir_scientists_extract_data_from_html,
    write_data_to_md=fa_ir_write_data_to_md,
    index_template_path="scripts/templates/fa_IR/scientists/scientists_index_template.html",
    extract_index=fa_ir_scientists_extract_index,
    write_index=fa_ir_scientists_write_index,
    # qr_template_path="scripts/templates/fa_IR/scientists/qr_pages_table_template.html",
    qr_template_path="scripts/templates/fa_IR/scientists/qr_pages_triangle_template.html",
)
fa_ir_root.sub_specs = [fa_ir_parts, fa_ir_scientists]
document_root.sub_specs = [fa_ir_root]


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None):
    # b.generate_index(fa_ir_parts, exceptions=b.GE)
    b.generate(fa_ir_parts, content_exceptions=(
        r"index\.html", r"qr_codes_.+\.html", r"choke_987\.md",
        r"choke_7825-5\.md", r"crt_465_tester\(b&k\)\.md", r"miller_big_rf_trans\.md"
    ), qr_pages=False)
    generate_beautiful_qr_codes(fa_ir_parts, exceptions=b.GE,
                                qr_pages_exceptions=b.GE,
                                qr_pages_rows=1, qr_pages_cols=4)

    # b.generate_index(fa_ir_scientists, exceptions=b.GE)
    # b.generate(fa_ir_scientists)
    b.generate(fa_ir_scientists, qr_pages=False)
    generate_beautiful_qr_codes(fa_ir_scientists, exceptions=b.GE,
                                qr_pages_exceptions=b.GE,
                                qr_pages_rows=1, qr_pages_cols=4)


if __name__ == "__main__":
    main()
