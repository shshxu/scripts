#!/usr/bin/env python

"""
Tool to validate documentation files about phonetic tables.

Validates the phonetic tables vocalizer_$lng_phonemes.htm located in
doc/suppl by comparing version information stored in these files with
version information retrieved from the official release page of the
L&H+ phonetic tables (http://twiki.nuance.com/bin/view/LR/LhTables or
\\gh-netapp01\releases\PhonemeTables).
"""

import sys
import os
import re
import urllib2
import urlparse
import zipfile
import codecs
import argparse
import traceback


def is_url(url):
  return urlparse.urlparse(url).scheme == 'http'


def version_to_num(major, minor):
  return int(major) * 100 + int(minor)


def version_num_to_str(num):
  return "%d.%d" % (int(num / 100), num % 100)


def extract_phontab_version_from_html(html_file):
  with codecs.open(html_file, 'r', 'utf-8') as file:
    for line in file:
      result = re.match('table version ([0-9]+).([0-9]+)', line.lower())
      if result:
        major = result.group(1)
        minor = result.group(2)
        return version_to_num(major, minor)
  return 0


def validate_phoneme_tables(doc_path, table_versions, ignore_languages):
  nr_issues = 0
  for root, dirs, files in os.walk(doc_path):
    for name in files:
      result = re.match('vocalizer_(.*)_phonemes.htm', name)
      if result:
        pathname = os.path.join(root, name).replace('\\', '/')
        sys.stdout.write("validating %s ... " % pathname)
        lng = result.group(1)
        if lng in table_versions:
          version = extract_phontab_version_from_html(pathname)
          if version:
            if version == table_versions[lng]:
              print "OK"
            elif version < table_versions[lng]:
              if ignore_languages and lng in ignore_languages:
                status = "IGNORED"
              else:
                status = "FAILED"
                nr_issues += 1
              print "%s (outdated, latest: %s, current: %s)" \
                % (status,
                   version_num_to_str(table_versions[lng]),
                   version_num_to_str(version))
            else:
              if ignore_languages and lng in ignore_languages:
                status = "IGNORED"
              else:
                status = "FAILED"
                nr_issues += 1
              print "FAILED (mismatch, latest: %s, current: %s)" \
                % (version_num_to_str(table_versions[lng]),
                   version_num_to_str(version))
        else:
          print "FAILED (no phonetic table found for '%s')" % lng
  if nr_issues > 0:
    print "FAILED, %d issues found." % nr_issues
  else:
    print "PASSED"
  return nr_issues


def download_phontabs(release_page):
  sys.stdout.write("reading %s ... " % release_page)
  page = urllib2.urlopen(release_page).readlines()
  sys.stdout.write("done\n")
  for line in page:
    result = re.match('.*all \(zip file\)[: ]*<a href="(.*)" target="_top">(.*)</a>.*', line)
    if result:
      zip_url = result.group(1)
      zip_name = result.group(2)
      sys.stdout.write("downloading %s ... " % zip_url)
      request = urllib2.urlopen(zip_url)
      with open(zip_name, 'wb') as file:
        file.write(request.read())
      sys.stdout.write("done\n")
      return zipfile.ZipFile(zip_name)


def extract_versions_from_phontab_candidates(candidates):
  table_versions = {}
  for name in candidates:
    result = re.match('symboltable_(.*)_v([0-9]+).([0-9]+)', name.lower())
    if result:
      lng = result.group(1)
      major = result.group(2)
      minor = result.group(3)
      num = version_to_num(major, minor)
      if (not lng in table_versions) or (num > table_versions[lng]):
        table_versions[lng] = num
  return table_versions


def phontab_candidates_from_zip(zip_file):
  return zip_file.namelist()


def phontab_candidates_from_path(path):
  candidates = []
  for root, dirs, files in os.walk(path):
    for name in files:
      candidates.append(name)
  return candidates


def validate(doc_path, rls_path, ignore_languages):
  if is_url(rls_path):
    zip_file = download_phontabs("http://twiki.nuance.com/bin/view/LR/LhTables")
    candidates = phontab_candidates_from_zip(zip_file)
    name = zip_file.filename
    zip_file.close()
    os.remove(name)
  else:
    candidates = phontab_candidates_from_path(rls_path)
  table_versions = extract_versions_from_phontab_candidates(candidates)
  return validate_phoneme_tables(doc_path, table_versions, ignore_languages)


def create_arg_parser():
  """Create argument parser for commands and options."""

  parser = argparse.ArgumentParser(
      description="Validate documentation files about phonetic tables.")

  parser.add_argument(
      'tables_location',
      help="path to the local phonetic table documentation files")

  default_release_location = 'http://twiki.nuance.com/bin/view/LR/LhTables'
  parser.add_argument(
      'release_location', nargs='?',
      default=default_release_location,
      help="URL to the release page of the L&H+ phonetic tables (default: %s), "
           "or the path to \\\\gh-netapp01\\releases\\PhonemeTables"
           % default_release_location)

  parser.add_argument(
      '--ignore', nargs='*', metavar='LNG',
      help="list of languages to be ignored")

  return parser


def main(argv):
  result = 1

  parser = create_arg_parser()
  args = parser.parse_args(argv)

  try:
    result = validate(args.tables_location, args.release_location, args.ignore)
  except:
    print("Unexpected error: %s" % sys.exc_info()[1])
    traceback.print_tb(sys.exc_info()[2])

  return result

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
