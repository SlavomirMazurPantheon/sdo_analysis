#!/usr/bin/env python

# Copyright The IETF Trust 2019, All Rights Reserved
# Copyright (c) 2018 Cisco and/or its affiliates.
# This software is licensed to you under the terms of the Apache License, Version 2.0 (the "License").
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# The code, technical concepts, and all information contained herein, are the property of Cisco Technology, Inc.
# and/or its affiliated entities, under various laws including copyright, international treaties, patent,
# and/or contract. Any use of the material herein must be in accordance with the terms of the License.
# All rights not expressly granted by the License are reserved.
# Unless required by applicable law or agreed to separately in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

__author__ = 'Benoit Claise'
__copyright__ = "Copyright(c) 2015-2018, Cisco Systems, Inc.,  Copyright The IETF Trust 2019, All Rights Reserved"
__license__ = "Apache V2.0"
__email__ = "bclaise@cisco.com"

import argparse
import configparser
import datetime
import json
import os
import re

import matplotlib as mpl

mpl.use('Agg')
from matplotlib.dates import date2num


# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------
def list_of_files_in_dir(srcdir, extension, debug_level):
    """
    Returns the list of file in a directory   
    :param srcdir: directory to search for files
    :param extension: file extension to search for
    :param debug_level: If > 0 print(some debug statements to the console
    :return: list of files
    """
    files = [f for f in os.listdir(srcdir) if os.path.isfile(os.path.join(srcdir, f))]
    yang_files = []
    for f in files:
        if f.endswith(extension):
            yang_files.append(f)
            if debug_level > 0:
                print("DEBUG: " + f + " in list_of_files_in_dir: ends with " + extension)
        else:
            if debug_level > 0:
                print("DEBUG: " + f + " in list_of_files_in_dir: doesn't ends with " + extension)
    return yang_files


def list_of_files_in_dir_created_after_date(files, srcdir, d, debug_level):
    """
    only select the files created wihin the number of days selected   
    :param files: list of files
    :param srcdir: directory to search for files
    :param d: number of days
    :param debug_level: If > 0 print(some debug statements to the console
    :return: list of files
    """
    new_files = []
    dt = datetime.datetime.utcnow()  # datetime now (all in UTC)
    if debug_level > 0:
        print(dt)
    delta = datetime.timedelta(d)  # x days interval
    dtdays = dt - delta  # datetime x days earlier than now
    dtdays = dtdays.date()
    if debug_level > 0:
        print(dtdays)
    for f in files:
        if debug_level > 0:
            print(srcdir + "/" + f)
        t_date = re.findall(r'\d+[_-]\d+[_-]\d+', f)[0]
        t_date = re.findall(r'\d+', t_date)
        dt = datetime.date(int(t_date[0]), int(t_date[1]), int(t_date[2]))  # time of last modification in seconds
        if dt >= dtdays:
            if debug_level > 0:
                print("Keep")
            new_files.append(f)
        else:
            if debug_level > 0:
                print("Dont keep")
    return new_files


def file_name_containing_keyword(drafts, keyword, debug_level):
    """
    Return the list of file whose name contains a specific keyword

    :param drafts: list of ietf drafts
    :param keyword: keyword for which to search
    :return: list of drafts containing the keyword
    """
    keyword = keyword.lower()
    drafts_with_keyword = []
    for f in drafts:
        if keyword in f.lower():
            if debug_level > 0:
                print("DEBUG: " + f + " in file_name_containing_keyword: contains " + keyword)
            drafts_with_keyword.append(f)
    if debug_level > 0:
        print("DEBUG: " + " in file_name_containing_keyword: drafts_with_keyword contains " + \
              str(drafts_with_keyword))
    drafts_with_keyword.sort()
    return drafts_with_keyword


def list_of_ietf_draft_containing_keyword(drafts, keyword, draftpath, debug_level):
    """
    Returns the IETF drafts that contains a specific keyword
    # status: troubleshooting done

    :param drafts: List of ietf drafts to search for the keyword
    :param keyword: Keyword to search for
    :return: List of ietf drafts containing the keyword
    """
    keyword = keyword.lower()
    list_of_ietf_draft_with_keyword = []
    for f in drafts:
        file_included = False
        for line in open(draftpath + f, 'r', encoding='utf-8'):
            if keyword in line.lower():
                file_included = True
                if debug_level > 0:
                    print("DEBUG: " + f + " in list_of_ietf_draft_containing_keyword: contains " + keyword)
                break
        if file_included:
            list_of_ietf_draft_with_keyword.append(f)
    if debug_level > 0:
        print("DEBUG: " + " in list_of_ietf_draft_containing_keyword: list_of_ietf_draft_with_keyword contains " \
              + str(list_of_ietf_draft_with_keyword))
    return list_of_ietf_draft_with_keyword


def write_dictionary_file_in_json(in_dict, path, file_name):
    """
    Create a file, in json, with my directory data
    For testing purposes.
    # status: in progress. 
    
    :param in_dict: The dictionary
    :param path: The directory where the json file with be created
    :param file_name: The file name to be created
    :return: None
    """
    with open(path + file_name, 'w', encoding='utf-8') as outfile:
        json.dump(in_dict, outfile, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=True)
    os.chmod(path + file_name, 0o664)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    bin_directory = os.environ['BIN']
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read('/etc/yangcatalog/yangcatalog.conf')
    web_private = config.get('Web-Section', 'private-directory')
    backup_directory = config.get('Directory-Section', 'backup')
    ietf_directory = config.get('Directory-Section', 'ietf-directory')

    parser = argparse.ArgumentParser(description='YANG Stats Extractor')
    parser.add_argument("--htmlpath", default=backup_directory + '/',
                        help="The path to get the HTML file (optional). Default is '" + backup_directory + "/'")
    parser.add_argument("--days", default="-1",
                        help="The numbers of days to get back in history. Default is all")
    parser.add_argument("--draftpathstrict", default=ietf_directory + "/draft-with-YANG-strict/",
                        help="The path to get the ietf drafts containing YANG model(s), with xym strict flag = True. Default is '" + ietf_directory + "/draft-with-YANG-strict/'")
    parser.add_argument("--draftpathnostrict", default=ietf_directory + "/draft-with-YANG-no-strict/",
                        help="The path to get the ietf drafts containing YANG model(s), with xym strict flag = False. Default is '" + ietf_directory + "/draft-with-YANG-no-strict/'")
    parser.add_argument("--draftpathdiff", default=ietf_directory + "/draft-with-YANG-diff/",
                        help="The path to put the ietf drafts containing YANG model(s), diff from flag = True and False. Default is '" + ietf_directory + "/draft-with-YANG-diff/'")
    parser.add_argument("--statspath", default=web_private + "/stats/",
                        help="The optional directory where to put the stats files . Default is '" + web_private + "/stats/'")
    parser.add_argument("--binpath", default=bin_directory,
                        help="Optional directory where to find the script executables. Default is '" + bin_directory + "'")
    parser.add_argument("--debug", type=int, default=0, help="Debug level; the default is 0")

    args = parser.parse_args()
    debug_level = args.debug

    category_list = ["FAILED", "PASSED WITH WARNINGS", "PASSED", "Email All Authors"]
    all_files = list_of_files_in_dir(args.htmlpath, "html", debug_level)

    # only select the files created wihin the number of days selected
    if int(args.days) > 0:
        files = list_of_files_in_dir_created_after_date(all_files, args.htmlpath, int(args.days), debug_level)
    else:
        files = all_files
    remove_old_html_files = []

    prefix = "YANGPageMain_"
    json_history_file = '{}/{}history.json'.format(args.htmlpath, prefix)
    yangPageCompilationStats = {}
    yangPageCompilationHistoricalStats = {}
    if os.path.isfile(json_history_file):
        with open(json_history_file, 'r') as f:
            yangPageCompilationStatsTemp = json.load(f)
            remove_keys = []
            for key, value in yangPageCompilationStatsTemp.items():
                yangPageCompilationStats[float(key)] = value
                remove_keys.append(key)
            del yangPageCompilationStatsTemp

    for f in file_name_containing_keyword(files, prefix, debug_level):
        name = 0
        generated_at = 0
        passed = 0
        passed_with_warnings = 0
        failed = 0
        f_no_extension = f.split(".")[0]
        year = f_no_extension.split("_")[1]
        month = f_no_extension.split("_")[2]
        day = f_no_extension.split("_")[3]
        extracted_date = datetime.date(int(year), int(month), int(day))
        if (datetime.date.today() - extracted_date).days > 30:
            remove_old_html_files.append(args.htmlpath + f)
            yangPageCompilationHistoricalStats[date2num(extracted_date)] = {}
        i = 0
        for line in open(args.htmlpath + f):
            if i == 1:
                generated_at = line.split('on')[-1].split('by')[0].strip()
            elif i == 4:
                name = line.split('<LI>')[-1].split(' ')[0]
            elif i == 5:
                passed = int(line.split(':')[-1].split('/')[0])
            elif i == 6:
                passed_with_warnings = int(line.split(':')[-1].split('/')[0])
            elif i == 7:
                failed = int(line.split(':')[-1].split('/')[0])
            elif i == 8:
                i = 0
                if (datetime.date.today() - extracted_date).days > 30:
                    yangPageCompilationStats[date2num(extracted_date)] = {
                        "name": {"generated-at": generated_at,
                                 "passed": passed,
                                 "warnings": passed_with_warnings,
                                 "failed": failed}}
                yangPageCompilationStats[date2num(extracted_date)] = {"name": {"generated-at": generated_at,
                                                                               "passed": passed,
                                                                               "warnings": passed_with_warnings,
                                                                               "failed": failed}}
    if int(args.days) == -1:
        with open(json_history_file, 'w') as f:
            json.dump(yangPageCompilationStats, f)
        write_dictionary_file_in_json(yangPageCompilationStats, args.statspath, "YANGPageMainStats.json")

    prefix = "IETFYANGPageMain_"
    json_history_file = '{}/{}history.json'.format(args.htmlpath, prefix)
    yangPageCompilationStats = {}
    yangPageCompilationHistoricalStats = {}
    if os.path.isfile(json_history_file):
        with open(json_history_file, 'r') as f:
            yangPageCompilationStatsTemp = json.load(f)
            remove_keys = []
            for key, value in yangPageCompilationStatsTemp.items():
                yangPageCompilationStats[float(key)] = value
                remove_keys.append(key)
            del yangPageCompilationStatsTemp

    for f in file_name_containing_keyword(files, prefix, debug_level):
        total = 0
        passed_with_warnings = 0
        passed = 0
        badly_formated = 0
        examples = 0
        for line in open(args.htmlpath + f):
            if 'correctly extracted YANG models' in line:
                total = int(line.split(':')[-1])
            elif 'without warnings' in line:
                passed = int(line.split(':')[-1].split('/')[0])
            elif 'with warnings' in line:
                passed_with_warnings = int(line.split(':')[-1].split('/')[0])
            elif '(example, badly formatted, etc. )' in line:
                badly_formated = int(line.split(':')[-1])
            elif 'correctly extracted example YANG' in line:
                examples = int(line.split(':')[-1])
        f_no_extension = f.split(".")[0]
        year = f_no_extension.split("_")[1]
        month = f_no_extension.split("_")[2]
        day = f_no_extension.split("_")[3]
        extracted_date = datetime.date(int(year), int(month), int(day))
        if (datetime.date.today() - extracted_date).days > 30:
            remove_old_html_files.append(args.htmlpath + f)
            yangPageCompilationStats[date2num(extracted_date)] = {"total": total,
                                                                            "warnings": passed_with_warnings,
                                                                            'passed': passed,
                                                                            "badly formated": badly_formated,
                                                                            'examples': examples}
        yangPageCompilationStats[date2num(extracted_date)] = {"total": total,
                                                              "warnings": passed_with_warnings,
                                                              'passed': passed,
                                                              "badly formated": badly_formated,
                                                              'examples': examples}
    if int(args.days) == -1:
        with open(json_history_file, 'w') as f:
            json.dump(yangPageCompilationStats, f)
        write_dictionary_file_in_json(yangPageCompilationStats, args.statspath, "IETFYANGPageMainStats.json")

    backup_prefix = ['HydrogenODLPageCompilation_', 'HeliumODLPageCompilation_',
                     'LithiumODLPageCompilation_', 'IETFCiscoAuthorsYANGPageCompilation_',
                     'IETFDraftYANGPageCompilation_',
                     'IEEEStandardYANGPageCompilation_', 'IEEEExperimentalYANGPageCompilation_']
    # !!! there are two IEEE IEEEExperimentalYANGPageCompilation and IEEEStandardYANGPageCompilation_
    for prefix in backup_prefix:
        print('')
        print("Looking at the files starting with: " + prefix)
        print("FILENAME: NUMBER OF DAYS SINCE EPOCH, TOTAL YANG MODULES, PASSED, PASSEDWITHWARNINGS, FAILED")
        json_history_file = '{}/{}history.json'.format(args.htmlpath, prefix)
        yangPageCompilationStats = {}
        yangPageCompilationHistoricalStats = {}
        if os.path.isfile(json_history_file):
            with open(json_history_file, 'r') as f:
                yangPageCompilationStatsTemp = json.load(f)
                remove_keys = []
                for key, value in yangPageCompilationStatsTemp.items():
                    yangPageCompilationStats[float(key)] = value
                    remove_keys.append(key)
                del yangPageCompilationStatsTemp

        for f in file_name_containing_keyword(files, prefix, debug_level):
            failed_result = 0
            passed_result = 0
            passed_with_warning_result = 0
            total_result = 0
            for line in open(args.htmlpath + f, 'r'):
                if "FAILED" in line:
                    failed_result += 1
                elif "PASSED WITH WARNINGS" in line:
                    passed_with_warning_result += 1
                elif "PASSED" in line:
                    passed_result += 1
                elif ".txt" in line:
                    total_result += 1
            if "ODLPageCompilation_" in prefix:
                total_result = str(int(failed_result) + int(passed_with_warning_result) + int(passed_result))

            f_no_extension = f.split(".")[0]
            year = f_no_extension.split("_")[1]
            month = f_no_extension.split("_")[2]
            day = f_no_extension.split("_")[3]
            extracted_date = datetime.date(int(year), int(month), int(day))
            matplot_date = date2num(extracted_date)
            if (datetime.date.today() - extracted_date).days > 30:
                remove_old_html_files.append(args.htmlpath + f)
                yangPageCompilationStats[matplot_date] = {"total": total_result,
                                                                    "warning": passed_with_warning_result,
                                                                    "success": passed_result}
            yangPageCompilationStats[matplot_date] = {"total": total_result, "warning": passed_with_warning_result,
                                                      "success": passed_result}

        if int(args.days) == -1:
            if prefix == "IETFDraftYANGPageCompilation_":
                with open(json_history_file, 'w') as f:
                    json.dump(yangPageCompilationStats, f)
                write_dictionary_file_in_json(yangPageCompilationStats, args.statspath,
                                              "IETFYANGPageCompilationStats.json")
            else:
                with open(json_history_file, 'w') as f:
                    json.dump(yangPageCompilationStats, f)
                write_dictionary_file_in_json(yangPageCompilationStats, args.statspath,
                                              "{}Stats.json".format(prefix[:-1]))

    # Print the number of RFCs per date, and store the info into a json file
    IETFYANGOutOfRFC = {}
    prefix = "IETFYANGOutOfRFC_"
    print('')
    print("Looking at the files starting with :" + prefix)
    print("FILENAME: NUMBER OF DAYS SINCE EPOCH, NUMBER OF YANG MODELS IN RFCS")
    json_history_file = '{}/{}history.json'.format(args.htmlpath, prefix)
    yangPageCompilationStats = {}
    yangPageCompilationHistoricalStats = {}
    if os.path.isfile(json_history_file):
        with open(json_history_file, 'r') as f:
            yangPageCompilationStatsTemp = json.load(f)
            remove_keys = []
            for key, value in yangPageCompilationStatsTemp.items():
                yangPageCompilationStats[float(key)] = value
                remove_keys.append(key)
            del yangPageCompilationStatsTemp
    for f in file_name_containing_keyword(files, prefix, debug_level):
        rfc_result = 0
        for line in open(args.htmlpath + f):
            if '.yang' in line:
                rfc_result += 1
        f_no_extension = f.split(".")[0]
        year = f_no_extension.split("_")[1]
        month = f_no_extension.split("_")[2]
        day = f_no_extension.split("_")[3]
        extracted_date = datetime.date(int(year), int(month), int(day))
        if (datetime.date.today() - extracted_date).days > 30:
            remove_old_html_files.append(args.htmlpath + f)
            yangPageCompilationStats[date2num(extracted_date)] = {"total": rfc_result}
        IETFYANGOutOfRFC[date2num(extracted_date)] = {"total": rfc_result}
    # write IETFYANGOutOfRFC to a json file
    if int(args.days) == -1:
        with open(json_history_file, 'w') as f:
            json.dump(yangPageCompilationStats, f)
        write_dictionary_file_in_json(yangPageCompilationStats, args.statspath, "IETFYANGOutOfRFCStats.json")

    # determine the number of company authored drafts
    files = [f for f in os.listdir(args.draftpathstrict) if os.path.isfile(os.path.join(args.draftpathstrict, f))]
    files_no_strict = [f for f in os.listdir(args.draftpathnostrict) if
                       os.path.isfile(os.path.join(args.draftpathnostrict, f))]
    total_number_drafts = len(files)
    total_number_drafts_no_strict = len(files_no_strict)

    print()
    print("Print, per company, the number of IETF drafts containing YANG model(s)")
    print("Total numbers of drafts with YANG Model(s): " + str(total_number_drafts) + " - non strict rules: " + str(
        total_number_drafts_no_strict))
    print('')
    print("Yumarkworks: " + str(len(list_of_ietf_draft_containing_keyword(files, "@yumaworks.com", args.draftpathstrict,
                                                                          debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@yumaworks.com", args.draftpathnostrict,
                                                  debug_level))))
    print("Tail-f: " + str(len(list_of_ietf_draft_containing_keyword(files, "@tail-f.com", args.draftpathstrict,
                                                                     debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@tail-f.com", args.draftpathnostrict, debug_level))))
    print("Cisco: " + str(len(list_of_ietf_draft_containing_keyword(files, "@cisco.com", args.draftpathstrict,
                                                                    debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@cisco.com", args.draftpathnostrict, debug_level))))
    print("Huawei: " + str(len(list_of_ietf_draft_containing_keyword(files, "@huawei.com", args.draftpathstrict,
                                                                     debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@huawei.com", args.draftpathnostrict, debug_level))))
    print("Juniper: " + str(len(list_of_ietf_draft_containing_keyword(files, "@juniper.net", args.draftpathstrict,
                                                                      debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@juniper.net", args.draftpathnostrict,
                                                  debug_level))))
    print("Ericsson: " + str(len(list_of_ietf_draft_containing_keyword(files, "@ericsson.com", args.draftpathstrict,
                                                                       debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@ericsson.com", args.draftpathnostrict,
                                                  debug_level))))
    print("Alcatel-Lucent: " + str(len(
        list_of_ietf_draft_containing_keyword(files, "@alcatel-lucent.com", args.draftpathstrict,
                                              debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@alcatel-lucent.com", args.draftpathnostrict,
                                              debug_level))))
    print("Ciena: " + str(len(list_of_ietf_draft_containing_keyword(files, "@ciena.com", args.draftpathstrict,
                                                                    debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@ciena.com", args.draftpathnostrict, debug_level))))
    print("Brocade: " + str(len(list_of_ietf_draft_containing_keyword(files, "@brocade.com", args.draftpathstrict,
                                                                      debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@brocade.com", args.draftpathnostrict,
                                                  debug_level))))
    print("ZTE: " + str(len(list_of_ietf_draft_containing_keyword(files, "@zte.com", args.draftpathstrict,
                                                                  debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@zte.com", args.draftpathnostrict, debug_level))))
    print("Fujitsu: " + str(len(list_of_ietf_draft_containing_keyword(files, "@jp.fujitsu.com", args.draftpathstrict,
                                                                      debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@jp.fujitsu.com", args.draftpathnostrict,
                                                  debug_level))))
    print("Intel: " + str(len(list_of_ietf_draft_containing_keyword(files, "@intel.com", args.draftpathstrict,
                                                                    debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@intel.com", args.draftpathnostrict, debug_level))))
    print("Infinera: " + str(len(list_of_ietf_draft_containing_keyword(files, "@infinera.com", args.draftpathstrict,
                                                                       debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@infinera.com", args.draftpathnostrict,
                                                  debug_level))))
    print("Metaswitch: " + str(len(list_of_ietf_draft_containing_keyword(files, "@metaswitch.com", args.draftpathstrict,
                                                                         debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@metaswitch.com", args.draftpathnostrict,
                                                  debug_level))))
    print('')
    print("Google: " + str(len(list_of_ietf_draft_containing_keyword(files, "@google.com", args.draftpathstrict,
                                                                     debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@google.com", args.draftpathnostrict, debug_level))))
    print("Verizon: " + str(len(list_of_ietf_draft_containing_keyword(files, "@verizon.com", args.draftpathstrict,
                                                                      debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@verizon.com", args.draftpathnostrict,
                                                  debug_level))))
    print("AT&T: " + str(len(list_of_ietf_draft_containing_keyword(files, "@att.com", args.draftpathstrict,
                                                                   debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@att.com", args.draftpathnostrict, debug_level))))
    print("Telefonica: " + str(len(list_of_ietf_draft_containing_keyword(files, "@telefonica.com", args.draftpathstrict,
                                                                         debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@telefonica.com", args.draftpathnostrict,
                                                  debug_level))))
    print("Orange: " + str(len(list_of_ietf_draft_containing_keyword(files, "@orange.com", args.draftpathstrict,
                                                                     debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@orange.com", args.draftpathnostrict, debug_level))))
    print("BT: " + str(len(list_of_ietf_draft_containing_keyword(files, "@bt.com", args.draftpathstrict,
                                                                 debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@bt.com", args.draftpathnostrict, debug_level))))
    print("Level 3: " + str(len(list_of_ietf_draft_containing_keyword(files, "@level3.com", args.draftpathstrict,
                                                                      debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@level3.com", args.draftpathnostrict,
                                                  debug_level))))
    print("Comcast: " + str(len(list_of_ietf_draft_containing_keyword(files, "@cable.comcast.com", args.draftpathstrict,
                                                                      debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@cable.comcast.com", args.draftpathnostrict,
                                                  debug_level))))
    print("China Unicom: " + str(len(
        list_of_ietf_draft_containing_keyword(files, "@chinaunicom.cn", args.draftpathstrict,
                                              debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@chinaunicom.cn", args.draftpathnostrict,
                                              debug_level))))
    print("China Mobile: " + str(len(
        list_of_ietf_draft_containing_keyword(files, "@chinamobile.com", args.draftpathstrict,
                                              debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@chinamobile.com", args.draftpathnostrict,
                                              debug_level))))
    print("Microsoft: " + str(len(list_of_ietf_draft_containing_keyword(files, "@microsoft.com", args.draftpathstrict,
                                                                        debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "@microsoft.com", args.draftpathnostrict,
                                                  debug_level))))
    print("DT: " + str(len(list_of_ietf_draft_containing_keyword(files, "@telekom.de", args.draftpathstrict,
                                                                 debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@telekom.de", args.draftpathnostrict, debug_level))))
    print("Softbank: " + str(len(list_of_ietf_draft_containing_keyword(files, "softbank.co.jp", args.draftpathstrict,
                                                                       debug_level))) + " - non strict rules: " + str(
        len(list_of_ietf_draft_containing_keyword(files_no_strict, "softbank.co.jp", args.draftpathnostrict,
                                                  debug_level))))
    print('')
    print("Packet Design: " + str(len(
        list_of_ietf_draft_containing_keyword(files, "@packetdesign.com", args.draftpathstrict,
                                              debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@packetdesign.com", args.draftpathnostrict,
                                              debug_level))))
    print("Qosmos: " + str(len(list_of_ietf_draft_containing_keyword(files, "@qosmos.com", args.draftpathstrict,
                                                                     debug_level))) + " - non strict rules: " + str(len(
        list_of_ietf_draft_containing_keyword(files_no_strict, "@qosmos.com", args.draftpathnostrict, debug_level))))

    for f in remove_old_html_files:
        try:
            os.unlink(f)
        except:
            # ignore if the file does not exist
            pass

    # diff between files and files_no_strict lists
    files_diff = []
    for f in files_no_strict:
        if f not in files:
            files_diff.append(f)
            bash_command = "cp " + args.draftpathnostrict + f + " " + args.draftpathdiff
            temp_result = os.popen(bash_command).read()
            if debug_level > 0:
                print(
                    "DEBUG: " + " copy the IETF draft containing a YANG model in draft-with-YANG-diff:  error " + temp_result)
    if debug_level > 0:
        print(
            "DEBUG: " + " print the diff between files and files_no_strict lists, so the files with xym extraction issues: " + str(
                files_diff))
