from abandi import version, downloader, path
from abandi.cli import call
from yapsy.IPlugin import IPlugin
import logging


KYRA_DAT_URL = "https://scummvm.svn.sourceforge.net/svnroot/scummvm/scummvm/tags/release-0-13-0/dists/engine-data/kyra.dat"
KYRA_DAT = "kyra.dat"
LURE_DAT_URL = "https://scummvm.svn.sourceforge.net/svnroot/scummvm/scummvm/tags/release-0-13-0/dists/engine-data/lure.dat"
LURE_DAT = "lure.dat"
SKY_CPT = "sky.cpt"
SKY_CPT_URL = "https://scummvm.svn.sourceforge.net/svnroot/scummvm/scummvm/tags/release-0-13-0/dists/engine-data/sky.cpt"

class scummvm(IPlugin):
    hook = 'runner'

    long_name = 'scummvm'
    extensions = []
    platforms = ['dos', 'c64']
    ubuntu_package = 'scummvm'

    def __init__(self):
        self.gameMap = None

    def run_game(self, game):
        game.scummvm_id = self.scummvm_id(game)
        self.downloadSupportFiles(game)
        self.do_copy(game)
        (stdout, stderr) = call('scummvm -p %s %s' % (game.dir, game.scummvm_id))

    def version(self):
        (stdout, stderr) = call('scummvm -v')
        return version.extract_version(stdout)

    def do_copy(self, game):
        dir = path.path(game.dir)
        def copyls(src, trg):
            files=dir.files(src.upper())+dir.files(src.lower())
            files.sort()
            for i in [1,2]:
                t = dir / (trg % (i))
                if not t.exists():
                    for s in files:
                        if str(i) in s:
                            s.copy(t)
                            break

        if game.scummvm_id == "maniac":
            # http: # wiki.scummvm.org / index.php / Datafiles
            #
            # Maniac Mansion (Original or Enhanced)
            # Apple II
            # * Rename disk image 1 to maniac1.dsk.
            # * Rename disk image 2 to maniac2.dsk.
            # Commodore 64
            # * Rename disk image 1 to maniac1.d64.
            # * Rename disk image 2 to maniac2.d64.
            copyls("*.dsk", 'maniac%d.dsk')
            copyls("*.d64", 'maniac%d.d64')

        if game.scummvm_id == "zak":
            # Zak McKracken and the Alien Mindbenders
            # Commodore 64
            # * Rename disk image 1 to zak1.d64.
            # * Rename disk image 2 to zak2.d64.
            copyls("*.d64", 'zak%d.d64')


    def extractGameMap(self, sysout):
        lines = sysout.splitlines()

        map = dict()
        start = 0
        for line in lines:
            ls = line.partition(' ')
            if "---" in ls[0]:
                start = 1
            elif start:
                map[ls[2].strip()] = ls[0].strip()
        return map


    def getGameListInt(self):
        if not self.gameMap:
            (stdout, stderr) = call('scummvm --list-games')
            self.gameMap = self.extractGameMap(stdout)
        return self.gameMap

    def findInList(self, name, gmap):
        sdict = dict([(self.simplifyText(x), x) for x in gmap.keys()])
        skeys = sdict.keys()
        sname = self.simplifyText(name)
        ls = []
        if not len(ls):        
            for k in skeys:
                if sname == k:
                    ls.append(k)
#        if not len(ls):        
#            for k in skeys:
#                if sname in k:
#                    ls.append(k)
        if not len(ls):        
            for k in skeys:
                if k in sname:
                    ls.append(k)
        if not len(ls):        
            for k in skeys:
                code = gmap[sdict[k]]
                nr = None
                if  code.endswith('1'):
                    nr = '1'
                if  code.endswith('2'):
                    nr = '2'
                if  code.endswith('3'):
                    nr = '3'
                if nr and nr in sname:
                    nsname = sname.replace(nr, '', 1)
                    nk = k.replace(nr, '', 1)
                    if nsname in nk:
                        ls.append(k)
                    
        ls.sort(key=len)
        if len(ls):        
            return sdict[ls[0]]

    def scummvm_id(self, game):
        goblins = "gobliiins,gobliins,goblins".split(",")
        code = None
        name = game.name.lower()
        for g in goblins:
            if g in name:
                code = "gob"

        if not code:
            if 'kyrandia' in name:
                if 'hand' in name:
                    code = "kyra2"
                elif 'malcolm' in name:
                    code = "kyra3"
                else:
                    code = "kyra1"
                  
        if not code:
            # String search = simplifyText(name)
            gameListMap = self.getGameListInt()
            key = self.findInList(name, gameListMap)
            assert key, 'scummvm code not found for:' + name
            code = gameListMap[key]
        logging.debug('scummvm_id:' + code)
        return code


    def simplifyText(self, txt):
        ignored_words = 'the of s a and 1 2 3 i ii iii'.split()
        txt = txt.lower()
        txt = ''.join(map(lambda x : x if x.isalnum() else ' ', txt))
        
        words = txt.split()
        words = filter(lambda x: x not in ignored_words, words)
        
        txt = ' '.join(words)
        return txt


    def downloadSupportFiles(self, game):
        code = game.scummvm_id
        url = ''
        file = ''
        if code == "sky":
            url = SKY_CPT_URL
            file = SKY_CPT
        elif code == "lure":
            url = LURE_DAT_URL
            file = LURE_DAT
        elif code == "kyra1":
            url = KYRA_DAT_URL
            file = KYRA_DAT

        if url:
            downloader.Downloader().download(url, game.dir, fileName=file)
