#! /usr/bin/python

'''
    chmod +x extract.py
    Use: extract.py [hocr file] | bash

    Create an images directory as a subdirectory of the path to the hocr file.
    Place the cropped images there, identified by their id.
    Generate a csv file with heading
        id, title, bbox A, bbox B, bbox C, bbox D, x_wconf, word


    for the hocr file use
      the argument
    no argument
      the one .hocr file in the directory,
      or choose among the many

    The program finds the image file based on the hocr information
'''

import os
import sys
import glob
import HTMLParser

clip = lambda a,mn,mx: min(max(a,mn),mx)

class HOCRParser(HTMLParser.HTMLParser):

    def __init__(self, text, csvouf):
        HTMLParser.HTMLParser.__init__(self)
        csvouf.write('{}\n'.format(self.title()))
        self.csvouf = csvouf
        self.go = False
        self.feed(text)

    def __bool__(self):  # python3
        return self.go

    __nonzero__ = __bool__  # python2

    def title(self):
        return '{}, {}, {}, {}, {}, {}, {}, {}'.format(
            'id', 'title', 'bbox A', 'bbox B', 'bbox C', 'bbox D', 'x_wconf', 'word'
        )

    def __str__(self):
        try:
            result = '{}, {}, {}, {}, {}, {}, {}, {}'.format(
                self.id, self.TITLE, self.a, self.b, self.c, self.d, self.x_wconf, self.word
            )
        except:
            result = 'data unavailable'
        return result

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            d = {k: v for (k,v) in attrs}
            k = 'title'
            if (k in d) and (d[k].startswith('image ')):
                self.imagefile = d[k].split('"')[1]
                self.imagedir = os.path.splitext(self.imagefile)[0]
		try:
		    os.mkdir(self.imagedir)
		except:
		    sys.stderr.write('Cannot make directory {}.  Already exists?\n')
                #sys.exit(0)
        elif tag == 'span':
            d = {k: v for (k, v) in attrs}
            k = 'class'
            if ('title' in d) and (k in d) and (d[k] == 'ocrx_word'):
                v = d['title']
                if v.startswith('bbox '):
                    t, u = v[5:].split(';')
                    positions = t.split()
                    if len(positions) == 4:
                        self.a,self.b,self.c,self.d = positions
                        self.crop = '{}x{}+{}+{}'.format(
                            int(self.c)-int(self.a),
                            int(self.d)-int(self.b),
                            self.a,
                            self.b,
                        )
                        self.id = d['id']
                        self.TITLE = v
                        self.x_wconf = u.strip()
                        self.go = True

    def handle_data(self, data):
        if self:
            self.word = data
            self.csvouf.write('{}\n'.format(self))
            print('convert -crop {} {} {}/{}.tiff'.format(self.crop, self.imagefile, self.imagedir, self.id))
        self.go = False

def main(hocr_file):
    sys.stderr.write('loading {}\n'.format(hocr_file))
    with open(hocr_file, 'rt') as inf: # bad file, file not found exception suffices
        text = inf.read()
    path = os.path.dirname(os.path.abspath(hocr_file))
    csvfile = '{}.csv'.format(os.path.splitext(hocr_file)[0])
    with open(csvfile, 'wt') as csvouf:
        parser = HOCRParser(text, csvouf)

if __name__ == '__main__':

    # for the hocr file use
    # : the argument
    # :no argument
    # : the one .hocr file in the directory,
    # : or choose among the many

    if 1 < len(sys.argv):
        hocr_file = sys.argv[1]
    else:
        hocr_files = glob.glob('*.hocr')
        L = len(hocr_files)
        if not L:
            print('Use: {} path_to_hocr'.format(sys.argv[0]))
            sys.exit(1)
        if L == 1:
            index = 0
        else:
            for t in enumerate(hocr_files):
                print(t)
            sys.stderr.write('choice?  '); sys.stderr.flush()
            choice = sys.stdin.readline()
            try:
                index = clip(int(i), -L, L-1)
            except:
                index = 0
        hocr_file = hocr_files[index]
    main(hocr_file)
