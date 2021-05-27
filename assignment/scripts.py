# importing necessary libraries
import os
import requests
from pyunpack import Archive
import numpy as np
import pandas as pd
import xml.etree.ElementTree as et
import nltk
from nltk.corpus import stopwords
from collections import Counter
import re


def unpack_7z(archive, path = None):
    '''
    Function that unpacks given 7z archive and returns path to the directory with unpacked files.
    archive - path to the archive to be unpacked.
    path - path to the directory which unpacked files will be saved in, if the directory does not exists it is created
             (on default directory in the same location as the archive and with the same name)
    '''
    # checking validity of the input
    if not isinstance(archive, str):
        raise TypeError('Path to the archive must a string.')
    if path is None:
        path = archive[:-3]
    elif not isinstance(path, str):
        raise TypeError('Path to a directory must be a string.')
    # if given directory does not exist, it is created
    if not os.path.exists(path):
        os.mkdir(path)
    # extracting files from given archives
    Archive(archive).extractall(path)
    return(path)

def parse_xml(xml_file):
    '''
    Function that parses given xml file to a data frame that is returned.
    xml_file - xml file to be parsed
    '''
    if not isinstance(xml_file, str):
        raise TypeError('Path to the file must be a string.')
    xtree = et.parse(xml_file)
    xroot = xtree.getroot()
    rows = []
    for elem in xroot:
        rows.append(elem.attrib)
    return pd.DataFrame(rows)

def parse_all_xmls(directory):
    '''
    Function that parses all xml files in given directory to data frames and returs a dictionary of frames.
    directory - path to the directory with xml files
    '''
    dfs = {}
    for filename in os.listdir(directory):
        if filename.endswith(".xml"): 
            dfs[filename[:-4]] = parse_xml(directory + '\\' + filename)
        else:
            continue
    return dfs

def unpack_all_7z(directory):
    '''
    Function that unpack all 7z files in given directory
    directory - path to the directory with 7z files
    '''
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(".7z"): 
            unpack_7z(directory + '\\' + filename)
            files.append(directory + '\\' + filename)
        else:
            continue
    return files

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def find_100_most_frequent_words_in_posts(postsXML_directory):
    '''
    Function that find 100 most frequent words in Posts.xml
    postsXML_directory - path to the file Posts.xml ex. 7zdatabase\hinduism.stackexchange.com\Posts.XML
    '''
    xtree = et.parse(postsXML_directory)
    xroot = xtree.getroot()
    df_cols = ["Id", "Body"]
    rows = []
    for node in xroot:
        s_id= node.attrib.get("Id")
        s_body = node.attrib.get("Body")
        # Clean html tags
        if s_body is not None:
            post_text = cleanhtml(s_body)
            # Remove \n sign
            text = re.sub(r'\n', ' ', post_text)
            rows.append({"Id": s_id, "Body": text})
    df = pd.DataFrame(rows, columns = df_cols)
    df_body = df['Body'].str.lower()
    # Make all words lowercase and add them to an array
    words_list = []
    for i in range(df_body.size):
        try:
            words_list.append( '{} '.format(df_body[i].lower()))
        except:
            None
    # Convert list to string
    words = ''
    words = words.join(words_list)
    # Find 100 most common words
    wd = pd.DataFrame(Counter(words.split()).most_common(200), columns=['word', 'frequency'])
    return wd

def show_most_frequent_words_graph(word_frequency_df):
    data = dict(zip(word_frequency_df['word'].tolist(), word_frequency_df['frequency'].tolist()))
    from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
    for word in STOPWORDS:
        if data.get(word) : data.pop(word)
    import matplotlib.pyplot as plt
    wc = WordCloud(background_color='white',
                stopwords=STOPWORDS,
                max_words=200).generate_from_frequencies(data)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()

d = find_100_most_frequent_words_in_posts(r"7zdatabase\hinduism.stackexchange.com\Posts.XML")
show_most_frequent_words_graph(d)