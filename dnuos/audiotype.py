"""Classes for processing audio file metadata"""

import os
import re
import string
import struct

import dnuos.id3
import dnuos.path


class SpacerError(Exception):
    pass


class UnknownType(object):

    def __init__(self, file_):

        self.filename = file_
        self.filesize = dnuos.path.getsize(self.filename)
        self.filetype = os.path.splitext(self.filename)[1][1:].lower()
        self.vendor = ''
        self.version = ''
        self.brtype = ''
        self.time = 0

    def bitrate(self):

        return 0

    def artist(self):

        return {'': None}

    def album(self):

        return {'': None}

    def year(self):

        return {'': None}

    def profile(self):

        return {}


class AudioType(UnknownType):
    """Base audio file type"""

    def __init__(self, file_):

        self.filename = file_
        self._f = dnuos.path.open(self.filename, 'rb')
        self._begin = None
        self._end = None
        self._meta = []
        self.filesize = dnuos.path.getsize(self.filename)
        self.vendor = ''
        self.version = ''
        self.time = 9

    def bitrate(self):

        return int(self.streamsize() * 8.0 / self.time)

    def streamsize(self):

        return self.stream_end() - self.stream_begin()

    def stream_begin(self):

        if self._begin != None:
            return self._begin

        mark = self._f.tell()
        self._begin = 0

        # check for prepended ID3v2
        self._f.seek(0)
        if self._f.read(3) == "ID3":
            self._meta.append((0, "ID3v2"))
            data = struct.unpack("<2x5B", self._f.read(7))
            self._begin += 10 + unpack_bits(data[-4:])
            if data[0] & 0x40:
                extsize = struct.unpack("<4B", self._f.read(4))
                self._begin += unpack_bits(extsize)
            if data[0] & 0x10:
                self._begin += 10

        self._f.seek(mark)
        return self._begin

    def stream_end(self):

        if self._end != None:
            return self._end

        mark = self._f.tell()
        self._end = self.filesize

        # check for ID3v1
        self._f.seek(-128, 2)
        if self._f.read(3) == "TAG":
            self._end -= 128
            self._meta.append((self._end, "ID3v1"))

        # check for appended ID3v2
        self._f.seek(self._end - 10)
        if self._f.read(3) == "3DI":
            data = struct.unpack("<2x5B", self._f.read(7))
            self._end -= 20 + unpack_bits(data[-4:])
            if data[0] & 0x40:
                extsize = struct.unpack("<4B", self._f.read(4))
                self._end -= unpack_bits(extsize)
                self._meta.append((self._end, "ID3v2"))

        self._f.seek(mark)
        return self._end


class Ogg(AudioType):

    filetype = "Ogg"

    def __init__(self, file_):

        AudioType.__init__(self, file_)

        self.header = self.getheader()
        self.version = self.header[1]
        self.channels = self.header[2]
        self.freq = self.header[3]
        self.maxbitrate = self.header[4]
        self.nombitrate = self.header[5]
        self.minbitrate = self.header[6]
        self._artist = None
        self._album = None
        self._year = None

        self.comment = self.getcomment()
        for i in self.comment:
            field, value = i.split('=', 1)
            field = field.lower()
            if field == "artist":
                self._artist = value
            elif field == "album":
                self._album = value
            elif field == "date":
                self._year = value

        self.audiosamples = self.lastgranule()[-1]
        self.time = float(self.audiosamples) / self.freq
        self.brtype = "V"

    def artist(self):

        return {'vorbis': self._artist}

    def album(self):

        return {'vorbis': self._album}

    def year(self):

        return {'vorbis': self._year}

    def getheader(self):

        # Setup header and sync stuff
        syncpattern = '\x01vorbis'
        overlap = len(syncpattern) - 1
        headerformat = '<x6sIBI3iB'
        headersize = struct.calcsize(headerformat)

        # Read first chunk
        self._f.seek(0)
        start = self._f.tell()
        chunk = self._f.read(1024 + overlap)

        # Do all file if we have to
        while len(chunk) > overlap:
            # Look for sync
            sync = chunk.find(syncpattern)
            if sync != -1:
                # Read the header
                self._f.seek(start + sync)
                return struct.unpack(headerformat, self._f.read(headersize))
            # Read next chunk
            start = start + 1024
            self._f.seek(start + overlap)
            chunk = chunk[-overlap:] + self._f.read(1024)

    def getcomment(self):

        # Get Ogg comment
        syncpattern = '\x03vorbis'
        overlap = len(syncpattern) - 1
        jvlformat = "<7xI"
        jvlformatsize = struct.calcsize(jvlformat)
        llclformat = "<I"
        llclformatsize = struct.calcsize(llclformat)

        # Read first chunk
        self._f.seek(0)
        start = self._f.tell()
        chunk = self._f.read(1024 + overlap)

        # Do all file if we have to
        while len(chunk) > overlap:
            # Look for sync
            sync = chunk.find(syncpattern)
            if sync != -1:
                self._f.seek(start + sync)
                vendor_length = struct.unpack(jvlformat, self._f.read(
                                              jvlformatsize))[0]
                format = "<%ds" % vendor_length
                self.vendor = struct.unpack(format, self._f.read(
                                            struct.calcsize(format)))[0]
                listlength = struct.unpack(llclformat,
                                           self._f.read(llclformatsize))[0]
                comments = []
                for i in xrange(listlength):
                    commentlength = struct.unpack(llclformat,
                                        self._f.read(llclformatsize))[0]
                    format = "<%ds" % commentlength
                    tmpcomment = struct.unpack(format,
                                   self._f.read(struct.calcsize(format)))[0]
                    comments.append(tmpcomment)
                return comments
            # Read next chunk
            start += 1024
            self._f.seek(start + overlap)
            chunk = chunk[-overlap:] + self._f.read(1024)

    def lastgranule(self):

        # The setup header and sync stuff
        syncpattern = 'OggS'
        overlap = len(syncpattern) - 1
        headerformat = '<4s2xl'
        headersize = struct.calcsize(headerformat)

        # Read last chunk
        self._f.seek(-1024, 2)
        start = self._f.tell()
        chunk = self._f.read(1024)

        # Do all file if we have to
        while len(chunk) > overlap:
            # Look for sync
            sync = chunk.find(syncpattern)
            if sync != -1:
                # Read the header
                self._f.seek(start + sync)
                return struct.unpack(headerformat, self._f.read(headersize))

            # Read next block
            start = start - 1024
            self._f.seek(start)
            chunk = self._f.read(1024) + chunk[:overlap]

    def profile(self):

        xiph = [80001, 96001, 112001, 128003, 160003, 192003, 224003, 256006,
                320017, 499821]
        gt3 = [128005, 180003, 212003, 244003, 276006, 340017, 519821]

        if self.nombitrate in xiph:
            return {"xiph": "-q" + str(xiph.index(self.nombitrate) + 1)}
        elif self.nombitrate in gt3:
            return {"gt3": "-q" + str(gt3.index(self.nombitrate) + 4)}
        else:
            return {}


class MP3(AudioType):

    filetype = "MP3"

    brtable = (
        # MPEG 2/2.5
        (
            # Layer III
            (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0),
            # Layer II
            (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0),
            # Layer I
            (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224,
             256, 0)
        ), 
        # MPEG 1
        (
            # Layer III
            (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256,
             320, 0),
            # Layer II
            (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320,
             384, 0),
            # Layer I
            (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384,
             416, 448, 0)
        )
    )

    fqtable = ((32000, 16000,  8000), # MPEG 2.5
               (    0,     0,     0), # Reserved
               (22050, 24000, 16000), # MPEG 2  
               (44100, 48000, 32000)) # MPEG 1  

    def __init__(self, file_):

        AudioType.__init__(self, file_)

        self.mp3header = self.getheader(self.stream_begin())
        self.brtype = "CV"[self.mp3header[1] in ('Xing', 'VBRI')]
        self.framesync = (self.mp3header[0] >> 21 & 2047)
        self.versionindex = (self.mp3header[0] >> 19 & 3)
        self.layerindex = (self.mp3header[0] >> 17 & 3)
        self.protectionbit = (self.mp3header[0] >> 16 & 1)
        bitrateindex = (self.mp3header[0] >> 12 & 15)
        frequencyindex = (self.mp3header[0] >> 10 & 3)
        self.paddingbit = (self.mp3header[0] >> 9 & 1)
        self.privatebit = (self.mp3header[0] >> 8 & 1)
        self.modeindex = (self.mp3header[0] >> 6 & 3)
        self.modeextindex = (self.mp3header[0] >> 4 & 3)
        self.copyrightbit = (self.mp3header[0] >> 3 & 1)
        self.originalbit = (self.mp3header[0] >> 2 & 1)
        self.emphasisindex = (self.mp3header[0] & 3)
        self.framesize = self.mp3header[4]
        self.vendor = self.mp3header[6]
        if self.vendor == 'UUUUUUUUU':
            self.vendor = ''
        else:
            for char in self.vendor:
                if char not in string.printable:
                    self.vendor = ''
                    break
        self.freq =  self.fqtable[self.versionindex][frequencyindex]
        self.channels = (2, 2, 2, 1)[self.modeindex]

        if self.brtype == "V":
            if self.framesize <= 0:
                self.framesize = AudioType.streamsize(self)
            self.framecount = self.mp3header[3] + 1
            self._bitrate = int(1000.0 * self.framesize * self.freq /
                                float(self.modificator() * self.framecount))
        else:
            self._bitrate = int(1000.0 * self.brtable[self.versionindex &
                                1][self.layerindex-1][bitrateindex])
            self.framecount = int(self.streamsize() * self.freq /
                                  float(self.modificator() * self._bitrate)
                                  * 1000)
        self.time = self.streamsize() * 8.0 / self._bitrate

        try:
            self.id3v1 = dnuos.id3.ID3v1(self._f)
        except dnuos.id3.Error:
            self.id3v1 = None

        try:
            self.id3v2 = dnuos.id3.ID3v2(self._f)
        except dnuos.id3.Error:
            self.id3v2 = None

    def artist(self):

        res = {'id3v1': None, 'id3v2': None}
        if self.id3v1 and self.id3v1.artist:
            res['id3v1'] = self.id3v1.artist
        if self.id3v2:
            for frame in self.id3v2.frames:
                if frame.id == 'TPE1':
                    res['id3v2'] = frame.value
        return res

    def album(self):

        res = {'id3v1': None, 'id3v2': None}
        if self.id3v1 and self.id3v1.album:
            res['id3v1'] = self.id3v1.album
        if self.id3v2:
            for frame in self.id3v2.frames:
                if frame.id == 'TALB':
                    res['id3v2'] = frame.value
        return res

    def year(self):

        res = {'id3v1': None, 'id3v2': None}
        if self.id3v1 and self.id3v1.year:
            res['id3v1'] = self.id3v1.year
        if self.id3v2:
            for frame in self.id3v2.frames:
                if frame.id in ('TYER', 'TDRC') and hasattr(frame, 'value'):
                    res['id3v2'] = frame.value
        return res

    def streamsize(self):

        if self.brtype == "V":
            return self.framesize
        else:
            return AudioType.streamsize(self)

    _search_sync = re.compile('\xff[\xe0-\xff]').search
    _search_info = re.compile('(Xing|Info|VBRI)').search

    def getheader(self, offset=0):

        _search_sync = self._search_sync
        _search_info = self._search_info

        # Setup header and sync stuff
        overlap = 1
        # frame header + presumed padding + xing/info header (oh god)
        pattern1 = '>l32x4s3l100xL9s2B8x2B5xH'
        # xing/info header
        pattern2 = '>4s3l100xL9s2B8x2B5xH' # 5xH adds preset info
        # vbri header
        pattern3 = '>4s6x2l'
        pattern1size = struct.calcsize(pattern1)
        pattern2size = struct.calcsize(pattern2)
        pattern3size = struct.calcsize(pattern3)

        # Read first block
        self._f.seek(offset)
        start = self._f.tell()
        chunk = self._f.read(1024 + overlap)

        # Do all file if we have to
        while len(chunk) > overlap:
            # Look for sync
            sync = _search_sync(chunk)
            while sync:
                # Read header
                self._f.seek(start + sync.start())
                header = struct.unpack(pattern1, self._f.read(pattern1size))
                if self.valid(header[0]):
                    info = _search_info(chunk)
                    while info:
                        self._f.seek(start + info.start())
                        if info.group() == 'VBRI':
                            data = struct.unpack(pattern3,
                                    self._f.read(pattern3size))
                            return (header[0], data[0], None, data[2],
                                    data[1], None, 'Fraunhofer')
                        return (header[0],) + struct.unpack(pattern2,
                                                self._f.read(pattern2size))
                    return header

                # How about next sync in this block?
                sync = _search_sync(chunk, sync.start() + 1)

            # Read next chunk
            start = start + 1024
            self._f.seek(start + overlap)
            chunk = chunk[-overlap:] + self._f.read(1024)
        if offset >= self.filesize - 2:
            raise SpacerError("Spacer found %s" % self._f.name)
        self._f.seek(offset)
        tag = struct.unpack(">3s", self._f.read(struct.calcsize(">3s")))
        if tag[0] == "TAG":
            raise SpacerError("Spacer found %s" % self._f.name)

    def modificator(self):

        if self.layerindex == 3:
            return 12000
        else:
            return 144000

    def valid(self, header):

        return (((header>>21 & 2047) == 2047) and
            ((header>>19 &  3) != 1) and
            ((header>>17 &  3) != 0) and
            ((header>>12 & 15) != 0) and
            ((header>>12 & 15) != 15) and
            ((header>>10 &  3) != 3) and
            ((header     &  3) != 2))

    def profile(self):

        res = {}
        if self.mp3header[6][:4] == "LAME":
            try:
                major, minor = self.mp3header[6][4:8].split('.', 1)
                version = (int(major), int(minor))
            except ValueError:
                version = (-1, 0)
            vbrmethod = self.mp3header[7] & 15
            lowpass = self.mp3header[8]
            ath = self.mp3header[9] & 15
            preset = self.mp3header[11] & 2047

            if preset > 0:
                if preset == 320:
                    res["lame"] = "-b 320"
                elif preset in (410, 420, 430, 440, 450, 460, 470, 480, 490,
                                500):
                    if vbrmethod == 4:
                        res["lame"] = "-V%dn" % ((500 - preset) / 10)
                    else:
                        res["lame"] = "-V%d" % ((500 - preset) / 10)
                # deprecated values?
                elif preset == 1000:
                    res["lame"] = "-r3mix"
                elif preset == 1001:
                    res["lame"] = "-aps"
                elif preset == 1002:
                    res["lame"] = "-ape"
                elif preset == 1003:
                    res["lame"] = "-api"
                elif preset == 1004:
                    res["lame"] = "-apfs"
                elif preset == 1005:
                    res["lame"] = "-apfe"
                elif preset == 1006:
                    res["lame"] = "-apm"
                elif preset == 1007:
                    res["lame"] = "-apfm"
            elif version < (3, 90) and version > (0, 0):
                if vbrmethod == 8:  # unknown
                    if lowpass in (97, 98):
                        if ath == 0:
                            res["lame"] = "-r3mix"
            elif version >= (3, 90) and version < (3, 97):
                if vbrmethod == 3:  # vbr-old / vbr-rh
                    if lowpass in (195, 196):
                        if ath in (2, 4):
                            res["lame"] = "-ape"
                    elif lowpass == 190:
                        if ath == 4:
                            res["lame"] = "-aps"
                    elif lowpass == 180:
                        if ath == 4:
                            res["lame"] = "-apm"
                elif vbrmethod == 4: # vbr-mtrh
                    if lowpass in (195, 196):
                        if ath in (2, 4):
                            res["lame"] = "-apfe"
                        elif ath == 3:
                            res["lame"] = "-r3mix"
                    elif lowpass == 190:
                        if ath == 4:
                            res["lame"] = "-apfs"
                    elif lowpass == 180:
                        if ath == 4:
                            res["lame"] = "-apfm"
                elif vbrmethod in (1, 2): # abr
                    if lowpass in (205, 206):
                        if ath in (2, 4):
                            res["lame"] = "-api"
        return res

    def bitrate(self):

        return self._bitrate


class MPC(AudioType):

    filetype = "MPC"

    def __init__(self, file_):

        AudioType.__init__(self, file_)

        self.profiletable = (
            'NoProfile',
            'Unstable',
            'Unspec.',
            'Unspec.',
            'Unspec.',
            'BelowTel.',
            'BelowTel.',
            'Telephone',
            'Thumb',
            'Radio',
            'Standard',
            'Xtreme',
            'Insane',
            'Braindead',
            'AbvBrnded',
            'AbvBrnded'
        )
        fqtable = (44100, 48000, 37800, 32000)
        self.freq = fqtable[self.getheader()[3]>>16 & 4]
        self.framecount = self.getheader()[2]
        self._bitrate = int(self.streamsize() * 144000.0 /
                            float(self.framecount * self.freq))
        self.time = (float(self.framecount) * 1.150 /
                     float(44.1) + float(0.5))
        self.brtype = "V"
        self.channels = "2"

        try:
            self.id3v1 = dnuos.id3.ID3v1(self._f)
        except dnuos.id3.Error:
            self.id3v1 = None

        try:
            self.id3v2 = dnuos.id3.ID3v2(self._f)
        except dnuos.id3.Error:
            self.id3v2 = None

    def artist(self):

        res = {}
        if self.id3v1 and self.id3v1.artist:
            res['id3v1'] = self.id3v1.artist
        if self.id3v2:
            for frame in self.id3v2.frames:
                if frame.id == 'TPE1':
                    res['id3v2'] = frame.value
        return res

    def album(self):

        res = {}
        if self.id3v1 and self.id3v1.album:
            res['id3v1'] = self.id3v1.album
        if self.id3v2:
            for frame in self.id3v2.frames:
                if frame.id == 'TALB':
                    res['id3v2'] = frame.value
        return res

    _search_header = re.compile('MP+').search

    def headerstart(self):

        _search_header = self._search_header
        self._f.seek(0)
        for x in xrange(self.filesize / 1024):
            buf = self._f.read(1024)
            if _search_header(buf):
                return (x * 1024) + buf.find('MP+')

    def getheader(self):

        _search_header = self._search_header

        # Setup header and sync stuff
        overlap = 1
        pattern = '<3sb2i4h'
        patternsize = struct.calcsize(pattern)

        # Read first block
        self._f.seek(0)
        start = self._f.tell()
        chunk = self._f.read(1024 + overlap)

        # Do all file if we have to
        while len(chunk) > overlap:
            # Look for sync
            sync = _search_header(chunk)
            while sync:
                # Read header
                self._f.seek(start + sync.start())
                header = struct.unpack(pattern, self._f.read(patternsize))

                # Return the header if it's valid
                if header[1] == 7:
                    return header

                # How about next sync in this block?
                sync = _search_header(chunk, sync.start() + 1)

            # Read next chunk
            start = start + 1024
            self._f.seek(start + overlap)
            chunk = chunk[-overlap:] + self._f.read(1024)

    def profile(self):

        return {"musepack": self.profiletable[self.getheader()[3] >> 20 & 0xF]}

    def bitrate(self):

        return self._bitrate


class FLAC(AudioType):

    filetype = "FLAC"

    def __init__(self, file_):

        AudioType.__init__(self, file_)

        # [(sample number, byte offset, samples in frame), ...]
        self.seekpoints = []
        # vorbis comments
        self.commentvendor = None
        self.comments = []
        self._artist = None
        self._album = None
        self._year = None
        self.streaminfo = None
        # 0 minimum blocksize
        # 1 maximum blocksize
        # 2 minimum framesize
        # 3 maximum framesize
        # 4 sample rate in Hz
        # 5 number of channels
        # 6 bits per sample
        # 7 total samples in stream
        # 8 MD5 sum of unencoded audio

        self._f.seek(self.stream_begin())
        self.parse()
        self.samples = self.streaminfo[7]
        self.freq = self.streaminfo[4]
        self.time = self.samples / self.freq
        self._bitrate = self.streamsize() * 8 / self.time
        self.channels = self.streaminfo[5]
        samplebits = self.streaminfo[6]
        self.compression = self.streamsize() / (self.samples * samplebits *
            self.channels / 8)
        self.encoding = "%.1f%%" % self.compression
        self.brtype = "L"

        for pair in self.comments:
            field, value = pair.split('=', 1)
            field = field.lower()
            if field == 'artist':
                self._artist = value
            elif field == 'album':
                self._album = value
            elif field == 'date':
                self._year = value

    def artist(self):

        return {'FLAC': self._artist}

    def album(self):

        return {'FLAC': self._album}

    def year(self):

        return {'FLAC': self._year}

    def profile(self):

        return {}

    def parse(self):

        # STREAM
        if struct.unpack('>4s', self._f.read(4))[0] != 'fLaC':
            return

        last = 0
        while not last:
            # METADATA_BLOCK_HEADER
            data = struct.unpack('>I', self._f.read(4))[0]
            last = data >> 31
            type_ = data >> 24 & 0x7F
            length = data & 0x00FFFFFF

            if type_ == 0:
                # Stream Info
                data = struct.unpack('>3HI3Q', self._f.read(34))
                self.streaminfo = (
                   data[0],
                   data[1],
                   (data[2] << 8) | (data[3] >> 24),
                   data[3] & 0x00FFFFFF,
                   data[4] >> 44,
                   (data[4] >> 41 & 0x07) + 1,
                   (data[4] >> 36 & 0x1F) + 1,
                   data[4] & 0x0000000FFFFFFFFFL)
            elif type_ == 3:
                # Seektable
                for i in xrange(length / 18):
                    self.seekpoints.append(struct.unpack('<2QH',
                        self._f.read(18)))
            elif type_ == 4:
                # Vorbis Comment
                self.commentvendor, self.comments = self.read_comment_header()
            else:
                # Padding or unknown
                self._f.seek(length, 1)

    def read_length(self):

        length = struct.unpack('<I', self._f.read(4))[0]
        if length >= self.streamsize():
            raise ValueError
        return length

    def read_string(self):
        return self._f.read(self.read_length())

    def read_comment_header(self):
        lst = []
        vendor = self.read_string()
        for i in xrange(self.read_length()):
            lst.append(self.read_string())
        return vendor, lst

    def bitrate(self):

        return self._bitrate


class AAC(AudioType):

    filetype = "AAC"

    def __init__(self, file_):
        AudioType.__init__(self, file_)

        self.header = self.getheader()
        self._artist    = self.header[0]
        self._album = self.header[1]
        self._year = self.header[2]
        self.time   = self.header[3]
        self.freq = self.header[4]
        self.channels  = self.header[5]
        self._bitrate   = self.header[6]
        self.brtype = "C"

    def artist(self):

        return {'AAC': self._artist}

    def album(self):

        return {'AAC': self._album}

    def year(self):

        return {'AAC': self._year}

    def profile(self):

        return {}

    def getheader(self):

        self._f.seek(0)

        start = self._f.tell()
        overlap = 4
        chunk = self._f.read(1024 + overlap)

        length_found = False
        stsd_found = False
        artist_found = False
        album_found = False
        year_found = False
        bitrate_found = False

        cfl_fmt = ">I"
        cfl_fmt_size = struct.calcsize(cfl_fmt)

        # this stops things from blowing up if none are found
        artist = None
        album = None
        year = None
        bitrate = 0.0

        while len(chunk) > overlap:
            # Get tracklength info from mvhd atom
            if not length_found:
                sync = chunk.find("mdhd")
                if sync != -1:
                    sync -= 4
                    length_found = True
                    self._f.seek(start + sync + 8)
                    if self._f.read(1) == "\x00":
                        sync += 20
                        format = ">2I"
                    else:
                        sync += 28
                        format = ">IQ"
                    self._f.seek(start + sync)
                    unit, length = struct.unpack(format, self._f.read(
                        struct.calcsize(format)))
                    time = float(length) / unit
            # Get frequency and channel info from stsd atom
            if not stsd_found:
                sync = chunk.find("stsd")
                if sync != -1:
                    stsd_found = True
                    self._f.seek(start + sync + 4 + 30)
                    channels = struct.unpack(cfl_fmt, self._f.read(
                        cfl_fmt_size))[0]
                    self._f.seek(start + sync + 4 + 38)
                    frequency = struct.unpack(cfl_fmt, self._f.read(
                        cfl_fmt_size))[0]
            # Get artist info from (c)ART atom
            if not artist_found:
                sync = chunk.find('\xa9ART')
                if sync != -1:
                    artist_found = True
                    # Go back & read size of artist atom
                    self._f.seek(start + sync - 4)
                    length = struct.unpack(cfl_fmt, self._f.read(
                        cfl_fmt_size))
                    # Now we can get artist info, but first skip over junk bytes
                    self._f.seek(start + sync + 20)
                    format = "<%ds" % (length[0] - 24)
                    artist = struct.unpack(format, self._f.read(
                        struct.calcsize(format)))[0]
            # Get album info from (c)album atom
            if not album_found:
                sync = chunk.find('\xa9alb')
                if sync != -1:
                    album_found = True
                    # Go back and read size of ablum atom
                    self._f.seek(start + sync - 4)
                    length = struct.unpack(cfl_fmt, self._f.read(
                        cfl_fmt_size))
                    # get artist info, but skip over junk bytes
                    self._f.seek( start + sync + 20 )
                    format = "<%ds" % (length[0] - 24)
                    album = struct.unpack(format, self._f.read(
                        struct.calcsize(format)))[0]
             # Get year info from (c)day atom
            if not year_found:
                sync = chunk.find('\xa9day')
                if sync != -1:
                    year_found = True
                    # Go back and read size of day atom
                    self._f.seek(start + sync - 4)
                    length = struct.unpack(cfl_fmt, self._f.read(
                        cfl_fmt_size))
                    # get year info, but skip over junk bytes
                    self._f.seek( start + sync + 20 )
                    format = "<%ds" % (length[0] - 24)
                    year = struct.unpack(format, self._f.read(
                        struct.calcsize(format)))[0]
            if not bitrate_found:
                sync = chunk.find("esds")
                if sync != -1:
                    sync += 9
                    self._f.seek(start + sync)
                    if self._f.read(3) == "\x80\x80\x80":
                        sync += 3
                    sync += 4
                    self._f.seek(start + sync)
                    if self._f.read(1) == "\x04":
                        sync += 1
                        self._f.seek(start + sync)
                        if self._f.read(3) == "\x80\x80\x80":
                            sync += 3
                        sync += 10
                        self._f.seek(start + sync)
                        bitrate = struct.unpack(">I", self._f.read(
                            struct.calcsize(">I")))[0]
                        if bitrate > 0:
                            bitrate = bitrate / 1000 * 1000
                        bitrate = float(bitrate)
                        bitrate_found = True
            if (length_found and stsd_found and artist_found and album_found
                and year_found and bitrate_found):
                break

            start += 1024
            self._f.seek(start + overlap)
            chunk = chunk[-overlap:] + self._f.read(1024)

        return (artist, album, year, time, frequency, channels, bitrate)

    def bitrate(self):

        return self._bitrate


def unpack_bits(bits):
    """Unpack ID3's syncsafe 7bit number format."""

    value = 0
    for chunk in bits:
        value = value << 7
        value = value | chunk
    return value


def openstream(filename):
    """Factory function that creates an instance of the appropriate class for
    given audio file name.
    """

    lowername = filename.lower()
    if lowername.endswith(".mp3"):
        return MP3(filename)
    elif lowername.endswith(".mpc") or lowername.endswith('.mp+'):
        return MPC(filename)
    elif lowername.endswith(".ogg"):
        return Ogg(filename)
    elif (lowername.endswith(".flac") or lowername.endswith('.fla') or
          lowername.endswith('.flc')):
        return FLAC(filename)
    elif lowername.endswith(".m4a"):
        return AAC(filename)
    else:
        return UnknownType(filename)
