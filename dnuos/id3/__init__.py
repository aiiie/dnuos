# @(#) $Id: __init__.py,v 1.5 2004/03/02 05:26:07 myers_carpenter Exp $
__revision__ = "$Revision: 1.5 $"

import re, struct
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import string

from dnuos.id3 import ID3v2Frames
from dnuos.id3 import binfuncs

DEBUG_LEVEL = 0

__version__ = '0.5.5'

class Error(RuntimeError):
    """
    Exception raised for all parse errors.
    """
    pass

class NoTagError(Error):
    """
    No tag found in the file
    """
    pass

class BrokenFrameError(Error):
    """
    Tag has a broken frame
    """
    pass

class ID3v2(object):
    """
    ID3v2 parsing/writing class
    """
    def __init__(self, fh=None, broken_frames='error', internal_checks = False):
        self.fh = None
        self.internal_checks = internal_checks
        self.version = (2,3,0,)

        self.tag_size = None
        self.broken_frames = broken_frames

        self.padding_size = 0

        self._unsync = False
        self._set_data_length = False
        self.extended_header = False
        self.experimental = False
        self.footer = False

        self.frames = []

        if fh:
            self.load(fh)

    def set_unsync(self, value):
        # need to do this so that silly tags that are read in can
        # be written out exactly as they were.
        if self.version[1] >= 4:
            self._set_data_length = True
        self._unsync = value
    def get_unsync(self):
        return self._unsync
    unsync = property(get_unsync, set_unsync)


    def get_text_frame(self, frameid, create=True):
        """
        Get the copy of the right frame object or make a new one to
        fit the bill
        """

        try:
            frametype = ID3v2Frames.frameTypes[self.version[1]][frameid][1]
            if frametype != ID3v2Frames.TextInfo:
                raise Error, "%r is not a TextInfo frame type" % (frameid,)
        except KeyError:
            raise Error, "%r is not a TextInfo frame type" % (frameid,)

        for frame in self.frames:
            if frame.id == frameid:
                return frame

        if create:
            return self.new_frame(frameid)
        else:
            return None

    def get_usertext_frame(self, description, create=True):
        """
        Get the copy of the right frame object or make a new one to
        fit the bill
        """

        for frame in self.frames:
            if frame.id == 'TXXX' and frame.description == description:
                return frame

        if create:
            ret = self.new_frame('TXXX')
            ret.description = description
            return ret
        else:
            return None

    def get_apic_frame(self, description, create=True):
        """
        Get the copy of the right frame object or make a new one to
        fit the bill
        """

        for frame in self.frames:
            if frame.id == 'APIC' and frame.description == description:
                return frame

        if create:
            ret = self.new_frame('APIC')
            ret.description = description
            return ret

        return None

    def get_ufid_frame(self, owner, create=True):
        """
        Get the copy of the right frame object or make a new one to
        fit the bill
        """

        for frame in self.frames:
            if frame.id == 'UFID' and frame.owner == owner:
                return frame

        if create:
            ret = self.new_frame('UFID')
            ret.owner = owner
            return ret
        else:
            return None


    def new_frame(self, frameid, data = None):
        try:
            frame_info = ID3v2Frames.frameTypes[self.version[1]][frameid]
            newframe = frame_info[1](frameid, self.version, data)
        except KeyError, err:
#           warnings.warn("Unknown frame type %r in file %r" % (frameid, self.filename,))
            newframe = ID3v2Frames.UnknownFrame(frameid, self.version, data)

        self.frames.append(newframe)
        return newframe

    _match_frame = re.compile(r'[A-Z0-9]{4}').match

    def load(self, fh):
        """
        Load a file and extract ID3v2 data
        """
        _match_frame = self._match_frame
        self.fh = fh
        fh.seek(0)
        if fh.read(3) != 'ID3':
            return

        verinfo = fh.read(2)
        self.version = (2,ord(verinfo[0]),ord(verinfo[1]),)
        if(self.version[1] < 3):
            raise Error, "Cannot process tags with version less than 2.3.0 (This tag's version is 2.%s.%s)" % (self.version[1],self.version[2],)
        if(self.version[1] > 4) or (self.version[2] > 0):
            raise Error, "Cannot process tags with version greater than 2.4.0 (This tag's version is 2.%s.%s)" % (self.version[1], self.version[2],)

        tag_flags = binfuncs.byte2bin(fh.read(1), 8)

        self._unsync = tag_flags[0]
        self.extended_header = tag_flags[1]
        self.experimental = tag_flags[2]
        self.footer = tag_flags[3]
        assert tag_flags[4] == 0
        assert tag_flags[5] == 0
        assert tag_flags[6] == 0
        assert tag_flags[7] == 0

        if self.extended_header:
            raise Error("Don't know what to do with an extended header")

        self.tag_size = binfuncs.synchsafe2dec(fh.read(4))
        if DEBUG_LEVEL >= 1:
            print "tag version: %d.%d.%d" % self.version
            print "tag size:", self.tag_size
            print "unsync:", self.unsync

        if self.version[1] == 3 and self.unsync:
            # print self.tag_size
            tag = fh.read(self.tag_size)
            tag = binfuncs.deunsynchstr(tag)
            self.tag_size = len(tag)
            fh = StringIO.StringIO(tag)

        sizeleft = self.tag_size

        # 11 == frame header + 1 byte frame, smallest legal frame
        while sizeleft >= 11:
            frameid = fh.read(4)
            if _match_frame(frameid) or ID3v2Frames.frameTypes[self.version[1]].has_key(frameid):
                rawframesize = fh.read(4)
                if self.version[1] >= 4 and frameid != 'COM ':
                    framesize = binfuncs.synchsafe2dec(rawframesize)
                    (framesize23,) = struct.unpack('!I', rawframesize)
#                    print "2.4: %d vs 2.3: %d" % (framesize, framesize23,)
                else:
                    (framesize,) = struct.unpack('!I', rawframesize)



                if framesize > sizeleft + 2:
                    if self.broken_frames == 'drop':
#                       warnings.warn("Broken frame size in %r. Dropping rest of tag." % self.filename)
                        self.padding_size = sizeleft
                        sizeleft = 0
                        break
                    else:
                        raise BrokenFrameError("Invalid frame size %r (raw: %r).  Frame type was %r. Corrupt tag." % (framesize,rawframesize,frameid,))
                data = fh.read(framesize + 2)
                if DEBUG_LEVEL >= 2:
                    print "Raw frame: %r" % (data,)
            elif frameid == '\x00\x00\x00\x00' or frameid == 'MP3e':
                # MP3ext http://www.mutschler.de/mp3ext/ puts "MP3ext " over and over in the padding
                sizeleft -= 4
                break
            else:
                try:
                    lastframeid = self.frames[-1].id
                except IndexError:
                    lastframeid = None

                raise Error("Found garbage where I expected a Frame Id %r. Last frame was %r" % (frameid, lastframeid,))

            try:
                self.new_frame(frameid, data)
            except BrokenFrameError, err:
                if self.broken_frames == 'drop':
#                   warnings.warn("Broken frame in %r. Dropping frame." % self.filename)
                    pass
                else:
                    raise
            sizeleft -= (framesize + 2 + 4 + 4)

        if sizeleft:
            # TODO: perhaps detect mp3 frames?  that would be nice to know.
            data = fh.read(sizeleft)
#           if frameid != 'MP3e' and data != '\x00' * sizeleft:
#               warnings.warn("Not all padding is NULLed out in %r.  Perhaps this tag was written by buggy software, or I didn't parsed it correctly. padding = %r" % (self.filename, frameid + data,))
            self.padding_size = sizeleft


class ID3v1(object):
    """
    ID3v1 parsing/writing class
    """
    def __init__(self, fh=None, error_if_no_tag = False):
        self.fh = None
        self.title = ''
        self.artist = ''
        self.album = ''
        self.year = ''
        self.comment = ''
        self.genre = 0
        self.genre_str = ''
        self.track = None
        self.error_if_no_tag = error_if_no_tag
        if fh:
            self.load(fh)

    def load(self, fh):
        """
        Load a file and extract ID3v1 data

        """
        strip = string.whitespace + '\x00'
        self.fh = fh
        fh.seek(0, 2)
        if fh.tell() < 127:
            if self.error_if_no_tag:
                raise NoTagError
            return
        fh.seek(-128, 2)
        id3tag = fh.read(128)
        if id3tag[0:3] != 'TAG':
            if self.error_if_no_tag:
                raise NoTagError
            return
        self.title = id3tag[3:33].strip(strip)
        self.artist = id3tag[33:63].strip(strip)
        self.album = id3tag[63:93].strip(strip)
        self.year = id3tag[93:97].strip(strip)
        self.comment = id3tag[97:127].strip(strip)
        self.genre = ord(id3tag[127:128])
        try:
            self.genre_str = "%s (%d)" % (genres[self.genre], self.genre,)
        except IndexError:
            self.genre_str = "unknown (%d)" % self.genre
        if self.comment[28:29] == '\x00':
            self.track = ord(self.comment[29:30])
            self.comment = self.comment[0:28].strip(strip)
        else:
            self.track = None

genres = (
    'Blues',
    'Classic Rock',
    'Country',
    'Dance',
    'Disco',
    'Funk',
    'Grunge',
    'Hip - Hop',
    'Jazz',
    'Metal',
    'New Age',
    'Oldies',
    'Other',
    'Pop',
    'R&B',
    'Rap',
    'Reggae',
    'Rock',
    'Techno',
    'Industrial',
    'Alternative',
    'Ska',
    'Death Metal',
    'Pranks',
    'Soundtrack',
    'Euro - Techno',
    'Ambient',
    'Trip - Hop',
    'Vocal',
    'Jazz + Funk',
    'Fusion',
    'Trance',
    'Classical',
    'Instrumental',
    'Acid',
    'House',
    'Game',
    'Sound Clip',
    'Gospel',
    'Noise',
    'Alt Rock',
    'Bass',
    'Soul',
    'Punk',
    'Space',
    'Meditative',
    'Instrumental Pop',
    'Instrumental Rock',
    'Ethnic',
    'Gothic',
    'Darkwave',
    'Techno - Industrial',
    'Electronic',
    'Pop - Folk',
    'Eurodance',
    'Dream',
    'Southern Rock',
    'Comedy',
    'Cult',
    'Gangsta Rap',
    'Top 40',
    'Christian Rap',
    'Pop / Funk',
    'Jungle',
    'Native American',
    'Cabaret',
    'New Wave',
    'Psychedelic',
    'Rave',
    'Showtunes',
    'Trailer',
    'Lo - Fi',
    'Tribal',
    'Acid Punk',
    'Acid Jazz',
    'Polka',
    'Retro',
    'Musical',
    'Rock & Roll',
    'Hard Rock',
    'Folk',
    'Folk / Rock',
    'National Folk',
    'Swing',
    'Fast - Fusion',
    'Bebob',
    'Latin',
    'Revival',
    'Celtic',
    'Bluegrass',
    'Avantgarde',
    'Gothic Rock',
    'Progressive Rock',
    'Psychedelic Rock',
    'Symphonic Rock',
    'Slow Rock',
    'Big Band',
    'Chorus',
    'Easy Listening',
    'Acoustic',
    'Humour',
    'Speech',
    'Chanson',
    'Opera',
    'Chamber Music',
    'Sonata',
    'Symphony',
    'Booty Bass',
    'Primus',
    'Porn Groove',
    'Satire',
    'Slow Jam',
    'Club',
    'Tango',
    'Samba',
    'Folklore',
    'Ballad',
    'Power Ballad',
    'Rhythmic Soul',
    'Freestyle',
    'Duet',
    'Punk Rock',
    'Drum Solo',
    'A Cappella',
    'Euro - House',
    'Dance Hall',
    'Goa',
    'Drum & Bass',
    'Club - House',
    'Hardcore',
    'Terror',
    'Indie',
    'BritPop',
    'Negerpunk',
    'Polsk Punk',
    'Beat',
    'Christian Gangsta Rap',
    'Heavy Metal',
    'Black Metal',
    'Crossover',
    'Contemporary Christian',
    'Christian Rock',
    'Merengue',
    'Salsa',
    'Thrash Metal',
    'Anime',
    'JPop',
    'Synthpop',
)
