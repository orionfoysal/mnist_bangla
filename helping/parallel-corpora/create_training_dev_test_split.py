import csv
import operator
import codecs
import sys
import os
import getopt
import random

# This program reads in the CSV files resulting from a translation HIT
# and optionally a dictionary HIT, and partitions the data into training /
# dev / test sets.  It assumes that there are 4 multiple tranlsations for
# each source segment, and makes sure that the same source segments don't 
# get included in both the training and the dev+test.
#
# Usage: python create_training_dev_test_split.py 2010-12-02\ -\ Translate\ Malayalam\ -\ images\ -\ length\ 10\ -\ Batch_390902_batch_results.csv ../../dict/2010-11-15\ -\ Malayalam\ Bilingual\ Dictionary\ -\ Batch_373206_batch_results.csv

def read_lines_from_file(filename):
   lines = []
   input_file = codecs.open(filename, encoding='utf-8')
   for line in input_file:
      lines.append(line.rstrip('\n'))
   input_file.close()
   return lines

def write_lines_to_file(output_filename, lines):
    output_file = codecs.open(output_filename, 'w', encoding='utf-8')
    for line in lines:
        output_file.write(line)
        output_file.write('\n')
    output_file.close()


filename = sys.argv[1]
csv_reader = csv.reader(open(filename))

print "Reading translation CSV from", filename

header_index = {}
for i, header in enumerate(csv_reader.next()):
   header_index[header] = i

hits = []
for hit in csv_reader:
    if hit[header_index['AssignmentStatus']] != 'Rejected':
        hits.append(hit)

seg_id_hash = {}
source_sentences = {}
segments = {}
turkers = {}
for hit in hits:
   for i in range(1, 11):
      seg_id = hit[header_index['Input.seg_id' + str(i)]]
      seg_id_hash[seg_id] = 1
      source = hit[header_index['Input.seg' + str(i)]]
      source_sentences[seg_id] = source
      translation = hit[header_index['Answer.translation' + str(i)]]
      translation = translation.replace('\n', ' ')
      translation = translation.replace('\r', ' ')
      translation = translation.replace('\t', ' ')
      translation = translation.replace('Translation of the first sentence goes here.', '')
      translation = translation.replace('Translation of the second sentence goes here.', '')
      translation = translation.replace('Translation of the first sentence goes here', '')
      translation = translation.replace('Translation of the second sentence goes here', '')
      worker = hit[header_index['WorkerId']]
      translations = []
      workers = []
      if seg_id in segments:
         translations = segments[seg_id]
         workers = turkers[seg_id]
      translations.append(translation)
      workers.append(worker)
      segments[seg_id] = translations
      turkers[seg_id] = workers


lines = []
for seg_id in seg_id_hash.keys():
   line = ''.decode('utf-8')
   if seg_id in segments:
      line = unicode(seg_id)
      source = source_sentences[seg_id]
      line = line + '\t' + source.decode('utf-8')
      if len(segments[seg_id]) == 4:
         for translation in segments[seg_id]:
            line = line + '\t' + translation.decode('utf-8')
         any_blanks = False
         for field in line.split('\t'):
            field = field.replace(' ', '')
            if field == '':
               any_blanks = True
         if not any_blanks:
            lines.append(line)


dev_set_size = min(1000, int(round(len(lines) * 0.1)))
test_set_size = min(1000, int(round(len(lines) * 0.1)))
random.shuffle(lines)

#lang_pair = hit[header_index['Input.lang_pair']]
lang_pair = 'ur-en'
(source_lang, target_lang) = lang_pair.split('-')

print "Collected translations for ", len(lines), "segments"   
dev_set = lines[0:dev_set_size]
test_set = lines[dev_set_size:(dev_set_size+test_set_size)]
training_set = lines[(dev_set_size+test_set_size):len(lines)]


def write_data_to_files(output_filename, lang_pair, lines, combine_translations=False):
   (source_lang, target_lang) = lang_pair.split('-')
   if combine_translations:
      seg_ids = []
      sources = []
      translations = []
      for line in lines:
         (seg_id, source, trans0, trans1, trans2, trans3) = line.split('\t')
         seg_ids.append(seg_id)
         seg_ids.append(seg_id)
         seg_ids.append(seg_id)
         seg_ids.append(seg_id)
         sources.append(source)
         sources.append(source)
         sources.append(source)
         sources.append(source)
         translations.append(trans0)
         translations.append(trans1)
         translations.append(trans2)
         translations.append(trans3)
      write_lines_to_file(lang_pair + "/" + output_filename + ".seg_ids", seg_ids)
      write_lines_to_file(lang_pair + "/" + output_filename + "." + source_lang, sources)
      write_lines_to_file(lang_pair + "/" + output_filename + "." + target_lang, translations)
   else:
      seg_ids = []
      sources = []
      translations = [[], [], [], []]
      for line in lines:
         (seg_id, source, trans0, trans1, trans2, trans3) = line.split('\t')
         seg_ids.append(seg_id)
         sources.append(source)
         translations[0].append(trans0)
         translations[1].append(trans1)
         translations[2].append(trans2)
         translations[3].append(trans3)
      write_lines_to_file(lang_pair + "/" + output_filename + ".seg_ids", seg_ids)
      write_lines_to_file(lang_pair + "/" + output_filename + "." + source_lang, sources)
      write_lines_to_file(lang_pair + "/" + output_filename + "." + target_lang + ".0", translations[0])
      write_lines_to_file(lang_pair + "/" + output_filename + "." + target_lang + ".1", translations[1])
      write_lines_to_file(lang_pair + "/" + output_filename + "." + target_lang + ".2", translations[2])
      write_lines_to_file(lang_pair + "/" + output_filename + "." + target_lang + ".3", translations[3])

if not os.path.isdir(lang_pair):
   os.makedirs(lang_pair)

write_data_to_files("training", lang_pair, training_set, combine_translations=True)
write_data_to_files("dev", lang_pair, dev_set)
write_data_to_files("test", lang_pair, test_set)

   
def extract_dictionary(dict_csv_file):
   dict_reader = csv.reader(open(dict_csv_file))
   headers = {}
   dictionary = {}
   for i, header in enumerate(dict_reader.next()):
      headers[header] = i
   for row in dict_reader:
      status = row[headers['AssignmentStatus']]
      if status == 'Approved':
         for i in range(1, 13):
            word = row[headers['Input.word_' + str(i)]].decode('utf8')
            translation = row[headers['Answer.translation_' + str(i) + '_1']].decode('utf8')
            if not word.replace(' ', '') == '' and not translation.replace(' ', '') == '':
               if not word in dictionary:
                  dictionary[word] = []
               dictionary[word].append(translation)
   return dictionary

# write out a dictionary if we have a dictionary HIT CSV
if len(sys.argv) > 2:
   dict_translation_filename = sys.argv[2]
   print "Reading dictionary CSV from", dict_translation_filename
   dictonary = extract_dictionary(dict_translation_filename)
   source_words = []
   translations = []
   for source_word in dictonary:
      for translation in dictonary[source_word]:
         source_words.append(source_word)
         translations.append(translation)
   write_lines_to_file(lang_pair + "/dict" + "." + source_lang, source_words)
   write_lines_to_file(lang_pair + "/dict" + "." + target_lang, translations)
   print "Wrote dictionary with", len(source_words), "words"
