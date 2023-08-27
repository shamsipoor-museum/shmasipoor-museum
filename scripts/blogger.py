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
import re
from typing import Optional, Union, Type, Callable, Tuple

# from pprint import pprint
from attrs import asdict, define, frozen, make_class, Factory
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
import qrcode as qr

# ge = ("index.html", "qr_codes.html")
GE = (r"index\.html", r"qr_codes_.+\.html")


@define
class SecSpec:
    name: str
    output_path: str
    url_prefix: Optional[str] = None
    input_path: Optional[str] = None
    sub_specs: Optional[list] = None
    data_spec: Optional[Type] = None
    template_path: Optional[str] = None
    md_template_path: Optional[str] = None  # template_path is an html template
    extract_data: Optional[Callable] = None  # function to extract data_specs from files of input_path directory
    write_data: Optional[Callable] = None
    extract_data_from_md: Optional[Callable] = None  # DEPRECATED
    extract_data_from_html: Optional[Callable] = None  # DEPRECATED
    write_data_to_md: Optional[Callable] = None  # DEPRECATED
    write_data_to_html: Optional[Callable] = None  # DEPRECATED
    index_template_path: Optional[str] = None
    index_filename: str = "index.html"  # Are relative to output_path
    extract_index: Optional[Callable] = None
    write_index: Optional[Callable] = None
    qr_dirname: str = "qr_codes"  # Are relative to output_path
    qr_template_path: Optional[str] = None
    qr_pages_dirname: str = "qr_codes/pages"  # Are relative to output_path


def _generate_html(sec: SecSpec, exceptions: Tuple[str] = GE):  # DEPRECATED
    if sec.input_path is not None:
        for dirpath, dirnames, filenames in os.walk(sec.input_path):
            for f in filenames:
                if f.endswith(".md"):
                    if f in exceptions:
                        continue
                    sec.write_data_to_html(sec.extract_data_from_md)  # pseudo code
        for dirpath, dirnames, filenames in os.walk(sec.output_path):
            for f in filenames:
                if f.endswith(".html"):
                    if f in exceptions:
                        continue
                    sec.write_index(sec.extract_index)
    for s in sec.sub_specs:
        _generate_html(s)


def compile_re_collection(collection):
    # lazy approach with generator expression sucks and it will let
    # exceptional files to be generated for some reason
    # (search_re_collection does not seem to like it)
    return [re.compile(e) for e in collection]


def search_re_collection(collection, string):
    for p in collection:
        if p.search(string) is not None:
            return True
    return False


def generate_content(sec: SecSpec, exceptions: Tuple[str] = GE):
    """Just chaining two calls, passing 'sec.extract_data()' to 'sec.write_data()'"""
    if sec.input_path is not None:
        sec.write_data(sec, sec.extract_data(sec, exceptions=exceptions))


def generate_index(sec: SecSpec, exceptions: Tuple[str] = GE):
    """Just chaining two calls, passing 'sec.extract_index()' to 'sec.write_index()'"""
    if sec.input_path is not None:
        sec.write_index(sec, sec.extract_index(sec, exceptions=exceptions))


def generate_qr_imgs(sec: SecSpec, exceptions: Tuple[str] = GE, dry_run: bool = False):
    exceptions = compile_re_collection(exceptions)
    for dirpath, dirnames, filenames in os.walk(sec.output_path):
        for f in filenames:
            if f.endswith(".html"):
                if search_re_collection(exceptions, f):
                    continue
                f = osp.splitext(f)[0]
                if dry_run:
                    print(sec.url_prefix + f)
                else:
                    qrcode = qr.make(sec.url_prefix + f)
                    # print("[!!!]", osp.join(osp.join(sec.output_path, sec.qr_dirname), f + ".png"))
                    qrcode.save(osp.join(osp.join(sec.output_path, sec.qr_dirname), f + ".png"))


def extract_qr_table(sec: SecSpec, rows: int = 5, cols: int = 4,
                     exceptions: Tuple[str] = (r"index\.png", )) -> tuple:
    exceptions = compile_re_collection(exceptions)
    pages = []
    for dirpath, dirnames, filenames in os.walk(osp.join(sec.output_path, sec.qr_dirname)):
        for f in filenames:
            if f.endswith(".png"):
                if search_re_collection(exceptions, f):
                    continue
                if len(pages) == 0 or (len(pages[-1]) >= rows and len(pages[-1][-1]) >= cols):
                    pages.append([])
                table = pages[-1]
                # print("[$$$]", f, table)
                table_len = len(table)
                if table_len <= rows:
                    if (table_len == 0 or len(table[-1]) >= cols) and table_len + 1 <= rows:
                        table.append([])
                    if len(table[-1]) < cols:
                        table[-1].append(osp.splitext(osp.basename(f))[0])
    return tuple(pages)


def write_qr_table(data, template, path, mode="w", title="QR Codes"):
    with open(path, mode=mode) as f:
        f.write(template.render(title=title, table=data, enumerate=enumerate, len=len))


def generate_qr_codes(sec: SecSpec, exceptions: Tuple[str] = GE,
                      qr_pages: bool = True, qr_pages_exceptions: Tuple[str] = GE,
                      qr_pages_rows: int = 5, qr_pages_cols: int = 4,
                      qr_pages_filename_fmt: str = "qr_codes_{i}.html",
                      qr_pages_title_fmt: str = "QR Codes {i}", dry_run: bool = False):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.qr_template_path)),
        autoescape=select_autoescape()
    )
    template = env.get_template(osp.split(sec.qr_template_path)[1])

    generate_qr_imgs(sec, exceptions=exceptions, dry_run=dry_run)
    if qr_pages:
        pages = extract_qr_table(sec, rows=qr_pages_rows, cols=qr_pages_cols, exceptions=qr_pages_exceptions)
        # print(qr_pages_rows, qr_pages_cols)
        # pprint(pages)
        for i, table in enumerate(pages, start=1):
            write_qr_table(table, template,
                           osp.join(osp.join(sec.output_path, sec.qr_pages_dirname), qr_pages_filename_fmt.format(i=i)),
                           title=qr_pages_title_fmt.format(i=i))


def generate(sec: SecSpec, content_exceptions: Tuple[str] = GE,
             index: bool = True, index_exceptions: Tuple[str] = GE,
             qr: bool = True, qr_exceptions: Tuple[str] = GE,
             qr_pages: bool = True, qr_pages_exceptions: Tuple[str] = GE,
             qr_pages_rows: int = 5, qr_pages_cols: int = 4,
             qr_pages_filename_fmt: str = "qr_codes_{i}.html", qr_pages_title_fmt: str = "QR Codes {i}",
             args_pass_through: bool = True):
    if sec.input_path is not None:
        generate_content(sec, exceptions=content_exceptions)
        if index:
            generate_index(sec, exceptions=index_exceptions)
        if qr:
            generate_qr_codes(sec, qr_exceptions, qr_pages, qr_pages_exceptions,
                              qr_pages_rows, qr_pages_cols,
                              qr_pages_filename_fmt, qr_pages_title_fmt)
    if sec.sub_specs is not None:
        for s in sec.sub_specs:
            if args_pass_through:
                generate(s, content_exceptions=content_exceptions,
                         index=index, index_exceptions=index_exceptions,
                         qr=qr, qr_exceptions=qr_exceptions,
                         qr_pages=qr_pages, qr_pages_exceptions=qr_pages_exceptions,
                         qr_pages_rows=qr_pages_rows, qr_pages_cols=qr_pages_cols,
                         qr_pages_filename_fmt=qr_pages_filename_fmt,
                         qr_pages_title_fmt=qr_pages_title_fmt,
                         args_pass_through=args_pass_through)
            else:
                generate(s)


def read_file(path: str):
    with open(path, "r") as f:
        return f.read()


def main():
    print("This framework is not meant to be executed like a script!",
          "Please refer to the documentation on how to use this framework to",
          "generate static websites.", sep="\n")


if __name__ == "__main__":
    main()
